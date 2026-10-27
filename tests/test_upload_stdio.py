import asyncio
import json
import sys
import threading
from contextlib import asynccontextmanager, contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from jsonschema import validate
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

FIXTURES = Path(__file__).parent / "fixtures"


@contextmanager
def file_printer(printer):
    class Handler(BaseHTTPRequestHandler):
        def handle_request(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            request = httpx.Request(
                self.command,
                "http://printer.invalid" + self.path,
                headers=dict(self.headers),
                content=body,
            )
            try:
                response = asyncio.run(printer.serve(request))
            except httpx.TimeoutException:
                self.close_connection = True
                return
            data = response.read()
            self.send_response(response.status_code)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        do_GET = handle_request
        do_POST = handle_request

        def log_message(self, *args):
            pass

    http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{http.server_port}"
    finally:
        http.shutdown()
        http.server_close()
        thread.join(timeout=2)


@asynccontextmanager
async def connected(config, stderr_path):
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "snapmaker_u1_mcp"], env={"U1_CONFIG_FILE": str(config)}
    )
    with stderr_path.open("w+", encoding="utf-8") as stderr:
        async with asyncio.timeout(40), stdio_client(params, errlog=stderr) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
        stderr.seek(0)
        assert stderr.read() == ""


async def test_actual_stdio_preparation_upload_hash_and_restart_reconciliation(
    setup_upload,
    tmp_path,
):
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
            prep_args = {
                "operation_id": str(uuid4()),
                "local_path": str(file),
                "plate": 1,
                "logical_to_physical": [2, 1, 4, 3],
            }
            response = await session.call_tool("u1_prepare_print", prep_args)
            assert not response.isError
            p = response.structuredContent
            validate(p, tools["u1_prepare_print"].outputSchema)
            assert str(file) not in response.content[0].text
            assert printer.posts == 0
            rejected = await session.call_tool(
                "u1_prepare_print", {**prep_args, "secret": "SECRET"}
            )
            assert rejected.isError
            assert "SECRET" not in rejected.content[0].text
            request = {"operation_id": str(uuid4()), "preparation_id": p["data"]["preparation_id"]}
            printer.failure = "lost_without_write"
            response = await session.call_tool("u1_upload_print", request)
            assert response.isError
            assert response.structuredContent["outcome"] == "unknown"
            remote = response.structuredContent["data"]["remote_path"]
        printer.files[remote] = file.read_bytes()
        printer.failure = None
        async with connected(config, tmp_path / "stderr2.txt") as session:
            response = await session.call_tool("u1_upload_print", request)
            validate(response.structuredContent, tools["u1_upload_print"].outputSchema)
            assert response.structuredContent["data"]["state"] == "verified"
            assert response.structuredContent["data"]["reconciled"] is True
            assert not response.isError
            assert printer.posts == 1

            assert (
                await session.call_tool("u1_upload_print", request)
            ).structuredContent == response.structuredContent
            conflict = await session.call_tool(
                "u1_upload_print", {**request, "preparation_id": str(uuid4())}
            )
            assert conflict.structuredContent["errors"][0]["code"] == "operation_conflict"
            assert printer.posts == 1


@pytest.mark.parametrize(
    "failure,expected",
    [
        ("error", "printer_error"),
        ("corrupt", "hash_mismatch"),
        ("missing", "material_not_loaded"),
        ("mapping", "mapping_changed"),
        ("escape", "path_not_allowed"),
    ],
)
async def test_failure_outcomes_over_actual_stdio_http(setup_upload, tmp_path, failure, expected):
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
        async with connected(config, tmp_path / "stderr.txt") as session:
            args = {
                "operation_id": str(uuid4()),
                "local_path": str(file),
                "plate": 1,
                "logical_to_physical": [2, 1, 4, 3],
            }
            if failure == "escape":
                args["local_path"] = str(tmp_path.parent / "private.gcode")
            prep = await session.call_tool("u1_prepare_print", args)
            if failure == "escape":
                response = prep
            else:
                assert not prep.isError
                objects = printer.replies["/printer/objects/query"]["result"]["status"]
                if failure == "missing":
                    objects["filament_motion_sensor e0_filament"]["filament_detected"] = False
                elif failure == "mapping":
                    objects["print_task_config"]["extruder_map_table"][1] = 1
                else:
                    printer.failure = failure
                args = {
                    "operation_id": str(uuid4()),
                    "preparation_id": prep.structuredContent["data"]["preparation_id"],
                }
                response = await session.call_tool("u1_upload_print", args)
            assert response.isError
            assert response.structuredContent["errors"][0]["code"] == expected
            assert "SECRET" not in response.content[0].text
            assert str(file) not in response.content[0].text
            assert printer.posts == (1 if failure in {"error", "corrupt"} else 0)


