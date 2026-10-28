"""Conflicting JSON members must not become trustworthy printer evidence."""

import json
from dataclasses import replace
from uuid import uuid4

import httpx
import pytest
from test_uploads import prepared

from snapmaker_u1_mcp import uploads
from snapmaker_u1_mcp.adapter import U1Reader
from snapmaker_u1_mcp.transport import Moonraker, ReadError


@pytest.mark.parametrize(
    "body",
    [
        b'{"result": {"state": "shutdown"}, "result": {"state": "ready"}}',
        b'{"result": {"state": "shutdown", "state": "ready"}}',
        b'{"result": {"state": "ready", "st\\u0061te": "ready"}}',
        b'{"result": {"unused": [{"flag": true, "flag": false}]}}',
    ],
)
async def test_duplicate_members_at_every_depth_are_invalid(body):
    from snapmaker_u1_mcp.config import Settings

    def serve(request):
        return httpx.Response(200, stream=httpx.ByteStream(body))

    async with Moonraker(
        Settings(printer_url="http://printer.invalid"), transport=httpx.MockTransport(serve)
    ) as client:
        with pytest.raises(ReadError) as error:
            await client.get("/printer/info")
        assert error.value.code == "invalid_response"


async def test_equal_keys_in_separate_objects_are_valid():
    from snapmaker_u1_mcp.config import Settings

    body = b'{"result": {"heads": [{"target": 0}, {"target": 0}]}}'
    async with Moonraker(
        Settings(printer_url="http://printer.invalid"),
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, stream=httpx.ByteStream(body))
        ),
    ) as client:
        assert await client.get("/printer/info") == {"heads": [{"target": 0}, {"target": 0}]}


async def test_conflicting_active_flag_cannot_prove_idle_or_allow_upload(setup_upload):
    settings, printer, file = setup_upload
    ambiguous = False

    async def serve(request):
        response = await printer.serve(request)
        if ambiguous and request.url.path == "/printer/objects/query":
            body = (await response.aread()).replace(
                b'"is_active": false', b'"is_active": true, "is_active": false'
            )
            return httpx.Response(200, stream=httpx.ByteStream(body))
        return response

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with uploads.Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            assert prep.outcome == "ok"
            ambiguous = True
            status = await U1Reader(client).status()
            assert status.outcome == "unavailable"
            assert status.data is None
            assert status.errors[0].code == "invalid_response"
            result = await coordinator.upload(
                uploads.UploadInput(
                    operation_id=str(uuid4()), preparation_id=prep.data.preparation_id
                )
            )
            assert result.outcome == "unavailable"
            assert result.errors[0].code == "invalid_response"
            assert printer.posts == 0


@pytest.mark.parametrize("member", ["print_started", "print_queued", "root", "path"])
async def test_ambiguous_upload_ack_is_terminal_and_never_replayed(setup_upload, member):
    settings, printer, file = setup_upload

    async def serve(request):
        response = await printer.serve(request)
        if request.method == "POST":
            body = await response.aread()
            if member in {"print_started", "print_queued"}:
                marker = f'"{member}": false'.encode()
                body = body.replace(marker, f'"{member}": true, '.encode() + marker)
            else:
                marker = f'"{member}": '.encode()
                body = body.replace(marker, marker + b'"private-unexpected", ' + marker)
            return httpx.Response(201, stream=httpx.ByteStream(body))
        return response

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with uploads.Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            request = uploads.UploadInput(
                operation_id=str(uuid4()), preparation_id=prep.data.preparation_id
            )
            result = await coordinator.upload(request)
            assert result.outcome == "unknown"
            assert result.data.state == "failed"
            assert result.data.response_flags_confirmed is False
            assert result.errors[0].code == "upload_contract"
            assert "private-unexpected" not in result.model_dump_json()
            assert printer.posts == 1
        with uploads.Coordinator(client) as restarted:
            assert await restarted.upload(request) == result
            assert printer.posts == 1


