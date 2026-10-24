from copy import deepcopy

import pytest


@pytest.fixture
def objects():
    """Synthetic values, independently shaped from the inspected U1 contract."""
    status = {
        "print_stats": {
            "state": "printing",
            "print_duration": 125,
            "info": {"current_layer": 10, "total_layer": 100},
            "message": "private upstream text",
        },
        "virtual_sdcard": {"progress": 0.25, "is_active": True},
        "toolhead": {"extruder": "extruder1"},
        "heater_bed": {"temperature": 60.2, "target": 60},
        "exception_manager": {"exceptions": []},
        "print_task_config": {
            "extruder_map_table": [1, 0, 3, 2] + [0] * 28,
            "extruders_used": [False, True, False, False],
            "filament_type": ["PLA"] * 4,
            "filament_exist": [True] * 4,
        },
        "filament_detect": {
            "state": [0, 0, 0, 0],
            "info": [
                {
                    "VENDOR": "Example",
                    "MAIN_TYPE": "PLA",
                    "SUB_TYPE": "Fast",
                    "ARGB_COLOR": 4278190080,
                    "SKU": 900000 + i,
                    "CARD_UID": [99, 88, 77, 66],
                }
                for i in range(4)
            ],
        },
        "filament_feed left": {},
        "filament_feed right": {},
    }
    for i, name in enumerate(["extruder", "extruder1", "extruder2", "extruder3"]):
        status[name] = {"temperature": 200 + i, "target": 210, "extruder_index": i}
        status[f"filament_motion_sensor e{i}_filament"] = {
            "enabled": True,
            "filament_detected": True,
        }
        side = "left" if i < 2 else "right"
        status[f"filament_feed {side}"][f"extruder{i}"] = {
            "module_exist": True,
            "filament_detected": True,
            "disable_auto": False,
            "channel_state": "load_finish",
            "channel_error": "ok",
            "channel_error_state": "none",
            "channel_action_state": "load_finish",
        }
    return deepcopy(status)


@pytest.fixture
def replies(objects):
    return {
        "/printer/info": {
            "result": {
                "state": "ready",
                "software_version": "2.0.0.205_20260914173503",
                "hostname": "private-printer",
                "config_file": "C:/private/config",
            }
        },
        "/server/info": {"result": {"klippy_connected": True, "moonraker_version": "2.0.0"}},
        "/printer/objects/list": {"result": {"objects": list(objects)}},
        "/printer/objects/query": {"result": {"eventtime": 123.5, "status": objects}},
        "/server/webcams/list": {"result": {"webcams": []}},
    }
