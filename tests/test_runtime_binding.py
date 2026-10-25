"""Snapshot drift must refuse transfer even when file/material evidence agrees."""

import json
from copy import deepcopy
from uuid import uuid4

import httpx
import pytest
from test_uploads import prepared

from snapmaker_u1_mcp.transport import Moonraker
from snapmaker_u1_mcp.uploads import Coordinator, UploadInput


async def test_preparation_records_bounded_nonatomic_runtime_window(setup_upload):
    settings, printer, file = setup_upload
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            assert prep.outcome == "ok"
            binding = prep.data.runtime_evidence
            assert binding.source_eventtime_start == 123.5
            assert binding.source_eventtime_end == 123.5
            assert binding.atomic_across_requests is False
            assert binding.observation_started_at <= binding.observed_at
            assert binding.data.tools[1].reported_offset == [-0.1, 0.2, 0.05]
            assert "synthetic-private-profile" not in prep.model_dump_json()
            assert printer.posts == 0


@pytest.mark.parametrize(
    "change", ["offset", "mesh", "profile", "mode", "origin", "position", "homed", "selection"]
)
async def test_runtime_change_invalidates_prepared_evidence(setup_upload, change):
    settings, printer, file = setup_upload
    objects = printer.replies["/printer/objects/query"]["result"]["status"]
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            assert prep.outcome == "ok"
            if change == "offset":
                objects["extruder3"]["extruder_offset"][0] += 0.01
            elif change == "mesh":
                objects["bed_mesh"]["mesh_matrix"][0][0] += 0.01
            elif change == "profile":
                objects["bed_mesh"]["profile_name"] = "changed-private-profile"
            elif change == "mode":
                objects["gcode_move"]["absolute_extrude"] = True
            elif change == "origin":
                objects["gcode_move"]["homing_origin"][0] += 0.01
            elif change == "position":
                objects["toolhead"]["position"][0] += 0.01
            elif change == "homed":
                objects["toolhead"]["homed_axes"] = ""
            else:
                objects["toolhead"]["extruder"] = "extruder"
                for name in ("extruder", "extruder1", "extruder2", "extruder3"):
                    objects[name].update(state="PARKED", real_extruder_stats=["extruder", 1])
            result = await coordinator.upload(
                UploadInput(
                    operation_id=str(uuid4()),
                    preparation_id=prep.data.preparation_id,
                )
            )
            assert result.outcome == "rejected"
            assert result.errors[0].code == "evidence_changed"
            assert printer.posts == 0


@pytest.mark.parametrize(
    "change,code",
    [
        ("missing", "runtime_evidence_missing"),
        ("index", "runtime_evidence_inconsistent"),
        ("eventtime", "runtime_evidence_missing"),
    ],
)
async def test_incomplete_runtime_blocks_new_preparation(setup_upload, change, code):
    settings, printer, file = setup_upload
    result = printer.replies["/printer/objects/query"]["result"]
    if change == "missing":
        del result["status"]["extruder3"]["extruder_offset"]
    elif change == "index":
        result["status"]["extruder3"]["extruder_index"] = 0
    else:
        result.pop("eventtime")
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with Coordinator(client) as coordinator:
            response = await prepared(coordinator, file)
            assert response.outcome == "rejected"
            assert response.errors[0].code == code
            assert printer.posts == 0


@pytest.mark.parametrize("change", ["offset", "backwards_time"])
async def test_race_between_runtime_reads_blocks_preparation(setup_upload, change):
    settings, printer, file = setup_upload
    runtime_reads = 0

    async def serve(request):
        nonlocal runtime_reads
        if request.url.path == "/printer/objects/query" and "gcode_move" in request.url.params:
            runtime_reads += 1
            if runtime_reads == 2:
                reply = deepcopy(printer.replies["/printer/objects/query"])
                if change == "offset":
                    reply["result"]["status"]["extruder"]["extruder_offset"][0] += 0.01
                else:
                    reply["result"]["eventtime"] = 100
                return httpx.Response(200, stream=httpx.ByteStream(json.dumps(reply).encode()))
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            response = await prepared(coordinator, file)
            assert response.outcome == "rejected"
            assert response.errors[0].code == "runtime_evidence_changed"
            assert printer.posts == 0


