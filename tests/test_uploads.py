import asyncio
import hashlib
import json
from uuid import uuid4

import httpx
import pytest
from test_gcode import VALID

from snapmaker_u1_mcp import uploads
from snapmaker_u1_mcp.transport import Moonraker


def json_response(status, value):
    return httpx.Response(status, stream=httpx.ByteStream(json.dumps(value).encode()))


class Printer:
    """Simulates the pinned upload envelope, byte storage, and response loss."""

    def __init__(self, replies):
        self.replies = replies
        self.files = {}
        self.posts = 0
        self.gets = 0
        self.failure = None
        self.return_path = None
        self.started = False
        self.delay = 0
        self.active_posts = 0
        self.max_active = 0

    async def serve(self, request):
        path = request.url.path
        if request.method == "POST":
            assert path == "/server/files/upload"
            self.posts += 1
            self.active_posts += 1
            self.max_active = max(self.max_active, self.active_posts)
            try:
                await asyncio.sleep(self.delay)
                # Parse the real multipart body, not an internal request helper.
                from email.parser import BytesParser
                from email.policy import default

                message = BytesParser(policy=default).parsebytes(
                    b"Content-Type: "
                    + request.headers["content-type"].encode()
                    + b"\r\nMIME-Version: 1.0\r\n\r\n"
                    + request.content
                )
                parts = {
                    p.get_param("name", header="content-disposition"): p
                    for p in message.iter_parts()
                }
                assert parts["print"].get_payload(decode=True) == b"false"
                assert parts["root"].get_payload(decode=True) == b"gcodes"
                assert parts["path"].get_payload(decode=True) == b""
                data = parts["file"].get_payload(decode=True)
                assert (
                    parts["checksum"].get_payload(decode=True).decode()
                    == hashlib.sha256(data).hexdigest()
                )
                name = parts["file"].get_filename()
                if self.failure == "error":
                    return json_response(200, {"error": {"message": "SECRET"}})
                if self.failure != "lost_without_write":
                    self.files[name] = data if self.failure != "corrupt" else data + b"; corrupt"
                if self.failure in {"lost", "lost_without_write"}:
                    raise httpx.ReadTimeout("SECRET", request=request)
                return json_response(
                    201,
                    {
                        "item": {"root": "gcodes", "path": self.return_path or name},
                        "print_started": self.started,
                        "print_queued": False,
                    },
                )
            finally:
                self.active_posts -= 1
        if path.startswith("/server/files/gcodes/"):
            self.gets += 1
            name = path.rsplit("/", 1)[-1]
            if self.failure == "download_error" and self.posts:
                return json_response(200, {"error": {"message": "SECRET"}})
            if name not in self.files:
                return httpx.Response(404)
            return httpx.Response(200, stream=httpx.ByteStream(self.files[name]))
        return httpx.Response(200, stream=httpx.ByteStream(json.dumps(self.replies[path]).encode()))


async def prepared(coordinator, file, **kwargs):
    return await coordinator.prepare(
        uploads.PrepareInput(
            operation_id=str(uuid4()),
            local_path=str(file),
            plate=1,
            logical_to_physical=[2, 1, 4, 3],
            **kwargs,
        )
    )


async def test_prepare_and_verified_upload_are_bound_and_idempotent(setup_upload):
    settings, printer, file = setup_upload
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with uploads.Coordinator(client) as coordinator:
            p = await prepared(coordinator, file)
            assert p.outcome == "ok"
            assert p.data.inspection.used_tools == [1]
            assert p.data.sha256 == hashlib.sha256(VALID).hexdigest()
            request = uploads.UploadInput(
                operation_id=str(uuid4()), preparation_id=p.data.preparation_id
            )
            result = await coordinator.upload(request)
            assert result.outcome == "ok"
            assert result.data.state == "verified"
            assert result.data.remote_sha256 == p.data.sha256
            assert printer.posts == 1
            assert (await coordinator.upload(request)) == result
            assert printer.posts == 1
            assert str(file) not in result.model_dump_json()


