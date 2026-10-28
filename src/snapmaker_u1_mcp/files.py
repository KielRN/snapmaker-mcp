"""Only generated G-code destinations and the fixed no-start upload endpoint."""

import asyncio
import hashlib
import json
import re

import httpx

from .gcode import ValidationError
from .transport import Moonraker, unique_object

NAME = re.compile(r"u1-[0-9a-f]{32}-[0-9a-f]{64}\.gcode")


class FileTransport:
    def __init__(self, client: Moonraker):
        self.client = client

    async def _request(self, method, path, limit, *, absent=False, **kwargs):
        try:
            async with asyncio.timeout(self.client.settings.upload_timeout_seconds):
                async with self.client.client.stream(
                    method, path, timeout=self.client.settings.upload_timeout_seconds, **kwargs
                ) as response:
                    status = response.status_code
                    if status == 404 and absent:
                        return None
                    if status in {401, 403}:
                        raise ValidationError("authentication_required")
                    if 300 <= status < 400:
                        raise ValidationError("redirect_refused")
                    if status not in ({200} if method == "GET" else {200, 201}):
                        raise ValidationError("http_error")
                    if (
                        response.headers.get("Content-Encoding", "identity").strip().lower()
                        != "identity"
                    ):
                        raise ValidationError("unsupported_encoding")
                    body = bytearray()
                    async for chunk in response.aiter_raw(chunk_size=8192):
                        if len(body) + len(chunk) > limit:
                            raise ValidationError("response_too_large")
                        body.extend(chunk)
                    # Error objects on HTTP 200 must not masquerade as file data.
                    if body.lstrip().startswith(b"{"):
                        try:
                            value = json.loads(body, object_pairs_hook=unique_object)
                        except (ValueError, UnicodeError, RecursionError):
                            value = None
                        if isinstance(value, dict) and "error" in value:
                            raise ValidationError("printer_error")
                    return bytes(body)
        except (httpx.TimeoutException, TimeoutError):
            raise ValidationError("timeout") from None
        except httpx.HTTPError:
            raise ValidationError("connection_failed") from None

    @staticmethod
    def _name(name):
        if not isinstance(name, str) or not NAME.fullmatch(name):
            raise ValidationError("remote_path_invalid")

    async def download(self, name: str, size: int) -> bytes | None:
        self._name(name)
        return await self._request("GET", "/server/files/gcodes/" + name, size + 1024, absent=True)

    async def upload(self, name: str, data: bytes) -> None:
        self._name(name)
        body = await self._request(
            "POST",
            "/server/files/upload",
            self.client.settings.max_bytes,
            data={
                "root": "gcodes",
                "path": "",
                "print": "false",
                "checksum": hashlib.sha256(data).hexdigest(),
            },
            files={"file": (name, data, "application/octet-stream")},
        )
        try:
            result = json.loads(body, object_pairs_hook=unique_object)
        except (ValueError, UnicodeError, RecursionError):
            raise ValidationError("upload_contract") from None
        if (
            not isinstance(result, dict)
            or not isinstance(result.get("item"), dict)
            or result["item"].get("root") != "gcodes"
            or result["item"].get("path") != name
            or result.get("print_started") is not False
            or result.get("print_queued") is not False
        ):
            raise ValidationError("upload_contract")
