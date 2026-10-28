"""A later evidence failure must not erase completed source observations."""

import asyncio
import json
from copy import deepcopy
from uuid import uuid4

import httpx
import pytest
from test_uploads import prepared

from snapmaker_u1_mcp.transport import Moonraker
from snapmaker_u1_mcp.uploads import Coordinator, UploadInput


@pytest.mark.parametrize("resumed_eventtime", [1500, 2000])
@pytest.mark.parametrize("verification_window", ["opening", "closing"])
@pytest.mark.parametrize(
    "failure,expected",
    [
        ("opening_busy", "printer_not_idle"),
        ("materials_timeout", "timeout"),
        ("materials_mapping", "mapping_changed"),
        ("materials_backwards", "runtime_evidence_changed"),
        ("closing_changed", "runtime_evidence_changed"),
        ("closing_missing", "runtime_evidence_missing"),
        ("closing_backwards", "runtime_evidence_changed"),
    ],
)
async def test_failed_evidence_retains_observations_after_restart(
    setup_upload, failure, expected, resumed_eventtime, verification_window
):
    settings, printer, file = setup_upload
    fail_evidence = False
    runtime_reads = 0

    async def serve(request):
        nonlocal runtime_reads
        if fail_evidence and request.url.path == "/printer/objects/query":
            material = "filament_detect" in request.url.params
            if not material:
                runtime_reads += 1
            window_reads = runtime_reads - (2 if verification_window == "closing" else 0)
            if window_reads <= 0:
                return await printer.serve(request)
            if material and failure == "materials_timeout":
                raise httpx.ReadTimeout("synthetic timeout", request=request)
            reply = deepcopy(printer.replies["/printer/objects/query"])
            result = reply["result"]
            result["eventtime"] = 1800
            if failure in {
                "opening_busy",
                "materials_timeout",
                "materials_backwards",
                "closing_backwards",
            }:
                result["eventtime"] = 2000
            if failure == "opening_busy":
                result["status"]["print_stats"]["state"] = "printing"
            if material and failure == "materials_mapping":
                result["eventtime"] = 2000
                result["status"]["print_task_config"]["extruder_map_table"][0] = 0
            if material and failure == "materials_backwards":
                result["eventtime"] = 1500
            if not material and window_reads == 2:
                result["eventtime"] = 2000
                if failure == "closing_changed":
                    result["status"]["extruder"]["extruder_offset"][0] += 0.01
                elif failure == "closing_missing":
                    del result["status"]["extruder3"]["extruder_offset"]
                elif failure == "closing_backwards":
                    result["eventtime"] = 1500
            return httpx.Response(200, stream=httpx.ByteStream(json.dumps(reply).encode()))
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            request = UploadInput(
                operation_id=str(uuid4()), preparation_id=prep.data.preparation_id
            )
            printer.failure = "lost_without_write"
            printer.replies["/printer/objects/query"]["result"]["eventtime"] = 1000
            response = await coordinator.upload(request)
            assert response.outcome == "unknown"
            printer.files[response.data.remote_path] = file.read_bytes()
            printer.failure = None
            fail_evidence = True
            response = await coordinator.upload(request)
            assert response.outcome == "unknown"
            assert response.errors[0].code == expected

        fail_evidence = False
        printer.replies["/printer/objects/query"]["result"]["eventtime"] = resumed_eventtime
        with Coordinator(client) as coordinator:
            response = await coordinator.upload(request)
            if resumed_eventtime < 2000:
                assert response.outcome == "unknown"
                assert response.errors[0].code == "runtime_evidence_changed"
            else:
                assert response.outcome == "ok"
                assert response.data.reconciled is True
            assert printer.posts == 1


@pytest.mark.parametrize("invalid_time", [None, True, "3000", float("nan"), float("inf"), -1, 1e13])
@pytest.mark.parametrize("invalid_read", ["opening", "materials", "closing"])
async def test_invalid_source_times_do_not_poison_recovery(
    setup_upload, invalid_time, invalid_read
):
    settings, printer, file = setup_upload
    invalid = False
    runtime_reads = 0

    async def serve(request):
        nonlocal runtime_reads
        if invalid and request.url.path == "/printer/objects/query":
            material = "filament_detect" in request.url.params
            if not material:
                runtime_reads += 1
            reply = deepcopy(printer.replies["/printer/objects/query"])
            reply["result"]["eventtime"] = 1800
            if (
                (invalid_read == "materials" and material)
                or (invalid_read == "opening" and not material and runtime_reads == 1)
                or (invalid_read == "closing" and not material and runtime_reads == 2)
            ):
                reply["result"]["eventtime"] = invalid_time
            return httpx.Response(200, stream=httpx.ByteStream(json.dumps(reply).encode()))
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            request = UploadInput(
                operation_id=str(uuid4()), preparation_id=prep.data.preparation_id
            )
            printer.failure = "lost_without_write"
            printer.replies["/printer/objects/query"]["result"]["eventtime"] = 1000
            response = await coordinator.upload(request)
            printer.files[response.data.remote_path] = file.read_bytes()
            printer.failure = None
            invalid = True
            assert (await coordinator.upload(request)).outcome == "unknown"

        invalid = False
        printer.replies["/printer/objects/query"]["result"]["eventtime"] = (
            1500 if invalid_read == "opening" else 1800
        )
        with Coordinator(client) as coordinator:
            assert (await coordinator.upload(request)).outcome == "ok"
            assert printer.posts == 1


@pytest.mark.parametrize("blocked_read", ["materials", "closing"])
@pytest.mark.parametrize("verification_window", ["opening", "closing"])
async def test_cancelled_evidence_retains_completed_reads(
    setup_upload, blocked_read, verification_window
):
    settings, printer, file = setup_upload
    block = False
    runtime_reads = 0
    blocked = asyncio.Event()

    async def serve(request):
        nonlocal runtime_reads
        if block and request.url.path == "/printer/objects/query":
            material = "filament_detect" in request.url.params
            if not material:
                runtime_reads += 1
            window_reads = runtime_reads - (2 if verification_window == "closing" else 0)
            if window_reads <= 0:
                return await printer.serve(request)
            if (material and blocked_read == "materials") or (
                not material and window_reads == 2 and blocked_read == "closing"
            ):
                blocked.set()
                await asyncio.Event().wait()
            reply = deepcopy(printer.replies["/printer/objects/query"])
            reply["result"]["eventtime"] = 2000 if material or blocked_read == "materials" else 1800
            return httpx.Response(200, stream=httpx.ByteStream(json.dumps(reply).encode()))
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            request = UploadInput(
                operation_id=str(uuid4()), preparation_id=prep.data.preparation_id
            )
            printer.failure = "lost_without_write"
            printer.replies["/printer/objects/query"]["result"]["eventtime"] = 1000
            response = await coordinator.upload(request)
            printer.files[response.data.remote_path] = file.read_bytes()
            printer.failure = None
            block = True
            task = asyncio.create_task(coordinator.upload(request))
            try:
                await asyncio.wait_for(blocked.wait(), timeout=5)
            finally:
                task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await task

        block = False
        printer.replies["/printer/objects/query"]["result"]["eventtime"] = 1900
        with Coordinator(client) as coordinator:
            response = await coordinator.upload(request)
            assert response.outcome == "unknown"
            assert response.errors[0].code == "runtime_evidence_changed"
            printer.replies["/printer/objects/query"]["result"]["eventtime"] = 2000
            assert (await coordinator.upload(request)).outcome == "ok"
            assert printer.posts == 1