@pytest.mark.parametrize("private", ["full_key", "substring_key", "host_prefix", "oversize"])
async def test_version_shape_does_not_bypass_configured_secret_redaction(replies, private):
    from snapmaker_u1_mcp.config import Settings

    version = "2.0.0.205_20260914173503"
    settings = Settings(printer_url="http://printer.invalid")
    if private == "full_key":
        settings = replace(settings, api_key=version)
    elif private == "substring_key":
        settings = replace(settings, api_key="20260914173503")
    elif private == "host_prefix":
        settings = replace(settings, printer_url="http://2.0.0.205")
    else:
        version = "2.0.0." + "2" * 60 + "_20260914173503"
        replies["/printer/info"]["result"]["software_version"] = version

    def serve(request):
        return httpx.Response(
            200, stream=httpx.ByteStream(json.dumps(replies[request.url.path]).encode())
        )

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        result = await U1Reader(client).capabilities()
        assert result.outcome == "partial"
        assert result.data.firmware_version is None
        assert version not in result.model_dump_json()


async def test_ambiguous_reconciliation_read_stays_unknown_then_recovers_without_post(setup_upload):
    settings, printer, file = setup_upload
    ambiguous = False

    async def serve(request):
        response = await printer.serve(request)
        if ambiguous and request.url.path == "/printer/objects/query":
            body = (await response.aread()).replace(
                b'"is_active": false', b'"is_active": true, "is_active": false'
            )
            return httpx.Response(200, stream=httpx.ByteStream(body))
        return response

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with uploads.Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            request = uploads.UploadInput(
                operation_id=str(uuid4()), preparation_id=prep.data.preparation_id
            )
            printer.failure = "lost_without_write"
            first = await coordinator.upload(request)
            assert first.outcome == "unknown"
            printer.files[first.data.remote_path] = file.read_bytes()
        printer.failure = None
        ambiguous = True
        with uploads.Coordinator(client) as restarted:
            result = await restarted.upload(request)
            assert result.outcome == "unknown"
            assert result.errors[0].code == "invalid_response"
            assert printer.posts == 1
        ambiguous = False
        with uploads.Coordinator(client) as restarted:
            result = await restarted.upload(request)
            assert result.outcome == "ok"
            assert result.data.reconciled is True
            assert result.data.response_flags_confirmed is False
            assert printer.posts == 1


@pytest.mark.parametrize("boundary", ["read", "ack"])
async def test_actual_mcp_rejects_ambiguous_evidence_and_preserves_terminal_result(
    setup_upload, tmp_path, boundary
):
    from test_upload_stdio import connected, file_printer

    settings, printer, file = setup_upload
    original = printer.serve
    ambiguous = False

    async def serve(request):
        response = await original(request)
        if ambiguous:
            body = await response.aread()
            if boundary == "read" and request.url.path == "/printer/objects/query":
                body = body.replace(b'"is_active": false', b'"is_active": true, "is_active": false')
            if boundary == "ack" and request.method == "POST":
                body = body.replace(
                    b'"print_started": false', b'"print_started": true, "print_started": false'
                )
            return httpx.Response(response.status_code, content=body)
        return response

    printer.serve = serve
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
            prep = await session.call_tool(
                "u1_prepare_print",
                {
                    "operation_id": str(uuid4()),
                    "local_path": str(file),
                    "plate": 1,
                    "logical_to_physical": [2, 1, 4, 3],
                },
            )
            assert prep.isError is False
            arguments = {
                "operation_id": str(uuid4()),
                "preparation_id": prep.structuredContent["data"]["preparation_id"],
            }
            ambiguous = True
            if boundary == "read":
                status = await session.call_tool("u1_status", {})
                assert status.isError is True
                assert status.structuredContent["data"] is None
            result = await session.call_tool("u1_upload_print", arguments)
            assert result.isError is True
            expected_code = "invalid_response" if boundary == "read" else "upload_contract"
            assert result.structuredContent["errors"][0]["code"] == expected_code
            assert printer.posts == (0 if boundary == "read" else 1)
        ambiguous = False
        async with connected(config, tmp_path / "stderr2.txt") as session:
            repeated = await session.call_tool("u1_upload_print", arguments)
            assert repeated.structuredContent == result.structuredContent
            assert printer.posts == (0 if boundary == "read" else 1)
