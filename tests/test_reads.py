import json

import httpx
import pytest

from snapmaker_u1_mcp.adapter import U1Reader
from snapmaker_u1_mcp.config import Settings
from snapmaker_u1_mcp.transport import Moonraker


@pytest.fixture
async def reader(replies):
    def serve(request):
        assert request.method == "GET"
        assert request.url.host == "printer.invalid"
        if request.url.path == "/printer/objects/query":
            # No raw object names from the printer may enter queries.
            assert "configfile" not in request.url.params
            assert set(request.url.params).issubset(
                replies["/printer/objects/list"]["result"]["objects"]
            )
        # Deliberately allow non-standard NaN/Infinity to exercise bad peer input.
        return httpx.Response(
            200, stream=httpx.ByteStream(json.dumps(replies[request.url.path]).encode())
        )

    settings = Settings(printer_url="http://printer.invalid:7125", api_key="SECRET-KEY")
    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        yield U1Reader(client)


async def test_ready_does_not_mean_idle_and_active_tool_is_one_based(reader):
    result = (await reader.status()).model_dump(mode="json")
    assert result["outcome"] == "ok"
    assert result["data"]["klipper_state"] == "ready"
    assert result["data"]["busy"] is True
    assert result["data"]["idle"] is False
    assert result["data"]["selected_physical_tool"] == 2
    assert result["data"]["progress"] == 0.25
    assert result["data"]["temperatures"][2]["temperature"] == 202
    assert result["data"]["current_layer"] == 10
    assert result["observed_at"].endswith("Z")
    text = json.dumps(result)
    assert all(x not in text for x in ["private-printer", "C:/private", "private upstream"])


async def test_all_four_tools_mapping_and_no_card_identifier_leak(reader):
    data = (await reader.materials()).data
    assert [t.physical_tool for t in data.tools] == [1, 2, 3, 4]
    assert [t.gcode_tool for t in data.tools] == ["T0", "T1", "T2", "T3"]
    assert data.logical_to_physical[:4] == [2, 1, 4, 3]
    assert len(data.logical_to_physical) == 32
    assert [t.used_by_job for t in data.tools] == [False, True, False, False]
    assert all(t.loaded_state == "loaded" for t in data.tools)
    assert data.tools[0].rfid.color_rgba == "000000FF"
    assert "CARD_UID" not in data.model_dump_json()


@pytest.mark.parametrize(
    "change,want",
    [
        ("missing_sensor", "unknown"),
        ("disabled_sensor", "unknown"),
        ("sensor_absent", "not_loaded"),
        ("missing_feed", "unknown"),
        ("feed_absent", "unknown"),
        ("feed_error", "unknown"),
        ("loading", "unknown"),
    ],
)
async def test_rfid_never_substitutes_for_feed_evidence(reader, objects, change, want):
    sensor = objects["filament_motion_sensor e0_filament"]
    feed = objects["filament_feed left"]["extruder0"]
    if change == "missing_sensor":
        sensor.clear()
    elif change == "disabled_sensor":
        sensor["enabled"] = False
    elif change == "sensor_absent":
        sensor["filament_detected"] = False
    elif change == "missing_feed":
        feed.clear()
    elif change == "feed_absent":
        feed["filament_detected"] = False
    elif change == "feed_error":
        feed["channel_error"] = "jam"
    elif change == "loading":
        feed["channel_state"] = "loading"
    data = (await reader.materials()).data
    assert data.tools[0].rfid.material_type == "PLA"
    assert data.tools[0].loaded_state == want


async def test_partial_mapping_is_not_coerced_and_unused_slots_are_not_job_use(reader, objects):
    objects["print_task_config"]["extruder_map_table"] = [3, -1, True, "2", 4]
    result = await reader.materials()
    assert result.outcome == "partial"
    assert result.data.logical_to_physical[:5] == [4, None, None, None, None]
    assert result.data.tools[0].used_by_job is False
    assert result.data.mapping_complete is False


async def test_missing_objects_remain_unknown_instead_of_healthy(reader, replies, objects):
    del objects["exception_manager"]
    del objects["virtual_sdcard"]
    replies["/printer/objects/list"]["result"]["objects"] = list(objects)
    result = await reader.status()
    assert result.outcome == "partial"
    assert result.data.exceptions_known is False
    assert result.data.virtual_sd_active is None
    assert result.data.idle is False  # printing still proves busy


