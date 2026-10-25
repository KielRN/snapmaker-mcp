"""Reported nozzle/flow/queue evidence must not become physical attestation."""

from uuid import uuid4

import httpx
import pytest
from test_uploads import prepared

from snapmaker_u1_mcp.models import RuntimeEvidence
from snapmaker_u1_mcp.runtime import normalize_runtime
from snapmaker_u1_mcp.transport import Moonraker
from snapmaker_u1_mcp.uploads import Coordinator, UploadInput


def test_head_reports_are_separate_from_saved_calibration_and_attachment(objects):
    evidence = normalize_runtime(objects)
    head = evidence.tools[0].model_dump()
    assert head.get("reported_nozzle_diameter") == 0.4
    assert head.get("reported_nozzle_volume_type") == "standard"
    assert head.get("pressure_advance") == 0.02
    assert head.get("pressure_advance_smooth_time") == 0.04
    assert head.get("motion_queue_named") is False
    assert head.get("motion_queue_physical_tool") is None
    assert evidence.missing_fields == []
    assert "stepper_trapq_attachment" in evidence.unestablished_dependencies
    assert "saved_calibration_k" in evidence.unestablished_dependencies
    assert "hidden_feed_thermal_consumption" in evidence.unestablished_dependencies


@pytest.mark.parametrize("name,tool", [("extruder", 1), ("extruder3", 4)])
def test_canonical_queue_names_are_projected_without_attachment_claim(objects, name, tool):
    objects["extruder1"]["motion_queue"] = name
    evidence = normalize_runtime(objects)
    head = evidence.tools[1].model_dump()
    assert head.get("motion_queue_named") is True
    assert head.get("motion_queue_physical_tool") == tool
    assert evidence.missing_fields == []
    assert evidence.inconsistencies == []
    assert "stepper_trapq_attachment" in evidence.unestablished_dependencies


@pytest.mark.parametrize(
    "field,target,bad",
    [
        ("nozzle_diameter", "reported_nozzle_diameter", True),
        ("nozzle_diameter", "reported_nozzle_diameter", "0.4"),
        ("nozzle_diameter", "reported_nozzle_diameter", 0),
        ("nozzle_diameter", "reported_nozzle_diameter", 0.5),
        ("nozzle_diameter", "reported_nozzle_diameter", float("inf")),
        ("nozzle_diameter", "reported_nozzle_diameter", []),
        ("nozzle_volume_type", "reported_nozzle_volume_type", "PRIVATE SECRET"),
        ("nozzle_volume_type", "reported_nozzle_volume_type", {}),
        ("pressure_advance", "pressure_advance", True),
        ("pressure_advance", "pressure_advance", "0.02"),
        ("pressure_advance", "pressure_advance", -0.01),
        ("pressure_advance", "pressure_advance", float("nan")),
        ("pressure_advance", "pressure_advance", 1e7),
        ("smooth_time", "pressure_advance_smooth_time", False),
        ("smooth_time", "pressure_advance_smooth_time", -0.01),
        ("smooth_time", "pressure_advance_smooth_time", 0.201),
        ("smooth_time", "pressure_advance_smooth_time", float("inf")),
        ("motion_queue", "motion_queue_named", False),
        ("motion_queue", "motion_queue_named", []),
        ("motion_queue", "motion_queue_named", ""),
        ("motion_queue", "motion_queue_named", "extruder0"),
        ("motion_queue", "motion_queue_named", "PRIVATE SECRET"),
    ],
)
def test_malformed_head_reports_remain_unknown_and_private(objects, field, target, bad):
    objects["extruder3"][field] = bad
    evidence = normalize_runtime(objects)
    assert evidence.tools[3].model_dump().get(target) is None
    assert f"extruder3.{field}" in evidence.missing_fields
    assert "PRIVATE SECRET" not in evidence.model_dump_json()