@pytest.mark.parametrize(
    "change,code",
    [
        ("missing", "material_not_loaded"),
        ("mapping", "mapping_changed"),
        ("identity", "evidence_changed"),
        ("file", "file_changed"),
        ("busy", "printer_not_idle"),
        ("material", "material_mismatch"),
    ],
)
async def test_fresh_evidence_blocks_mutation(setup_upload, change, code):
    settings, printer, file = setup_upload
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with uploads.Coordinator(client) as coordinator:
            p = await prepared(coordinator, file)
            status = printer.replies["/printer/objects/query"]["result"]["status"]
            if change == "missing":
                status["filament_motion_sensor e0_filament"]["filament_detected"] = False
            elif change == "mapping":
                status["print_task_config"]["extruder_map_table"][1] = 1
            elif change == "identity":
                printer.replies["/printer/info"]["result"]["hostname"] = "different"
            elif change == "file":
                file.write_bytes(VALID + b"; edited")
            elif change == "busy":
                status["print_stats"]["state"] = "printing"
            else:
                status["filament_detect"]["info"][0]["MAIN_TYPE"] = "PETG"
            result = await coordinator.upload(
                uploads.UploadInput(operation_id=str(uuid4()), preparation_id=p.data.preparation_id)
            )
            assert result.outcome == "rejected"
            assert result.errors[0].code == code
            assert printer.posts == 0


@pytest.mark.parametrize(
    "failure,code",
    [("corrupt", "hash_mismatch"), ("error", "printer_error"), ("download_error", "printer_error")],
)
async def test_no_false_upload_success(setup_upload, failure, code):
    settings, printer, file = setup_upload
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with uploads.Coordinator(client) as coordinator:
            p = await prepared(coordinator, file)
            printer.failure = failure
            request = uploads.UploadInput(
                operation_id=str(uuid4()), preparation_id=p.data.preparation_id
            )
            result = await coordinator.upload(request)
            assert result.outcome in {"rejected", "unknown"}
            assert result.errors[0].code == code
            assert "SECRET" not in result.model_dump_json()
            assert (await coordinator.upload(request)).outcome != "ok"
            assert printer.posts == 1


@pytest.mark.parametrize(
    "returned", ["../escape.gcode", "config/private", "https://evil.invalid/a", "gcodes/x.gcode"]
)
async def test_returned_path_must_be_exact_generated_destination(setup_upload, returned):
    settings, printer, file = setup_upload
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with uploads.Coordinator(client) as coordinator:
            p = await prepared(coordinator, file)
            printer.return_path = returned
            result = await coordinator.upload(
                uploads.UploadInput(operation_id=str(uuid4()), preparation_id=p.data.preparation_id)
            )
            assert result.outcome == "unknown"
            assert result.errors[0].code == "upload_contract"
            assert returned not in result.model_dump_json()


async def test_lost_reply_reconciles_after_restart_without_repost(setup_upload):
    settings, printer, file = setup_upload
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with uploads.Coordinator(client) as first:
            p = await prepared(first, file)
            request = uploads.UploadInput(
                operation_id=str(uuid4()), preparation_id=p.data.preparation_id
            )
            printer.failure = "lost_without_write"
            result = await first.upload(request)
            assert result.outcome == "unknown"
            # A late write becomes visible only after the response timed out.
            printer.files[result.data.remote_path] = VALID
        file.unlink()  # reconciliation must use persisted expected hash, not source bytes
        with uploads.Coordinator(client) as second:
            result = await second.upload(request)
            assert result.outcome == "ok"
            assert result.data.reconciled is True
            assert result.data.response_flags_confirmed is False
            assert printer.posts == 1


async def test_expiry_and_repeated_id_conflict_do_not_post(setup_upload):
    settings, printer, file = setup_upload
    clock = [1000.0]
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with uploads.Coordinator(client, clock=lambda: clock[0]) as coordinator:
            p = await prepared(coordinator, file)
            clock[0] = 1601
            request = uploads.UploadInput(
                operation_id=str(uuid4()), preparation_id=p.data.preparation_id
            )
            result = await coordinator.upload(request)
            assert result.errors[0].code == "receipt_expired"
            conflict = await coordinator.upload(
                request.model_copy(update={"preparation_id": str(uuid4())})
            )
            assert conflict.errors[0].code == "operation_conflict"
            assert printer.posts == 0


async def test_concurrent_uploads_serialize_and_one_preparation_cannot_upload_twice(setup_upload):
    settings, printer, file = setup_upload
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with uploads.Coordinator(client) as coordinator:
            p = await prepared(coordinator, file)
            printer.delay = 0.05
            results = await asyncio.gather(
                *(
                    coordinator.upload(
                        uploads.UploadInput(
                            operation_id=str(uuid4()), preparation_id=p.data.preparation_id
                        )
                    )
                    for _ in range(2)
                )
            )
            assert sum(r.outcome == "ok" for r in results) == 1
            assert printer.posts == 1
            assert printer.max_active == 1


