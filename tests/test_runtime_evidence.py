"""Reported fields are evidence only; never infer calibration or transform safety."""

import json

import httpx
import pytest

from snapmaker_u1_mcp.adapter import U1Reader
from snapmaker_u1_mcp.config import Settings
from snapmaker_u1_mcp.transport import Moonraker


@pytest.fixture
async def runtime_reader(replies):
    def serve(request):
        assert request.method == "GET"
        return httpx.Response(
            200, stream=httpx.ByteStream(json.dumps(replies[request.url.path]).encode())
        )

    async with Moonraker(
        Settings(printer_url="http://printer.invalid"), transport=httpx.MockTransport(serve)
    ) as client:
        yield U1Reader(client)


async def test_reported_signed_coordinates_and_different_transformed_positions(runtime_reader):
    response = await runtime_reader.status()
    evidence = response.data.runtime_evidence
    assert response.outcome == "ok"
    assert evidence.homed_axes == "xyz"
    assert evidence.selected_physical_tool == 2
    assert evidence.toolhead_position == [100, 100, 2.1, 0]
    assert evidence.gcode_move_position == [100, 100, 2, 0]
    assert evidence.homing_origin == [-0.1, 0.2, 0.05, 0]
    assert evidence.tools[3].reported_offset == pytest.approx([-0.3, 0.6, 0.15])
    assert evidence.mesh.reported_state == "populated"
    assert evidence.mesh.mesh_matrix.rows == 3
    assert evidence.mesh.mesh_matrix.columns == 3
    assert len(evidence.mesh.profile_sha256) == 64
    assert evidence.missing_fields == []
    assert evidence.inconsistencies == []
    assert evidence.running_code_attested is False
    assert evidence.atomic is False
    assert "transform_chain" in evidence.unestablished_dependencies
    assert "synthetic-private-profile" not in response.model_dump_json()


async def test_all_parked_does_not_prove_a_physically_gripped_selected_head(
    runtime_reader, objects
):
    objects["toolhead"]["homed_axes"] = ""
    for name in ("extruder", "extruder1", "extruder2", "extruder3"):
        objects[name].update(
            state="PARKED",
            active_pin=False,
            park_pin=True,
            grab_valid_pin=False,
            real_extruder_stats=["extruder1", 1],
        )
    evidence = (await runtime_reader.status()).data.runtime_evidence
    assert evidence.homed_axes == ""
    assert evidence.selected_physical_tool == 2
    assert evidence.reported_gripped_tool is None
    assert evidence.tools[0].activation_status == 1
    assert evidence.inconsistencies == []
    assert evidence.missing_fields == []


async def test_all_parked_aggregate_must_agree_with_selected_object(runtime_reader, objects):
    for name in ("extruder", "extruder1", "extruder2", "extruder3"):
        objects[name].update(state="PARKED", real_extruder_stats=["extruder", 1])
    response = await runtime_reader.status()
    assert response.outcome == "partial"
    assert response.data.runtime_evidence.reported_gripped_tool is None
    assert "selection_report_mismatch" in response.data.runtime_evidence.inconsistencies


async def test_empty_mesh_with_nonzero_extrema_is_unknown(runtime_reader, objects):
    objects["bed_mesh"].update(profile_name="", mesh_matrix=[[]], probed_matrix=[[]])
    response = await runtime_reader.status()
    assert response.outcome == "partial"
    assert response.data.runtime_evidence.mesh.reported_state == "unknown"
    assert "mesh_state_mismatch" in response.data.runtime_evidence.inconsistencies


async def test_reported_zero_offsets_do_not_establish_calibration(runtime_reader, objects):
    objects["extruder"]["extruder_offset"] = [0, 0, 0]
    evidence = (await runtime_reader.status()).data.runtime_evidence
    assert evidence.tools[0].reported_offset == [0, 0, 0]
    assert "offset_calibration_provenance" in evidence.unestablished_dependencies
    assert evidence.running_code_attested is False


