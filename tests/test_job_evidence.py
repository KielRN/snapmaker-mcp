"""Reported job preferences bind receipts, never certify completed actions."""

from uuid import uuid4

import httpx
import pytest
from test_uploads import prepared

from snapmaker_u1_mcp.models import RuntimeEvidence
from snapmaker_u1_mcp.runtime import normalize_runtime
from snapmaker_u1_mcp.transport import Moonraker
from snapmaker_u1_mcp.uploads import Coordinator, UploadInput

BOOLEAN_FIELDS = (
    "time_lapse_camera",
    "auto_bed_leveling",
    "flow_calibrate",
    "shaper_calibrate",
    "auto_replenish_filament",
    "replenish_ignore_color",
    "filament_entangle_detect",
    "end_led_turn_off",
)
ARRAY_FIELDS = ("flow_calib_extruders", "end_unload_filament")
FIELDS = (*BOOLEAN_FIELDS, *ARRAY_FIELDS, "filament_entangle_sen")


@pytest.mark.parametrize("field", BOOLEAN_FIELDS)
@pytest.mark.parametrize("bad", [None, 0, 1, "PRIVATE FLAG", [], {}])
def test_invalid_job_booleans_stay_unknown_private(objects, field, bad):
    objects["print_task_config"][field] = bad
    evidence = normalize_runtime(objects)
    assert evidence.model_dump().get("job", {}).get(field) is None
    assert f"print_task_config.{field}" in evidence.missing_fields
    assert "PRIVATE FLAG" not in evidence.model_dump_json()


@pytest.mark.parametrize("field", ARRAY_FIELDS)
@pytest.mark.parametrize(
    "bad",
    [None, [], [True] * 3, [True] * 5, [1] * 4, [False, False, False, None], "PRIVATE FLAGS", {}],
)
def test_job_tool_flags_require_four_exact_booleans(objects, field, bad):
    objects["print_task_config"][field] = bad
    evidence = normalize_runtime(objects)
    assert evidence.model_dump().get("job", {}).get(field) is None
    assert f"print_task_config.{field}" in evidence.missing_fields
    assert "PRIVATE FLAGS" not in evidence.model_dump_json()


@pytest.mark.parametrize("bad", [None, True, 1, "HIGH", "PRIVATE SENSITIVITY", [], {}])
def test_unknown_sensitivity_is_not_reflected(objects, bad):
    objects["print_task_config"]["filament_entangle_sen"] = bad
    evidence = normalize_runtime(objects)
    assert "print_task_config.filament_entangle_sen" in evidence.missing_fields
    assert "PRIVATE SENSITIVITY" not in evidence.model_dump_json()


@pytest.mark.parametrize("field", FIELDS)
def test_missing_job_reports_are_not_defaults(objects, field):
    objects["print_task_config"].pop(field, None)
    evidence = normalize_runtime(objects)
    assert f"print_task_config.{field}" in evidence.missing_fields


def test_job_flags_preserve_physical_order_and_are_not_completion(objects):
    job = objects["print_task_config"]
    job.update({field: True for field in BOOLEAN_FIELDS})
    job["flow_calib_extruders"] = [True, False, True, False]
    job["end_unload_filament"] = [False, True, False, True]
    job["filament_entangle_sen"] = "low"
    job["reprint_info"] = {"PRIVATE REPRINT": "PRIVATE CONFIG"}
    evidence = normalize_runtime(objects)
    expected = {field: job[field] for field in FIELDS}
    assert evidence.model_dump().get("job") == expected
    assert not any(key.startswith("print_task_config.") for key in evidence.missing_fields)
    assert "PRIVATE" not in evidence.model_dump_json()
    assert "job_action_completion" in evidence.unestablished_dependencies
    assert "reprint_and_job_parameters" in evidence.unestablished_dependencies


async def test_fixed_job_projection_keeps_materials_and_binds_both_reads(setup_upload):
    settings, printer, file = setup_upload
    queries = []

    async def serve(request):
        if request.url.path == "/printer/objects/query":
            queries.append(dict(request.url.params))
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            assert prep.outcome == "ok"
            assert prep.data.runtime_evidence.data.model_dump().get("job") == {
                field: printer.replies["/printer/objects/query"]["result"]["status"][
                    "print_task_config"
                ][field]
                for field in FIELDS
            }
        for projection in ("", "time_lapse_camera", "reprint_info"):
            with pytest.raises(ValueError):
                await client.get("/printer/objects/query", {"print_task_config": projection})
    assert len([q for q in queries if "gcode_move" in q]) == 2
    expected = {*FIELDS, "extruder_map_table", "extruders_used", "filament_type"}
    assert all(set(q.get("print_task_config", "").split(",")) == expected for q in queries)


@pytest.mark.parametrize("field", FIELDS)
@pytest.mark.parametrize("phase", ["prepare", "preflight", "hash", "restart"])
@pytest.mark.parametrize("missing", [False, True])
async def test_job_races_block_dispatch_or_promotion(setup_upload, field, phase, missing):
    settings, printer, file = setup_upload
    objects = printer.replies["/printer/objects/query"]["result"]["status"]
    reads = 0

    def mutate():
        config = objects["print_task_config"]
        if missing:
            config.pop(field, None)
        elif field in BOOLEAN_FIELDS:
            config[field] = not config[field]
        elif field in ARRAY_FIELDS:
            config[field][3] = not config[field][3]
        else:
            config[field] = "high"

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
                    "runtime_evidence_missing" if missing else "runtime_evidence_changed"
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
                    assert response.errors[0].code == (
                        "runtime_evidence_missing" if missing else "evidence_changed"
                    )
        if phase == "restart":
            with Coordinator(client) as coordinator:
                response = await coordinator.upload(request)
                assert response.outcome == "unknown"
                assert response.errors[0].code == (
                    "runtime_evidence_missing" if missing else "evidence_changed"
                )
    assert printer.posts == int(phase in {"hash", "restart"})


def test_historical_job_reports_deserialize_as_unknown(objects):
    old = normalize_runtime(objects).model_dump()
    old.pop("job", None)
    evidence = RuntimeEvidence.model_validate(old)
    assert evidence.model_dump().get("job") == dict.fromkeys(FIELDS)
