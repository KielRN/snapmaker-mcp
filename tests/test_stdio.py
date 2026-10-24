import asyncio
import json
import os
import subprocess
import sys
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import pytest
from jsonschema import validate
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@contextmanager
def simulated_printer(replies):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path)
            requests.append((self.command, path.path, parse_qs(path.query, keep_blank_values=True)))
            body = json.dumps(replies.get(path.path, {"error": {"message": "bad route"}})).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{http.server_port}", requests
    finally:
        http.shutdown()
        http.server_close()
        thread.join(timeout=2)


async def test_real_mcp_discovery_calls_errors_and_argument_rejection(replies, tmp_path):
    with simulated_printer(replies) as (url, requests):
        params = StdioServerParameters(
            command=sys.executable, args=["-m", "snapmaker_u1_mcp"], env={"U1_PRINTER_URL": url}
        )
        with (tmp_path / "stderr.txt").open("w+", encoding="utf-8") as stderr:
            async with asyncio.timeout(25), stdio_client(params, errlog=stderr) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    discovered = (await session.list_tools()).tools
                    assert {t.name for t in discovered} == {
                        "u1_capabilities",
                        "u1_status",
                        "u1_materials",
                        "u1_prepare_print",
                        "u1_upload_print",
                    }
                    for tool in discovered:
                        assert tool.inputSchema["additionalProperties"] is False
                        assert tool.annotations.readOnlyHint is (tool.name != "u1_upload_print")
                        if tool.name in {"u1_prepare_print", "u1_upload_print"}:
                            response = await session.call_tool(tool.name, {})
                            assert response.isError
                            continue
                        response = await session.call_tool(tool.name, {})
                        assert response.isError is False
                        assert response.structuredContent["outcome"] == "ok"
                        validate(response.structuredContent, tool.outputSchema)
                        assert json.loads(response.content[0].text) == response.structuredContent
                    count = len(requests)
                    response = await session.call_tool(
                        "u1_status", {"url": "http://private.invalid/SECRET"}
                    )
                    assert response.isError is True
                    assert "private.invalid" not in response.content[0].text
                    assert len(requests) == count
                    response = await session.call_tool("u1_start_print", {})
                    assert response.isError is True
                    assert len(requests) == count
                    replies["/printer/objects/query"] = {"error": {"message": "SECRET"}}
                    response = await session.call_tool("u1_status", {})
                    assert response.isError is True
                    assert response.structuredContent["outcome"] == "rejected"
                    assert "SECRET" not in response.content[0].text
                    assert all(method == "GET" for method, _, _ in requests)
            stderr.seek(0)
            logs = stderr.read()
            assert all(v not in logs for v in [url, "SECRET", "private.invalid", "private-printer"])


def test_startup_errors_do_not_echo_local_configuration(tmp_path):
    import subprocess

    env = {**os.environ, "U1_CONFIG_FILE": str(tmp_path / "SECRET-config.json")}
    env.pop("U1_PRINTER_URL", None)
    run = subprocess.run(
        [sys.executable, "-m", "snapmaker_u1_mcp"],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert run.returncode != 0
    assert run.stdout == ""
    assert "SECRET" not in run.stderr
    assert "Traceback" not in run.stderr


@pytest.mark.parametrize(
    "frame",
    [
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "u1_status",
                    "arguments": "SYNTHETIC-SECRET http://private.invalid",
                },
            }
        ),
        "{broken SYNTHETIC-SECRET http://private.invalid",
    ],
)
def test_malformed_stdio_frames_never_echo_peer_payloads(frame):
    env = {**os.environ, "U1_PRINTER_URL": "http://printer.invalid"}
    env.pop("U1_CONFIG_FILE", None)
    run = subprocess.run(
        [sys.executable, "-m", "snapmaker_u1_mcp"],
        env=env,
        input=frame + "\n",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert "SYNTHETIC-SECRET" not in run.stderr + run.stdout
    assert "private.invalid" not in run.stderr + run.stdout