async def test_documented_connection_checker_calls_only_reads(setup_upload, tmp_path):
    import os

    _, printer, _ = setup_upload
    with file_printer(printer) as url:
        env = {k: v for k, v in os.environ.items() if not k.startswith("U1_")}
        child = await asyncio.create_subprocess_exec(
            sys.executable,
            "tools/check_connection.py",
            env={**env, "U1_PRINTER_URL": url},
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(child.communicate(), 15)
        assert child.returncode == 0
        assert stderr == b""
        assert set(json.loads(stdout)) == {"u1_status", "u1_materials", "u1_capabilities"}
        assert printer.posts == 0


@pytest.mark.parametrize(
    "pattern,expected",
    [
        ("numeric", None),
        ("tool_xyz", None),
        ("stock", "unsupported_command"),
        ("arc_bounds", "movement_bounds"),
        ("arc_endpoint", "movement_bounds"),
        ("arc_cold", "cold_extrusion"),
        ("arc_consumption", "consumption_understated"),
        ("missing_plane", "position_unknown"),
        ("fan_syntax", "job_requirements"),
        ("later_tool", "consumption_missing"),
        ("tool_relative", "position_unknown"),
        ("tool_partial", "position_unknown"),
        ("tool_arc", "position_unknown"),
        ("heater_unused", "consumption_missing"),
        ("heater_syntax", "unsupported_tool"),
        ("heater_alias", "mapping_ambiguous"),
        ("homing_tool", "unsupported_tool"),
        ("heated_feed", "material_not_loaded"),
        ("tool_syntax", "unsupported_tool"),
    ],
)
async def test_orca_forms_over_real_mcp_preserve_bytes_and_rejections(
    setup_upload, tmp_path, pattern, expected
):
    settings, printer, file = setup_upload
    data = (FIXTURES / "orca_u1_numeric.gcode").read_bytes()
    mapping = [2, 1, 4, 3]
    if pattern == "stock":
        data = (FIXTURES / "orca_u1_stock_shape.gcode").read_bytes()
    elif pattern == "arc_bounds":
        data = data.replace(b"I10 J0 Z1 E5", b"I-10 J0 Z1 E5")
    elif pattern == "arc_endpoint":
        data = data.replace(b"G2 X30", b"G2 X271")
    elif pattern == "arc_cold":
        data = data.replace(b"G17", b"M104 S0\nG17")
    elif pattern == "arc_consumption":
        data = data.replace(b"Z1 E5", b"Z1 E11")
    elif pattern == "missing_plane":
        data = data.replace(b"G17", b"; no plane established")
    elif pattern == "fan_syntax":
        data = data.replace(b"P2 S178", b"P2.0 S178")
    elif pattern == "later_tool":
        data += b"T2\nM109 S210\nG1 X10 Y20 Z1\nG1 E1\n"
    elif pattern == "tool_xyz":
        data = data.replace(b"G17", b"T1\nG1 X10 Y20 Z0.2\nG17")
    elif pattern == "tool_relative":
        data += b"T1\nG91\nG1 X1\n"
    elif pattern == "tool_partial":
        data += b"T1\nG1 X20\n"
    elif pattern == "tool_arc":
        data += b"T1\nG2 I10 J0\n"
    elif pattern == "heater_unused":
        data += b"M104 T2 S140\n"
    elif pattern == "heater_syntax":
        data += b"M104 T1.0 S0\n"
    elif pattern == "heater_alias":
        mapping = [1, 1, 4, 3]
        printer.replies["/printer/objects/query"]["result"]["status"]["print_task_config"][
            "extruder_map_table"
        ][:4] = [0, 0, 3, 2]
        data = data.replace(b"M109 S210", b"M109 T1 S210\nM104 T0 S0")
    elif pattern == "homing_tool":
        data += b"G28\nM104 S210\n"
    elif pattern == "heated_feed":
        data = data.replace(b"0, 10, 0, 0", b"0, 10, 1, 0").replace(
            b"0, 0.03, 0, 0", b"0, 0.03, 0.01, 0"
        )
        data += b"M109 T2 S210\n"
        printer.replies["/printer/objects/query"]["result"]["status"][
            "filament_motion_sensor e3_filament"
        ]["filament_detected"] = False
    elif pattern == "tool_syntax":
        data = data.replace(b"T1\n", b"T01\n")
    file.write_bytes(data)
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
        async with connected(config, tmp_path / "stderr.txt") as session:
            args = {
                "operation_id": str(uuid4()),
                "local_path": str(file),
                "plate": 1,
                "logical_to_physical": mapping,
            }
            prep = await session.call_tool("u1_prepare_print", args)
            assert printer.posts == 0
            if expected:
                assert prep.isError
                assert prep.structuredContent["outcome"] == "rejected"
                assert prep.structuredContent["errors"][0]["code"] == expected
                return
            assert not prep.isError
            inspection = prep.structuredContent["data"]["inspection"]
            assert inspection["used_tools"] == [1]
            assert inspection["bounds_max"] == [30, 30, 1]
            upload = await session.call_tool(
                "u1_upload_print",
                {
                    "operation_id": str(uuid4()),
                    "preparation_id": prep.structuredContent["data"]["preparation_id"],
                },
            )
            assert not upload.isError
            result = upload.structuredContent["data"]
            assert result["state"] == "verified"
            assert result["authorizes_start"] is False
            assert result["hardware_accepted"] is False
            assert result["remote_sha256"] == prep.structuredContent["data"]["sha256"]
            assert printer.files[result["remote_path"]] == data
            assert printer.posts == 1


@pytest.mark.parametrize("dispatched", [False, True])
@pytest.mark.parametrize("validator", [2, 3, 4, 5, 6, 7, 8, 9])
async def test_old_policy_receipts_cannot_promote_over_real_mcp(
    setup_upload, tmp_path, monkeypatch, dispatched, validator
):
    from dataclasses import replace

    from test_uploads import prepared

    from snapmaker_u1_mcp import uploads
    from snapmaker_u1_mcp.transport import Moonraker

    settings, printer, file = setup_upload
    with file_printer(printer) as url:
        settings = replace(settings, printer_url=url)
        async with Moonraker(settings) as client:
            with uploads.Coordinator(client) as coordinator:
                old_policy = uploads.digest(
                    {
                        "origin": url,
                        "roots": [str(p) for p in settings.allowed_roots],
                        "nozzles": settings.nozzle_diameters,
                        "maximum": settings.max_gcode_bytes,
                        "validator": validator,
                    }
                )
                with monkeypatch.context() as patch:
                    patch.setattr(coordinator, "_policy", lambda: old_policy)
                    prep = await prepared(coordinator, file)
                    assert prep.outcome == "ok"
                    request = uploads.UploadInput(
                        operation_id=str(uuid4()), preparation_id=prep.data.preparation_id
                    )
                    if dispatched:
                        printer.failure = "lost_without_write"
                        uncertain = await coordinator.upload(request)
                        assert uncertain.outcome == "unknown"
                        printer.files[uncertain.data.remote_path] = file.read_bytes()
        printer.failure = None
        config = tmp_path / "config.json"
        config.write_text(
            json.dumps(
                {
                    "printer_url": url,
                    "allowed_roots": [str(p) for p in settings.allowed_roots],
                    "receipt_db": str(settings.receipt_db),
                    "enable_uploads": True,
                    "nozzle_diameters": list(settings.nozzle_diameters),
                }
            )
        )
        async with connected(config, tmp_path / "stderr.txt") as session:
            response = await session.call_tool("u1_upload_print", request.model_dump())
            assert response.isError
            assert response.structuredContent["outcome"] == (
                "unknown" if dispatched else "rejected"
            )
            assert response.structuredContent["errors"][0]["code"] == "evidence_changed"
            assert printer.posts == int(dispatched)