@pytest.mark.parametrize(
    "bad",
    [
        None,
        [0, 0],
        [0, True, 0],
        [0, "0", 0],
        [0, float("nan"), 0],
        [0, float("inf"), 0],
        [0, 1e20, 0],
    ],
)
async def test_bad_offset_never_becomes_zero_or_known(runtime_reader, objects, bad):
    objects["extruder"]["extruder_offset"] = bad
    response = await runtime_reader.status()
    assert response.outcome == "partial"
    assert response.data.runtime_evidence.tools[0].reported_offset is None
    assert "extruder.extruder_offset" in response.data.runtime_evidence.missing_fields


@pytest.mark.parametrize(
    "field,bad",
    [
        ("absolute_coordinates", 1),
        ("absolute_extrude", "false"),
        ("homing_origin", [0, 0, 0]),
        ("extrude_factor", 0),
        ("speed_factor", True),
    ],
)
async def test_bad_mode_or_origin_stays_unknown(runtime_reader, objects, field, bad):
    objects["gcode_move"][field] = bad
    response = await runtime_reader.status()
    assert response.outcome == "partial"
    assert getattr(response.data.runtime_evidence, field) is None
    assert f"gcode_move.{field}" in response.data.runtime_evidence.missing_fields


@pytest.mark.parametrize(
    "bad", [[[1, 2], [3]], [[True]], [[float("nan")]], [[0] * 129], "SECRET", []]
)
async def test_malformed_or_oversized_mesh_is_unknown(runtime_reader, objects, bad):
    objects["bed_mesh"]["mesh_matrix"] = bad
    response = await runtime_reader.status()
    assert response.outcome == "partial"
    assert response.data.runtime_evidence.mesh.mesh_matrix is None
    assert "bed_mesh.mesh_matrix" in response.data.runtime_evidence.missing_fields
    assert "SECRET" not in response.model_dump_json()


async def test_clear_mesh_is_distinct_from_missing_mesh(runtime_reader, objects):
    objects["bed_mesh"].update(
        profile_name="",
        mesh_min=[0, 0],
        mesh_max=[0, 0],
        mesh_matrix=[[]],
        probed_matrix=[[]],
    )
    response = await runtime_reader.status()
    assert response.outcome == "ok"
    assert response.data.runtime_evidence.mesh.reported_state == "empty"
    objects["bed_mesh"].clear()
    response = await runtime_reader.status()
    assert response.outcome == "partial"
    assert response.data.runtime_evidence.mesh.reported_state == "unknown"


async def test_indices_and_activation_disagreement_are_explicit(runtime_reader, objects):
    objects["extruder3"]["extruder_index"] = 1
    objects["extruder2"]["real_extruder_stats"] = ["extruder", 0]
    response = await runtime_reader.status()
    assert response.outcome == "partial"
    assert "extruder_index_mismatch" in response.data.runtime_evidence.inconsistencies
    assert "activation_reports_disagree" in response.data.runtime_evidence.inconsistencies


async def test_missing_objects_and_private_extra_fields_do_not_invent_evidence(
    runtime_reader, replies, objects
):
    objects.pop("gcode_move")
    replies["/printer/objects/list"]["result"]["objects"] = list(objects)
    objects["bed_mesh"]["profiles"] = {"SECRET C:/private/path": {"secret": "value"}}
    response = await runtime_reader.status()
    assert response.outcome == "partial"
    assert response.data.runtime_evidence.homing_origin is None
    assert "gcode_move" in response.data.missing_objects
    assert "SECRET" not in response.model_dump_json()


async def test_known_empty_exclusion_does_not_attest_transform_removal(runtime_reader):
    response = await runtime_reader.status()
    exclusion = response.data.runtime_evidence.exclusion
    assert response.outcome == "ok"
    assert exclusion.excluded_count == 0
    assert exclusion.excluded_sha256 == (
        "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
    )
    assert exclusion.current_object_present is False
    assert exclusion.current_object_sha256 is None
    assert exclusion.in_excluded_region is False
    assert exclusion.move_transform_installed is None


