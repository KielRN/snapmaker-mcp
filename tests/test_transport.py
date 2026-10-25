import json

import httpx
import pytest

from snapmaker_u1_mcp.config import Settings
from snapmaker_u1_mcp.transport import Moonraker, ReadError


@pytest.mark.parametrize(
    "url",
    [
        "ftp://printer.invalid",
        "http://u:p@printer.invalid",
        "http://printer.invalid/path",
        "http://printer.invalid?token=x",
        "http://printer.invalid#x",
    ],
)
def test_configuration_rejects_non_origin_endpoints_without_echo(url):
    with pytest.raises(ValueError) as error:
        Settings(printer_url=url)
    assert url not in str(error.value)


@pytest.mark.parametrize(
    "case,code",
    [
        ("timeout", "timeout"),
        ("disconnect", "connection_failed"),
        ("redirect", "redirect_refused"),
        ("oversize", "response_too_large"),
        ("bad_json", "invalid_response"),
        ("not_object", "invalid_response"),
        ("no_result", "invalid_response"),
        ("unauthorized", "authentication_required"),
        ("error_200", "printer_error"),
        ("unknown_route", "unsupported"),
    ],
)
async def test_failed_reads_are_bounded_classified_and_redacted(case, code):
    requests = []

    def serve(request):
        requests.append(request)
        assert request.headers["x-api-key"] == "SECRET"
        if case == "timeout":
            raise httpx.ReadTimeout("http://private.invalid SECRET", request=request)
        if case == "disconnect":
            raise httpx.ConnectError("http://private.invalid SECRET", request=request)
        return {
            "redirect": httpx.Response(302, headers={"Location": "http://elsewhere.invalid"}),
            "oversize": httpx.Response(200, stream=httpx.ByteStream(b"a" * 1025)),
            "bad_json": httpx.Response(200, stream=httpx.ByteStream(b"SECRET not-json")),
            "not_object": httpx.Response(200, stream=httpx.ByteStream(b'["SECRET"]')),
            "no_result": httpx.Response(200, stream=httpx.ByteStream(b'{"secret":"SECRET"}')),
            "unauthorized": httpx.Response(401, text="SECRET"),
            "error_200": httpx.Response(
                200, stream=httpx.ByteStream(json.dumps({"error": {"message": "SECRET"}}).encode())
            ),
            "unknown_route": httpx.Response(404, text="SECRET"),
        }[case]

    settings = Settings(printer_url="http://printer.invalid", api_key="SECRET", max_bytes=1024)
    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with pytest.raises(ReadError) as error:
            await client.get("/printer/info")
        assert error.value.code == code
        assert "SECRET" not in str(error.value)
        assert "private.invalid" not in str(error.value)
    assert len(requests) == 1


async def test_no_arbitrary_route_or_query_can_be_fetched():
    def serve(request):
        pytest.fail("Invalid route reached the network")

    async with Moonraker(
        Settings(printer_url="http://printer.invalid"), transport=httpx.MockTransport(serve)
    ) as client:
        for path in ["http://evil.invalid", "/printer/gcode/script", "//evil.invalid/info"]:
            with pytest.raises(ValueError):
                await client.get(path)
        with pytest.raises(ValueError):
            await client.get("/printer/objects/query", {"configfile": ""})
        for fields in ["", "objects", "next_transform", "excluded_objects"]:
            with pytest.raises(ValueError):
                await client.get("/printer/objects/query", {"exclude_object": fields})


async def test_compressed_responses_are_refused_before_decompression():
    import gzip

    payload = gzip.compress(b" " * 1048576)

    def serve(request):
        assert request.headers["accept-encoding"] == "identity"
        return httpx.Response(
            200, headers={"Content-Encoding": "gzip"}, stream=httpx.ByteStream(payload)
        )

    async with Moonraker(
        Settings(printer_url="http://printer.invalid", max_bytes=1024),
        transport=httpx.MockTransport(serve),
    ) as client:
        with pytest.raises(ReadError) as error:
            await client.get("/printer/info")
        assert error.value.code == "unsupported_encoding"
