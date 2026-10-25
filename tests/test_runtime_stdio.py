"""Exercise runtime evidence through actual MCP subprocesses and loopback HTTP."""

import json
from uuid import uuid4

import pytest
from jsonschema import validate
from test_upload_stdio import connected, file_printer


@pytest.mark.parametrize(
    "change,code",
    [
        ("mesh", "evidence_changed"),
        ("missing", "runtime_evidence_missing"),
        ("uncertain", "evidence_changed"),
        ("exclusion", "evidence_changed"),
        ("missing_exclusion", "runtime_evidence_missing"),
        ("uncertain_exclusion", "evidence_changed"),
        ("head_flow", "evidence_changed"),
        ("missing_head", "runtime_evidence_missing"),
        ("uncertain_head", "evidence_changed"),
    ],
)
async def test_runtime_receipts_and_no_replay_over_actual_mcp(setup_upload, tmp_path, change, code):
    settings, printer, file = setup_upload
    with file_printer(printer) as url:
        config = tmp_path / "config.json"
        config.write_text(
            json.dumps(
                {
                    "printer_url": url,
                    "allowed_roots": [str(tmp_path)],
                    "receipt_db": str(settings.receipt_db),
                    "enable_uploads": True,
                    "nozzle_diameters": [0.4] * 4,
                }
            )
        )
        async with connected(config, tmp_path / "stderr1.txt") as session:
            tools = {t.name: t for t in (await session.list_tools()).tools}
            assert len(tools) == 5
            status = await session.call_tool("u1_status", {})
            validate(status.structuredContent, tools["u1_status"].outputSchema)
            evidence = status.structuredContent["data"]["runtime_evidence"]
            assert evidence["selected_physical_tool"] == 2
            assert evidence["homing_origin"] == [-0.1, 0.2, 0.05, 0]
            assert evidence["exclusion"]["excluded_count"] == 0
            assert evidence["exclusion"]["current_object_present"] is False
            assert evidence["exclusion"]["move_transform_installed"] is None
            assert "SYNTHETIC PRIVATE OBJECT" not in status.content[0].text
            args = {
                "operation_id": str(uuid4()),
                "local_path": str(file),
                "plate": 1,
                "logical_to_physical": [2, 1, 4, 3],
            }
            prep = await session.call_tool("u1_prepare_print", args)
            assert not prep.isError
            validate(prep.structuredContent, tools["u1_prepare_print"].outputSchema)
            assert (
                prep.structuredContent["data"]["runtime_evidence"]["atomic_across_requests"]
                is False
            )
            assert "synthetic-private-profile" not in prep.content[0].text
            request = {"operation_id": str(uuid4()), "preparation_id": args["operation_id"]}
            if change.startswith("uncertain"):
                printer.failure = "lost_without_write"
                result = await session.call_tool("u1_upload_print", request)
                assert result.structuredContent["outcome"] == "unknown"
                printer.files[result.structuredContent["data"]["remote_path"]] = file.read_bytes()
                printer.failure = None
        objects = printer.replies["/printer/objects/query"]["result"]["status"]
        if change == "missing":
            del objects["extruder3"]["extruder_offset"]
        elif change == "missing_exclusion":
            del objects["exclude_object"]["current_object"]
        elif change == "missing_head":
            del objects["extruder3"]["motion_queue"]
        elif change in {"head_flow", "uncertain_head"}:
            objects["extruder3"]["pressure_advance"] = 0.03
        elif change in {"exclusion", "uncertain_exclusion"}:
            objects["exclude_object"]["excluded_objects"] = ["PRIVATE OBJECT"]
        else:
            objects["bed_mesh"]["mesh_matrix"][0][0] += 0.01
        async with connected(config, tmp_path / "stderr2.txt") as session:
            result = await session.call_tool("u1_upload_print", request)
            assert result.isError
            validate(result.structuredContent, tools["u1_upload_print"].outputSchema)
            assert result.structuredContent["errors"][0]["code"] == code
            assert result.structuredContent["outcome"] == (
                "unknown" if change.startswith("uncertain") else "rejected"
            )
            assert printer.posts == int(change.startswith("uncertain"))
            assert evidence["tools"][0].get("reported_nozzle_diameter") == 0.4
            assert evidence["tools"][0].get("pressure_advance") == 0.02
            assert evidence["tools"][0].get("motion_queue_named") is False
