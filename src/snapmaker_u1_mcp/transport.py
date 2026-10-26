"""Bounded, non-redirecting, GET-only Moonraker transport."""

import asyncio
import json
import re
from urllib.parse import urlsplit

import httpx

from .config import Settings

EXTRUDERS = ("extruder", "extruder1", "extruder2", "extruder3")
SENSORS = tuple(f"filament_motion_sensor e{i}_filament" for i in range(4))
JOB_BOOLEAN_FIELDS = (
    "time_lapse_camera",
    "auto_bed_leveling",
    "flow_calibrate",
    "shaper_calibrate",
    "auto_replenish_filament",
    "replenish_ignore_color",
    "filament_entangle_detect",
    "end_led_turn_off",
)
JOB_TOOL_FIELDS = ("flow_calib_extruders", "end_unload_filament")
OBJECTS = (
    *EXTRUDERS,
    *SENSORS,
    "print_stats",
    "virtual_sdcard",
    "pause_resume",
    "machine_state_manager",
    "toolhead",
    "gcode_move",
    "bed_mesh",
    "exclude_object",
    "heater_bed",
    "exception_manager",
    "print_task_config",
    "filament_detect",
    "filament_feed left",
    "filament_feed right",
)
OBJECT_FIELDS = {
    "exclude_object": "excluded_objects,current_object,in_excluded_region",
    "pause_resume": "is_paused",
    "machine_state_manager": "main_state,action_code",
    "print_task_config": ",".join(
        (
            "extruder_map_table",
            "extruders_used",
            "filament_type",
            *JOB_BOOLEAN_FIELDS,
            *JOB_TOOL_FIELDS,
            "filament_entangle_sen",
        )
    ),
}


def object_query(names):
    """Use fixed projections for bounded runtime and material reports."""
    return {name: OBJECT_FIELDS.get(name, "") for name in names}


ROUTES = {
    "/printer/info",
    "/server/info",
    "/printer/objects/list",
    "/printer/objects/query",
    "/server/webcams/list",
}

MESSAGES = {
    "timeout": "Printer read timed out; check the local connection and retry the read.",
    "connection_failed": "Printer connection failed; check the configured local endpoint.",
    "authentication_required": "Printer authentication failed; check local API-key configuration.",
    "redirect_refused": "Printer returned a redirect; configure the direct printer origin.",
    "response_too_large": "Printer response exceeded the configured size limit.",
    "unsupported_encoding": "Compressed response refused; configure an uncompressed endpoint.",
    "invalid_response": "Printer returned an invalid response; verify firmware compatibility.",
    "printer_error": "Printer rejected the read; inspect printer state in the supported app.",
    "unsupported": "This read endpoint is unavailable on the printer.",
    "http_error": "Printer HTTP read failed; check printer availability.",
}


class ReadError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(MESSAGES[code])


class Moonraker:
    def __init__(self, settings: Settings, *, transport: httpx.AsyncBaseTransport | None = None):
        self.settings = settings
        self.client = httpx.AsyncClient(
            base_url=settings.printer_url.rstrip("/"),
            timeout=settings.timeout_seconds,
            follow_redirects=False,
            trust_env=False,
            transport=transport,
            headers={
                "Accept-Encoding": "identity",
                **({"X-Api-Key": settings.api_key} if settings.api_key else {}),
            },
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.client.aclose()

    def text(self, value: object) -> str | None:
        """Project only short display labels; never raw paths, messages, or IDs."""
        if not isinstance(value, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9 ._+-]{0,63}", value
        ):
            return None
        if re.search(
            r"password|passwd|token|secret|credential|clientid|session|api.?key", value, re.I
        ):
            return None
        if re.search(r"\d{1,3}(?:\.\d{1,3}){3}", value):
            return None
        host = urlsplit(self.settings.printer_url).hostname
        if (host and host.lower() in value.lower()) or (
            self.settings.api_key and self.settings.api_key in value
        ):
            return None
        return value

    async def get(self, path: str, params: dict[str, str] | None = None) -> dict:
        if path not in ROUTES or (
            params is not None
            and (
                path != "/printer/objects/query"
                or set(params) - set(OBJECTS)
                or any(v != OBJECT_FIELDS.get(k, "") for k, v in params.items())
            )
        ):
            raise ValueError("Only fixed read endpoints and known status objects are allowed")
        try:
            # HTTPX's per-operation timeout does not bound a slow trickling response.
            async with asyncio.timeout(self.settings.timeout_seconds):
                async with self.client.stream("GET", path, params=params) as response:
                    status = response.status_code
                    if status in {401, 403}:
                        raise ReadError("authentication_required")
                    if 300 <= status < 400:
                        raise ReadError("redirect_refused")
                    if status in {404, 405}:
                        raise ReadError("unsupported")
                    if status != 200:
                        raise ReadError("http_error")
                    if (
                        response.headers.get("Content-Encoding", "identity").strip().lower()
                        != "identity"
                    ):
                        raise ReadError("unsupported_encoding")
                    body = bytearray()
                    async for chunk in response.aiter_raw(chunk_size=8192):
                        if len(body) + len(chunk) > self.settings.max_bytes:
                            raise ReadError("response_too_large")
                        body.extend(chunk)
                    try:
                        data = json.loads(body)
                    except (ValueError, UnicodeError, RecursionError):
                        raise ReadError("invalid_response") from None
                    if not isinstance(data, dict):
                        raise ReadError("invalid_response")
                    if "error" in data:
                        raise ReadError("printer_error")
                    if not isinstance(data.get("result"), dict):
                        raise ReadError("invalid_response")
                    return data["result"]
        except (httpx.TimeoutException, TimeoutError):
            raise ReadError("timeout") from None
        except httpx.HTTPError:
            raise ReadError("connection_failed") from None