async def test_exception_levels_and_unrecognized_records_are_conservative(reader, objects):
    objects["print_stats"]["state"] = "standby"
    objects["virtual_sdcard"]["is_active"] = False
    objects["exception_manager"]["exceptions"] = [
        {
            "id": 531,
            "index": 0,
            "code": 17,
            "level": 2,
            "message": "http://private.invalid password=SECRET-KEY",
        },
        {"id": 500, "index": 1, "code": 9, "level": 1},
        {"id": "unexpected", "level": "new"},
    ]
    result = await reader.status()
    assert result.data.idle is False
    assert [e.blocking for e in result.data.exceptions] == [True, False, None]
    assert result.outcome == "partial"
    assert "SECRET-KEY" not in result.model_dump_json()


async def test_invalid_numeric_and_boolean_values_are_not_coerced(reader, objects):
    objects["virtual_sdcard"] = {"is_active": "false", "progress": float("nan")}
    objects["heater_bed"] = {"temperature": float("inf"), "target": -2}
    objects["print_stats"]["state"] = "standby"
    result = await reader.status()
    assert result.data.virtual_sd_active is None
    assert result.data.progress is None
    assert result.data.bed.temperature is None
    assert result.data.idle is None
    assert result.outcome == "partial"


async def test_capabilities_separate_observed_reads_from_unimplemented_operations(reader):
    data = (await reader.capabilities()).data
    assert data.firmware_version == "2.0.0.205_20260914173503"
    assert data.transports == ["moonraker_http"]
    assert data.implemented_tools == ["u1_capabilities", "u1_status", "u1_materials"]
    assert data.camera.availability == "unknown"
    assert data.camera.configured_webcams == 0
    assert "u1_start_print" in data.unimplemented_tools


async def test_http_200_error_does_not_return_old_success(reader, replies):
    assert (await reader.status()).outcome == "ok"
    replies["/printer/objects/query"] = {
        "error": {"code": 400, "message": "password=SECRET-KEY at http://private.invalid"}
    }
    result = await reader.status()
    assert result.outcome == "rejected"
    assert result.data is None
    assert result.errors[0].code == "printer_error"
    assert "SECRET-KEY" not in result.model_dump_json()


@pytest.mark.parametrize("value", ["192.0.2.44", "SECRET-KEY", "printer.invalid", "token-value"])
async def test_firmware_identity_never_projects_addresses_or_secrets(reader, replies, value):
    replies["/printer/info"]["result"]["software_version"] = value
    result = await reader.capabilities()
    assert result.data.firmware_version is None
    assert value not in result.model_dump_json()
    assert result.outcome == "partial"


@pytest.mark.parametrize("value", [None, {}, ["bad"], "unexpected"])
async def test_malformed_inventory_never_invents_support(reader, replies, value):
    replies["/printer/objects/list"]["result"]["objects"] = value
    status = await reader.status()
    assert status.outcome == "unavailable"
    assert status.data is None
    capabilities = await reader.capabilities()
    assert capabilities.outcome == "partial"
    assert capabilities.data.observed_objects == []


async def test_idle_requires_both_inactive_print_state_and_known_clear_exceptions(reader, objects):
    objects["print_stats"]["state"] = "standby"
    objects["virtual_sdcard"]["is_active"] = False
    assert (await reader.status()).data.idle is True
    objects["exception_manager"]["exceptions"] = None
    result = await reader.status()
    assert result.data.idle is None
    assert result.data.exceptions_known is False


@pytest.mark.parametrize("field", ["VENDOR", "MAIN_TYPE", "SUB_TYPE"])
async def test_untrusted_material_labels_cannot_disclose_connection_data(reader, objects, field):
    for value in [
        "SECRET-KEY",
        "http://printer.invalid",
        "192.0.2.44",
        "C:/private/path",
        "password=value",
        "injected\nmessage",
    ]:
        objects["filament_detect"]["info"][0][field] = value
        result = await reader.materials()
        assert value not in result.model_dump_json()