async def test_runtime_change_during_destination_preflight_blocks_post(setup_upload):
    settings, printer, file = setup_upload

    async def serve(request):
        if request.url.path.startswith("/server/files/gcodes/"):
            objects = printer.replies["/printer/objects/query"]["result"]["status"]
            objects["extruder"]["extruder_offset"][0] += 0.01
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            assert prep.outcome == "ok"
            response = await coordinator.upload(
                UploadInput(
                    operation_id=str(uuid4()),
                    preparation_id=prep.data.preparation_id,
                )
            )
            assert response.outcome == "rejected"
            assert response.errors[0].code == "evidence_changed"
            assert printer.posts == 0


async def test_backwards_source_time_between_operations_blocks_reuse(setup_upload):
    settings, printer, file = setup_upload
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            assert prep.outcome == "ok"
            printer.replies["/printer/objects/query"]["result"]["eventtime"] = 100
            response = await coordinator.upload(
                UploadInput(
                    operation_id=str(uuid4()),
                    preparation_id=prep.data.preparation_id,
                )
            )
            assert response.outcome == "rejected"
            assert response.errors[0].code == "runtime_evidence_changed"
            assert printer.posts == 0


async def test_runtime_change_during_remote_hash_read_prevents_promotion(setup_upload):
    settings, printer, file = setup_upload

    async def serve(request):
        if request.url.path.startswith("/server/files/gcodes/") and printer.posts:
            objects = printer.replies["/printer/objects/query"]["result"]["status"]
            objects["extruder"]["extruder_offset"][0] += 0.01
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            request = UploadInput(
                operation_id=str(uuid4()), preparation_id=prep.data.preparation_id
            )
            response = await coordinator.upload(request)
            assert response.outcome == "unknown"
            assert response.errors[0].code == "evidence_changed"
            assert printer.posts == 1
            assert (await coordinator.upload(request)).outcome == "unknown"
            assert printer.posts == 1


async def test_material_time_must_fall_inside_runtime_window(setup_upload):
    settings, printer, file = setup_upload

    async def serve(request):
        if request.url.path == "/printer/objects/query" and "filament_detect" in request.url.params:
            reply = deepcopy(printer.replies["/printer/objects/query"])
            reply["result"]["eventtime"] = 100
            return httpx.Response(200, stream=httpx.ByteStream(json.dumps(reply).encode()))
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            response = await prepared(coordinator, file)
            assert response.outcome == "rejected"
            assert response.errors[0].code == "runtime_evidence_changed"
            assert printer.posts == 0


async def test_reconciliation_retains_latest_source_time_watermark(setup_upload):
    settings, printer, file = setup_upload
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
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
        with Coordinator(client) as coordinator:
            printer.replies["/printer/objects/query"]["result"]["eventtime"] = 2000
            # A successful reconciliation would be terminal, so retain absence first.
            content = printer.files.pop(response.data.remote_path)
            assert (await coordinator.upload(request)).outcome == "unknown"
            printer.files[response.data.remote_path] = content
            printer.replies["/printer/objects/query"]["result"]["eventtime"] = 1500
            response = await coordinator.upload(request)
            assert response.outcome == "unknown"
            assert response.errors[0].code == "runtime_evidence_changed"
            assert printer.posts == 1