def test_zero_pressure_advance_and_smoothing_are_known(objects):
    objects["extruder"].update(pressure_advance=0, smooth_time=0, nozzle_volume_type="high_flow")
    head = normalize_runtime(objects).tools[0].model_dump()
    assert head.get("pressure_advance") == 0
    assert head.get("pressure_advance_smooth_time") == 0
    assert head.get("reported_nozzle_volume_type") == "high_flow"


@pytest.mark.parametrize(
    "field",
    ["nozzle_diameter", "nozzle_volume_type", "pressure_advance", "smooth_time", "motion_queue"],
)
async def test_missing_head_report_blocks_preparation(setup_upload, field):
    settings, printer, file = setup_upload
    del printer.replies["/printer/objects/query"]["result"]["status"]["extruder3"][field]
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with Coordinator(client) as coordinator:
            status = await coordinator.reader.status()
            assert status.outcome == "partial"
            response = await prepared(coordinator, file)
            assert response.outcome == "rejected"
            assert response.errors[0].code == "runtime_evidence_missing"
            assert printer.posts == 0


@pytest.mark.parametrize("head,outcome", [("extruder", "rejected"), ("extruder3", "ok")])
async def test_used_reported_nozzle_must_match_file_and_attestation(setup_upload, head, outcome):
    settings, printer, file = setup_upload
    printer.replies["/printer/objects/query"]["result"]["status"][head]["nozzle_diameter"] = 0.6
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with Coordinator(client) as coordinator:
            response = await prepared(coordinator, file)
            assert response.outcome == outcome
            if outcome == "rejected":
                assert response.errors[0].code == "nozzle_mismatch"
            else:
                assert (
                    response.data.runtime_evidence.data.tools[3]
                    .model_dump()
                    .get("reported_nozzle_diameter")
                    == 0.6
                )
            assert printer.posts == 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("nozzle_diameter", 0.6),
        ("nozzle_volume_type", "high_flow"),
        ("pressure_advance", 0.03),
        ("smooth_time", 0.05),
        ("motion_queue", "extruder"),
    ],
)
@pytest.mark.parametrize("phase", ["prepare", "preflight", "hash", "restart"])
async def test_all_head_report_changes_block_dispatch_or_promotion(
    setup_upload, field, value, phase
):
    settings, printer, file = setup_upload
    head = printer.replies["/printer/objects/query"]["result"]["status"]["extruder3"]
    runtime_reads = 0

    async def serve(request):
        nonlocal runtime_reads
        if request.url.path == "/printer/objects/query" and "gcode_move" in request.url.params:
            runtime_reads += 1
            if phase == "prepare" and runtime_reads == 2:
                head[field] = value
        if request.url.path.startswith("/server/files/gcodes/"):
            if phase == "preflight" or (phase == "hash" and printer.posts):
                head[field] = value
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            if phase == "prepare":
                assert prep.outcome == "rejected"
                assert prep.errors[0].code == "runtime_evidence_changed"
            else:
                assert prep.outcome == "ok"
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
                    head[field] = value
                    printer.files[response.data.remote_path] = file.read_bytes()
                    printer.failure = None
        if phase == "restart":
            with Coordinator(client) as coordinator:
                response = await coordinator.upload(request)
                assert response.outcome == "unknown"
                assert response.errors[0].code == "evidence_changed"
        assert printer.posts == int(phase in {"hash", "restart"})


def test_historical_head_models_deserialize_without_inventing_reports(objects):
    old = normalize_runtime(objects).model_dump()
    for head in old["tools"]:
        for field in (
            "reported_nozzle_diameter",
            "reported_nozzle_volume_type",
            "pressure_advance",
            "pressure_advance_smooth_time",
            "motion_queue_named",
            "motion_queue_physical_tool",
        ):
            head.pop(field, None)
    evidence = RuntimeEvidence.model_validate(old)
    head = evidence.tools[0].model_dump()
    assert "motion_queue_named" in head
    assert head["motion_queue_named"] is None
    assert head["reported_nozzle_diameter"] is None