async def test_exclusion_labels_are_private_and_region_may_lag_marker(runtime_reader, objects):
    objects["exclude_object"].update(
        excluded_objects=["SYNTHETIC PRIVATE OBJECT"],
        current_object=None,
        in_excluded_region=True,
        next_transform="SECRET",
    )
    response = await runtime_reader.status()
    exclusion = response.data.runtime_evidence.exclusion
    assert response.outcome == "ok"
    assert exclusion.excluded_count == 1
    assert len(exclusion.excluded_sha256) == 64
    assert exclusion.current_object_present is False
    assert exclusion.in_excluded_region is True
    assert exclusion.move_transform_installed is None
    assert "PRIVATE" not in response.model_dump_json()
    assert "SECRET" not in response.model_dump_json()
    # Source can retain the region flag after END or resetting exclusions.
    objects["exclude_object"]["excluded_objects"] = []
    assert (await runtime_reader.status()).outcome == "ok"


async def test_current_object_hash_changes_without_publishing_label(runtime_reader, objects):
    objects["exclude_object"]["current_object"] = "SYNTHETIC PRIVATE OBJECT"
    first = await runtime_reader.status()
    assert first.data.runtime_evidence.exclusion.current_object_present is True
    assert len(first.data.runtime_evidence.exclusion.current_object_sha256) == 64
    objects["exclude_object"]["current_object"] = "ANOTHER PRIVATE OBJECT"
    second = await runtime_reader.status()
    assert first.data.runtime_evidence.exclusion != second.data.runtime_evidence.exclusion
    assert "PRIVATE" not in first.model_dump_json() + second.model_dump_json()


@pytest.mark.parametrize("key", ["excluded_objects", "current_object", "in_excluded_region"])
async def test_missing_exclusion_fields_stay_unknown(runtime_reader, objects, key):
    del objects["exclude_object"][key]
    response = await runtime_reader.status()
    assert response.outcome == "partial"
    assert f"exclude_object.{key}" in response.data.runtime_evidence.missing_fields
    if key == "current_object":
        assert response.data.runtime_evidence.exclusion.current_object_present is None


@pytest.mark.parametrize(
    "key,bad",
    [
        ("excluded_objects", None),
        ("excluded_objects", "SECRET"),
        ("excluded_objects", [True]),
        ("excluded_objects", ["X" * 257]),
        ("excluded_objects", [str(i) for i in range(1025)]),
        ("excluded_objects", ["DUPLICATE", "DUPLICATE"]),
        ("current_object", False),
        ("current_object", {}),
        ("current_object", "X" * 257),
        ("in_excluded_region", 0),
        ("in_excluded_region", "false"),
    ],
)
async def test_malformed_or_oversized_exclusion_is_unknown(runtime_reader, objects, key, bad):
    objects["exclude_object"][key] = bad
    response = await runtime_reader.status()
    assert response.outcome == "partial"
    assert f"exclude_object.{key}" in response.data.runtime_evidence.missing_fields
    assert "SECRET" not in response.model_dump_json()


async def test_missing_exclusion_object_is_partial(runtime_reader, replies, objects):
    objects.pop("exclude_object")
    replies["/printer/objects/list"]["result"]["objects"] = list(objects)
    response = await runtime_reader.status()
    assert response.outcome == "partial"
    assert "exclude_object" in response.data.missing_objects


async def test_status_uses_only_fixed_exclusion_fields(replies):
    queries = []

    def serve(request):
        if request.url.path == "/printer/objects/query":
            queries.append(dict(request.url.params))
        return httpx.Response(
            200, stream=httpx.ByteStream(json.dumps(replies[request.url.path]).encode())
        )

    async with Moonraker(
        Settings(printer_url="http://printer.invalid"), transport=httpx.MockTransport(serve)
    ) as client:
        assert (await U1Reader(client).status()).outcome == "ok"
    assert queries[0].get("exclude_object") == (
        "excluded_objects,current_object,in_excluded_region"
    )