@pytest.mark.parametrize("change", ["selection", "empty_mesh"])
async def test_contradictory_runtime_reports_block_preparation(setup_upload, change):
    settings, printer, file = setup_upload
    objects = printer.replies["/printer/objects/query"]["result"]["status"]
    if change == "selection":
        for name in ("extruder", "extruder1", "extruder2", "extruder3"):
            objects[name].update(state="PARKED", real_extruder_stats=["extruder", 1])
    else:
        objects["bed_mesh"].update(profile_name="", mesh_matrix=[[]], probed_matrix=[[]])
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with Coordinator(client) as coordinator:
            response = await prepared(coordinator, file)
            assert response.outcome == "rejected"
            assert response.errors[0].code == "runtime_evidence_inconsistent"
            assert printer.posts == 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("excluded_objects", ["PRIVATE OBJECT"]),
        ("current_object", "PRIVATE OBJECT"),
        ("in_excluded_region", True),
    ],
)
@pytest.mark.parametrize("phase", ["prepare", "preflight", "hash", "restart"])
async def test_exclusion_changes_block_dispatch_or_promotion(setup_upload, field, value, phase):
    settings, printer, file = setup_upload
    objects = printer.replies["/printer/objects/query"]["result"]["status"]
    runtime_reads = 0
    queries = []

    async def serve(request):
        nonlocal runtime_reads
        if request.url.path == "/printer/objects/query" and "gcode_move" in request.url.params:
            runtime_reads += 1
            queries.append(request.url.params.get("exclude_object"))
            if phase == "prepare" and runtime_reads == 2:
                objects["exclude_object"][field] = value
        if request.url.path.startswith("/server/files/gcodes/"):
            if phase == "preflight" or (phase == "hash" and printer.posts):
                objects["exclude_object"][field] = value
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            if phase == "prepare":
                assert prep.outcome == "rejected"
                assert prep.errors[0].code == "runtime_evidence_changed"
            else:
                assert prep.outcome == "ok"
                assert prep.data.runtime_evidence.data.exclusion.current_object_present is False
                request = UploadInput(
                    operation_id=str(uuid4()), preparation_id=prep.data.preparation_id
                )
                if phase == "restart":
                    printer.failure = "lost_without_write"
                response = await coordinator.upload(request)
                assert response.outcome == ("rejected" if phase == "preflight" else "unknown")
                if phase != "restart":
                    assert response.errors[0].code == "evidence_changed"
                else:
                    objects["exclude_object"][field] = value
                    printer.files[response.data.remote_path] = file.read_bytes()
                    printer.failure = None
        if phase == "restart":
            with Coordinator(client) as coordinator:
                response = await coordinator.upload(request)
                assert response.outcome == "unknown"
                assert response.errors[0].code == "evidence_changed"
        assert printer.posts == int(phase in {"hash", "restart"})
        assert queries and set(queries) == {"excluded_objects,current_object,in_excluded_region"}


@pytest.mark.parametrize("field", ["excluded_objects", "current_object", "in_excluded_region"])
async def test_missing_exclusion_blocks_preparation(setup_upload, field):
    settings, printer, file = setup_upload
    del printer.replies["/printer/objects/query"]["result"]["status"]["exclude_object"][field]
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with Coordinator(client) as coordinator:
            response = await prepared(coordinator, file)
            assert response.outcome == "rejected"
            assert response.errors[0].code == "runtime_evidence_missing"
            assert printer.posts == 0


async def test_same_size_excluded_set_change_invalidates_receipt(setup_upload):
    settings, printer, file = setup_upload
    exclusion = printer.replies["/printer/objects/query"]["result"]["status"]["exclude_object"]
    exclusion["excluded_objects"] = ["FIRST PRIVATE OBJECT"]
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            assert prep.outcome == "ok"
            exclusion["excluded_objects"] = ["SECOND PRIVATE OBJECT"]
            response = await coordinator.upload(
                UploadInput(operation_id=str(uuid4()), preparation_id=prep.data.preparation_id)
            )
            assert response.outcome == "rejected"
            assert response.errors[0].code == "evidence_changed"
            assert printer.posts == 0