async def test_rejected_second_claim_stays_terminal_on_repeat(setup_upload):
    settings, printer, file = setup_upload
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with uploads.Coordinator(client) as coordinator:
            p = await prepared(coordinator, file)
            await coordinator.upload(
                uploads.UploadInput(operation_id=str(uuid4()), preparation_id=p.data.preparation_id)
            )
            request = uploads.UploadInput(
                operation_id=str(uuid4()), preparation_id=p.data.preparation_id
            )
            first = await coordinator.upload(request)
            assert first.errors[0].code == "preparation_already_used"
            assert await coordinator.upload(request) == first
            assert printer.posts == 1


async def test_wrong_material_or_missing_feed_prevents_preparation(setup_upload):
    settings, printer, file = setup_upload
    printer.replies["/printer/objects/query"]["result"]["status"]["filament_feed left"][
        "extruder0"
    ]["filament_detected"] = False
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with uploads.Coordinator(client) as coordinator:
            result = await prepared(coordinator, file)
            assert result.outcome == "rejected"
            assert result.errors[0].code == "material_not_loaded"
            assert printer.posts == 0


async def test_read_unavailability_is_not_a_printer_rejection(setup_upload):
    settings, printer, file = setup_upload

    async def disconnected(request):
        raise httpx.ConnectError("SECRET", request=request)

    async with Moonraker(settings, transport=httpx.MockTransport(disconnected)) as client:
        with uploads.Coordinator(client) as coordinator:
            result = await prepared(coordinator, file)
            assert result.outcome == "unavailable"
            assert result.errors[0].code == "connection_failed"


async def test_state_race_during_preflight_blocks_post(setup_upload):
    settings, printer, file = setup_upload

    async def racing(request):
        response = await printer.serve(request)
        if request.url.path.startswith("/server/files/gcodes/") and not printer.posts:
            printer.replies["/printer/objects/query"]["result"]["status"]["print_stats"][
                "state"
            ] = "printing"
        return response

    async with Moonraker(settings, transport=httpx.MockTransport(racing)) as client:
        with uploads.Coordinator(client) as coordinator:
            p = await prepared(coordinator, file)
            result = await coordinator.upload(
                uploads.UploadInput(operation_id=str(uuid4()), preparation_id=p.data.preparation_id)
            )
            assert result.errors[0].code == "printer_not_idle"
            assert printer.posts == 0


async def test_cancellation_after_dispatch_leaves_restart_reconciliation(setup_upload):
    settings, printer, file = setup_upload
    reached = asyncio.Event()

    async def interrupted(request):
        response = await printer.serve(request)
        if request.method == "POST":
            reached.set()
            await asyncio.Event().wait()
        return response

    async with Moonraker(settings, transport=httpx.MockTransport(interrupted)) as client:
        with uploads.Coordinator(client) as first:
            p = await prepared(first, file)
            request = uploads.UploadInput(
                operation_id=str(uuid4()), preparation_id=p.data.preparation_id
            )
            task = asyncio.create_task(first.upload(request))
            await asyncio.wait_for(reached.wait(), timeout=3)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        with uploads.Coordinator(client) as second:
            result = await second.upload(request)
            assert result.outcome == "ok"
            assert result.data.reconciled
            assert printer.posts == 1


async def test_same_id_cannot_be_repurposed_after_missing_preparation(setup_upload):
    settings, printer, file = setup_upload
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with uploads.Coordinator(client) as coordinator:
            request = uploads.UploadInput(operation_id=str(uuid4()), preparation_id=str(uuid4()))
            assert (await coordinator.upload(request)).errors[0].code == "preparation_missing"
            p = await prepared(coordinator, file)
            request = request.model_copy(update={"preparation_id": p.data.preparation_id})
            assert (await coordinator.upload(request)).errors[0].code == "operation_conflict"
            assert printer.posts == 0


async def test_another_process_holding_coordinator_lock_blocks_preparation(setup_upload):
    import sys

    settings, printer, file = setup_upload
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with uploads.Coordinator(client) as coordinator:
            child = await asyncio.create_subprocess_exec(
                sys.executable,
                "-c",
                (
                    "from pathlib import Path; from snapmaker_u1_mcp.receipts import Store; "
                    "import sys; s=Store(Path(sys.argv[1])); "
                    "ctx=s.exclusive(); ctx.__enter__(); print('locked',flush=True); input()"
                ),
                str(settings.receipt_db),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                assert (await asyncio.wait_for(child.stdout.readline(), 5)).strip() == b"locked"
                result = await prepared(coordinator, file)
                assert result.outcome == "unavailable"
                assert result.errors[0].code == "coordinator_busy"
                assert printer.posts == 0
            finally:
                await asyncio.wait_for(child.communicate(b"release\n"), 5)
