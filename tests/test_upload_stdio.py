import asyncio
import json
import sys
import threading
from contextlib import asynccontextmanager, contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from uuid import uuid4

import httpx
import pytest
from jsonschema import validate
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


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
