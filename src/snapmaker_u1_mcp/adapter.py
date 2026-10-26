"""Conservative normalization of the observed U1 HTTP object contract."""

import math
import re
from datetime import UTC, datetime
from typing import Any

from .models import (
    RFID,
    CameraCapability,
    Capabilities,
    Issue,
    Materials,
    MaterialTool,
    Observation,
    PrinterException,
    Status,
    Temperature,
)
from .runtime import normalize_runtime
from .transport import EXTRUDERS, OBJECTS, SENSORS, Moonraker, ReadError, object_query

READ_TOOLS = ["u1_capabilities", "u1_status", "u1_materials"]
FILE_TOOLS = ["u1_prepare_print", "u1_upload_print"]
FUTURE_TOOLS = [
    "u1_list_files",
    "u1_start_print",
    "u1_pause_print",
    "u1_resume_print",
    "u1_cancel_print",
    "u1_camera_status",
    "u1_camera_snapshot",
    "u1_camera_open",
    "u1_camera_close",
]


def now() -> datetime:
    return datetime.now(UTC)


def obj(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def at(value: Any, index: int) -> Any:
    return value[index] if isinstance(value, list) and index < len(value) else None


def boolean(value: Any) -> bool | None:
    return value if type(value) is bool else None


def number(value: Any, maximum: float = 1e12) -> float | None:
    if type(value) in {int, float} and 0 <= value <= maximum and math.isfinite(value):
        return float(value)
    return None


def integer(value: Any, maximum: int = 1000000) -> int | None:
    return value if type(value) is int and 0 <= value <= maximum else None


def choice(value: Any, options: set[str]) -> str | None:
    return value if isinstance(value, str) and value in options else None


def incomplete(code: str) -> Issue:
    return Issue(
        code=code, message="Some fields are missing or unrecognized; verify in the printer app."
    )


class U1Reader:
    def __init__(self, client: Moonraker):
        self.client = client

    async def _snapshot(self, requested: tuple[str, ...]) -> tuple[dict, list[str], float | None]:
        inventory = (await self.client.get("/printer/objects/list")).get("objects")
        if not isinstance(inventory, list) or not all(isinstance(v, str) for v in inventory):
            raise ReadError("invalid_response")
        present = [name for name in requested if name in inventory]
        missing = [name for name in requested if name not in present]
        if not present:
            raise ReadError("unsupported")
        result = await self.client.get("/printer/objects/query", object_query(present))
        if not isinstance(result.get("status"), dict):
            raise ReadError("invalid_response")
        status = result["status"]
        # Only requested objects may affect a result, even if the peer returns extra keys.
        missing += [name for name in present if not isinstance(status.get(name), dict)]
        return (
            {name: obj(status.get(name)) for name in present},
            missing,
            number(result.get("eventtime")),
        )

    @staticmethod
    def _failure(start: datetime, error: ReadError) -> Observation:
        outcome = "rejected" if error.code == "printer_error" else "unavailable"
        return Observation(
            outcome=outcome,
            observation_started_at=start,
            observed_at=now(),
            errors=[Issue(code=error.code, message=str(error))],
        )

    async def status(self) -> Observation[Status]:
        start = now()
        required = (
            *EXTRUDERS,
            "print_stats",
            "virtual_sdcard",
            "pause_resume",
            "toolhead",
            "gcode_move",
            "bed_mesh",
            "exclude_object",
            "heater_bed",
            "exception_manager",
        )
        try:
            info = await self.client.get("/printer/info")
            status, missing, eventtime = await self._snapshot(required)
        except ReadError as error:
            return self._failure(start, error)
        stats = obj(status.get("print_stats"))
        sd = obj(status.get("virtual_sdcard"))
        klipper = choice(info.get("state"), {"ready", "startup", "shutdown", "error"})
        state = choice(
            stats.get("state"), {"standby", "printing", "paused", "complete", "cancelled", "error"}
        )
        active = boolean(sd.get("is_active"))
        runtime = normalize_runtime(status)
        paused = runtime.pause_resume_is_paused
        busy = (
            True
            if state in {"printing", "paused"} or active is True or paused is True
            else (False if state is not None and active is False and paused is False else None)
        )
        raw = obj(status.get("exception_manager")).get("exceptions")
        known = isinstance(raw, list) and len(raw) <= 256
        exceptions = []
        for entry in raw if known else []:
            e = obj(entry)
            level = integer(e.get("level"), 3)
            exceptions.append(
                PrinterException(
                    id=integer(e.get("id")),
                    index=integer(e.get("index")),
                    code=integer(e.get("code")),
                    level=level,
                    blocking=level >= 2 if level in {1, 2, 3} else None,
                )
            )
        # Unknown exceptions block any positive idle assertion.
        clear = known and not exceptions
        blocked = any(e.blocking is True for e in exceptions)
        idle = (
            False
            if busy is True or klipper in {"startup", "shutdown", "error"} or blocked
            else (
                True
                if busy is False
                and klipper == "ready"
                and state in {"standby", "complete", "cancelled"}
                and clear
                else None
            )
        )
        selected = obj(status.get("toolhead")).get("extruder")
        temps = [
            self._temperature(obj(status.get(name)), i + 1) for i, name in enumerate(EXTRUDERS)
        ]
        bed = self._temperature(obj(status.get("heater_bed")))
        layers = obj(stats.get("info"))
        data = Status(
            klipper_state=klipper,
            print_state=state,
            virtual_sd_active=active,
            busy=busy,
            idle=idle,
            progress=number(sd.get("progress"), 1),
            print_duration_seconds=number(stats.get("print_duration")),
            current_layer=integer(layers.get("current_layer")),
            total_layers=integer(layers.get("total_layer")),
            selected_physical_tool=EXTRUDERS.index(selected) + 1 if selected in EXTRUDERS else None,
            temperatures=temps,
            bed=bed,
            exceptions_known=known,
            exceptions=exceptions,
            missing_objects=missing,
            runtime_evidence=runtime,
        )
        partial = (
            bool(missing)
            or bool(data.runtime_evidence.missing_fields)
            or bool(data.runtime_evidence.inconsistencies)
            or klipper is None
            or state is None
            or active is None
            or data.progress is None
            or data.selected_physical_tool is None
            or not known
            or any(e.blocking is None or e.id is None or e.code is None for e in exceptions)
            or any(t.temperature is None or t.target is None for t in [*temps, bed])
        )
        return Observation[Status](
            outcome="partial" if partial else "ok",
            observation_started_at=start,
            observed_at=now(),
            source_eventtime=eventtime,
            data=data,
            errors=[incomplete("incomplete_status")] if partial else [],
        )

    @staticmethod
    def _temperature(raw: dict, physical: int | None = None) -> Temperature:
        return Temperature(
            physical_tool=physical,
            temperature=number(raw.get("temperature"), 500),
            target=number(raw.get("target"), 500),
        )

    async def materials(self) -> Observation[Materials]:
        start = now()
        required = (
            "print_task_config",
            "filament_detect",
            "filament_feed left",
            "filament_feed right",
            *SENSORS,
        )
        try:
            status, missing, eventtime = await self._snapshot(required)
        except ReadError as error:
            return self._failure(start, error)
        config = obj(status.get("print_task_config"))
        detect = obj(status.get("filament_detect"))
        table = config.get("extruder_map_table")
        mapping = [integer(at(table, i), 3) for i in range(32)]
        mapping = [v + 1 if v is not None else None for v in mapping]
        complete = isinstance(table, list) and len(table) == 32 and None not in mapping
        tools = []
        for i, name in enumerate(EXTRUDERS):
            side = "left" if i < 2 else "right"
            feed = obj(obj(status.get(f"filament_feed {side}")).get(f"extruder{i}"))
            sensor = obj(status.get(SENSORS[i]))
            rfid = obj(at(detect.get("info"), i))
            enabled = boolean(sensor.get("enabled"))
            present = boolean(sensor.get("filament_detected"))
            module = boolean(feed.get("module_exist"))
            feed_present = boolean(feed.get("filament_detected"))
            loaded = "unknown"
            if enabled is True and present is False:
                loaded = "not_loaded"
            elif (
                enabled is True
                and present is True
                and module is True
                and feed_present is True
                and feed.get("channel_state") == "load_finish"
                and feed.get("channel_error") == "ok"
                and feed.get("channel_error_state") == "none"
            ):
                loaded = "loaded"
            argb = integer(rfid.get("ARGB_COLOR"), 0xFFFFFFFF)
            color = f"{argb & 0xFFFFFF:06X}{argb >> 24:02X}" if argb is not None else None
            tools.append(
                MaterialTool(
                    physical_tool=i + 1,
                    api_extruder=name,
                    gcode_tool=f"T{i}",
                    used_by_job=boolean(at(config.get("extruders_used"), i)),
                    rfid=RFID(
                        vendor=self.client.text(rfid.get("VENDOR")),
                        material_type=self.client.text(rfid.get("MAIN_TYPE")),
                        sub_type=self.client.text(rfid.get("SUB_TYPE")),
                        color_rgba=color,
                        sku=integer(rfid.get("SKU")),
                        read_state=integer(at(detect.get("state"), i), 255),
                    ),
                    configured_material_type=self.client.text(at(config.get("filament_type"), i)),
                    feed_module_present=module,
                    feed_filament_detected=feed_present,
                    feed_state=self.client.text(feed.get("channel_state")),
                    feed_error=self.client.text(feed.get("channel_error")),
                    toolhead_sensor_enabled=enabled,
                    toolhead_filament_detected=present,
                    loaded_state=loaded,
                )
            )
        data = Materials(
            tools=tools,
            logical_to_physical=mapping,
            mapping_complete=complete,
            missing_objects=missing,
        )
        partial = (
            bool(missing)
            or not complete
            or any(
                t.loaded_state == "unknown" or t.used_by_job is None or t.rfid.read_state is None
                for t in tools
            )
        )
        return Observation[Materials](
            outcome="partial" if partial else "ok",
            observation_started_at=start,
            observed_at=now(),
            source_eventtime=eventtime,
            data=data,
            errors=[incomplete("incomplete_materials")] if partial else [],
        )

    async def capabilities(self) -> Observation[Capabilities]:
        start = now()
        errors = []
        results = {}
        for path in [
            "/printer/info",
            "/server/info",
            "/printer/objects/list",
            "/server/webcams/list",
        ]:
            try:
                results[path] = await self.client.get(path)
            except ReadError as error:
                errors.append(Issue(code=error.code, message=str(error)))
        if not results:
            return Observation[Capabilities](
                outcome="unavailable",
                observation_started_at=start,
                observed_at=now(),
                errors=errors,
            )
        inventory = results.get("/printer/objects/list", {}).get("objects")
        if not isinstance(inventory, list) or not all(isinstance(x, str) for x in inventory):
            inventory = []
            errors.append(incomplete("invalid_inventory"))
        webcams = results.get("/server/webcams/list", {}).get("webcams")
        if not isinstance(webcams, list):
            errors.append(incomplete("invalid_webcam_list"))
        info = results.get("/printer/info", {})
        firmware = self.client.text(info.get("software_version"))
        # Versions contain dots but are not addresses: validate independently of display labels.
        version = info.get("software_version")
        if isinstance(version, str) and re.fullmatch(r"\d+\.\d+\.\d+\.\d+_\d{14}", version):
            firmware = version
        if firmware is None:
            errors.append(incomplete("unknown_firmware"))
        data = Capabilities(
            firmware_version=firmware,
            moonraker_version=self.client.text(
                results.get("/server/info", {}).get("moonraker_version")
            ),
            transports=["moonraker_http"],
            implemented_tools=READ_TOOLS + FILE_TOOLS,
            unimplemented_tools=FUTURE_TOOLS,
            observed_objects=[x for x in OBJECTS if x in inventory],
            missing_objects=[x for x in OBJECTS if x not in inventory],
            camera=CameraCapability(
                configured_webcams=len(webcams) if isinstance(webcams, list) else None
            ),
            file_preparation_configured=bool(self.client.settings.allowed_roots),
            uploads_enabled=self.client.settings.enable_uploads,
        )
        return Observation[Capabilities](
            outcome="partial" if errors or data.missing_objects else "ok",
            observation_started_at=start,
            observed_at=now(),
            data=data,
            errors=errors,
        )
