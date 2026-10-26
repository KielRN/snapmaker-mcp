"""Machine/action codes can veto idle, never attest physical completion."""

from uuid import uuid4

import httpx
import pytest
from test_uploads import prepared

from snapmaker_u1_mcp.adapter import U1Reader
from snapmaker_u1_mcp.models import RuntimeEvidence
from snapmaker_u1_mcp.runtime import normalize_runtime
from snapmaker_u1_mcp.transport import Moonraker
from snapmaker_u1_mcp.uploads import Coordinator, UploadInput


@pytest.mark.parametrize("field", ["main_state", "action_code"])
@pytest.mark.parametrize("bad", [None, True, False, 0.0, "IDLE", "PRIVATE STATE", [], {}, -1, 999])
def test_invalid_machine_codes_remain_unknown_private(objects, field, bad):
    objects["machine_state_manager"][field] = bad
    evidence = normalize_runtime(objects)
    assert evidence.model_dump()["machine_" + field] is None
    assert "machine_state_manager." + field in evidence.missing_fields
    assert "PRIVATE STATE" not in evidence.model_dump_json()


@pytest.mark.parametrize("field", ["main_state", "action_code"])
def test_missing_machine_codes_are_not_idle_defaults(objects, field):
    del objects["machine_state_manager"][field]
    evidence = normalize_runtime(objects)
    assert evidence.model_dump()["machine_" + field] is None
    assert "machine_state_manager." + field in evidence.missing_fields


@pytest.mark.parametrize(
    "main,action,busy,idle",
    [
        (0, 0, False, True),
        (3, 0, True, False),
        (0, 1, True, False),
        (9, None, True, False),
        (None, 576, True, False),
        (None, 0, None, None),
        (0, None, None, None),
        (True, False, None, None),
        (0, 999, None, None),
    ],
)
async def test_independent_machine_activity_vetoes_idle(setup_upload, main, action, busy, idle):
    settings, printer, file = setup_upload
    objects = printer.replies["/printer/objects/query"]["result"]["status"]
    objects["machine_state_manager"] = {"main_state": main, "action_code": action}
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with Coordinator(client) as coordinator:
            status = await coordinator.reader.status()
            assert status.data.busy is busy
            assert status.data.idle is idle
            prep = await prepared(coordinator, file)
            assert prep.outcome == ("ok" if idle is True else "rejected")
            if idle is not True:
                assert prep.errors[0].code == "printer_not_idle"
    assert printer.posts == 0


async def test_print_activity_remains_busy_with_missing_machine_provider(setup_upload):
    settings, printer, _ = setup_upload
    objects = printer.replies["/printer/objects/query"]["result"]["status"]
    del objects["machine_state_manager"]
    objects["print_stats"]["state"] = "printing"
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        status = await U1Reader(client).status()
    assert status.data.busy is True and status.data.idle is False
    assert "machine_state_manager" in status.data.missing_objects


async def test_fixed_machine_projection_in_both_queries(setup_upload):
    settings, printer, file = setup_upload
    reads = []

    async def serve(request):
        if request.url.path == "/printer/objects/query" and "gcode_move" in request.url.params:
            reads.append(dict(request.url.params))
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            assert prep.outcome == "ok"
            assert prep.data.runtime_evidence.data.machine_main_state == 0
    assert len(reads) == 2
    assert all(q.get("machine_state_manager") == "main_state,action_code" for q in reads)
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        for projection in ("", "main_state", "state_history"):
            with pytest.raises(ValueError):
                await client.get("/printer/objects/query", {"machine_state_manager": projection})


@pytest.mark.parametrize("field", ["main_state", "action_code"])
@pytest.mark.parametrize("phase", ["prepare", "preflight", "hash", "restart"])
@pytest.mark.parametrize("change", [1, None, "missing"])
async def test_machine_races_block_dispatch_or_promotion(setup_upload, field, phase, change):
    settings, printer, file = setup_upload
    objects = printer.replies["/printer/objects/query"]["result"]["status"]
    reads = 0

    def mutate():
        if change == "missing":
            objects["machine_state_manager"].pop(field, None)
        else:
            objects["machine_state_manager"][field] = change

    async def serve(request):
        nonlocal reads
        if request.url.path == "/printer/objects/query" and "gcode_move" in request.url.params:
            reads += 1
            if phase == "prepare" and reads == 2:
                mutate()
        if request.url.path.startswith("/server/files/gcodes/"):
            if phase == "preflight" or (phase == "hash" and printer.posts):
                mutate()
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            if phase == "prepare":
                assert prep.outcome == "rejected"
                assert prep.errors[0].code == (
                    "runtime_evidence_changed" if change == 1 else "runtime_evidence_missing"
                )
            else:
                assert prep.outcome == "ok"
                request = UploadInput(
                    operation_id=str(uuid4()), preparation_id=prep.data.preparation_id
                )
                if phase == "restart":
                    printer.failure = "lost_without_write"
                response = await coordinator.upload(request)
                assert response.outcome == ("rejected" if phase == "preflight" else "unknown")
                if phase == "restart":
                    mutate()
                    printer.files[response.data.remote_path] = file.read_bytes()
                    printer.failure = None
                else:
                    assert response.errors[0].code == "printer_not_idle"
        if phase == "restart":
            with Coordinator(client) as coordinator:
                response = await coordinator.upload(request)
                assert response.outcome == "unknown"
                assert response.errors[0].code == "printer_not_idle"
    assert printer.posts == int(phase in {"hash", "restart"})


def test_historical_machine_reports_deserialize_as_unknown(objects):
    old = normalize_runtime(objects).model_dump()
    for key in ("machine_main_state", "machine_action_code"):
        old.pop(key, None)
    evidence = RuntimeEvidence.model_validate(old)
    assert evidence.machine_main_state is None and evidence.machine_action_code is None
