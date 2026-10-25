"""Bounded file access and a deliberately fail-closed plain G-code dialect.

This is inspection, never an interpreter or a slicer. Unknown macros/coordinate
transforms cannot be proved safe and are rejected rather than ignored.
"""

import io
import math
import os
import re
import stat
from pathlib import Path

from pydantic import BaseModel


class ValidationError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class Inspection(BaseModel):
    used_tools: list[int]  # zero-based logical tools
    filament_mm: list[float]
    filament_g: list[float]
    material: list[str]
    nozzle_diameter: list[float]
    filament_diameter: list[float]
    layer_height: float
    nozzle_max: list[float]
    bed_max: float
    bounds_min: list[float]
    bounds_max: list[float]


def _opened_path(fd: int) -> Path:
    """Resolve the opened handle, not just a path checked before open (TOCTOU)."""
    if os.name == "nt":
        import ctypes
        import msvcrt
        from ctypes import wintypes

        get_path = ctypes.WinDLL("kernel32", use_last_error=True).GetFinalPathNameByHandleW
        get_path.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
        get_path.restype = wintypes.DWORD
        buffer = ctypes.create_unicode_buffer(32768)
        length = get_path(msvcrt.get_osfhandle(fd), buffer, len(buffer), 0)
        if not 0 < length < len(buffer):
            raise ValidationError("path_not_allowed")
        value = buffer.value
        if value.startswith("\\\\?\\UNC\\"):
            raise ValidationError("path_not_allowed")
        return Path(value.removeprefix("\\\\?\\")).resolve(strict=True)
    handle = Path(f"/proc/self/fd/{fd}")
    if not handle.exists():
        # No portable handle-path primitive: fail closed on unsupported platforms.
        raise ValidationError("path_verification_unavailable")
    return handle.resolve(strict=True)


def read_file(path: str, roots: tuple[Path, ...], maximum: int) -> tuple[Path, bytes]:
    try:
        requested = Path(path)
        if (
            not requested.is_absolute()
            or requested.drive.startswith("\\\\")
            or (os.name == "nt" and ":" in str(requested)[len(requested.drive) :])
        ):
            raise ValidationError("path_not_allowed")
        canonical = requested.resolve(strict=True)
        if not any(canonical.is_relative_to(root) for root in roots):
            raise ValidationError("path_not_allowed")
        if canonical.suffix.lower() != ".gcode":
            raise ValidationError("unsupported_file")
        fd = os.open(
            canonical,
            os.O_RDONLY
            | getattr(os, "O_BINARY", 0)
            | getattr(os, "O_NONBLOCK", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        with os.fdopen(fd, "rb") as stream:
            opened = _opened_path(stream.fileno())
            if opened != canonical or not any(opened.is_relative_to(root) for root in roots):
                raise ValidationError("path_not_allowed")
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise ValidationError("unsupported_file")
            if before.st_size > maximum:
                raise ValidationError("file_too_large")
            data = stream.read(maximum + 1)
            after = os.fstat(stream.fileno())
            if len(data) > maximum:
                raise ValidationError("file_too_large")
            if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_size,
                after.st_mtime_ns,
                after.st_ctime_ns,
            ):
                raise ValidationError("file_changed")
        return canonical, data
    except (OSError, ValueError, RuntimeError):
        raise ValidationError("path_not_allowed") from None


NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)"
PARAMETER = re.compile(rf"([A-Z])({NUMBER})")
METADATA = {
    "filament used [mm]",
    "filament used [g]",
    "filament_type",
    "nozzle_diameter",
    "filament_diameter",
    "layer_height",
}


def _array(value: str, count: int | None = None) -> list[float]:
    parts = re.split(r"[,;]", value)
    if not 1 <= len(parts) <= 4 or (count is not None and len(parts) != count):
        raise ValidationError("job_requirements")
    if any(not re.fullmatch(NUMBER, x.strip()) for x in parts):
        raise ValidationError("job_requirements")
    result = [float(x) for x in parts]
    if any(not math.isfinite(x) or x < 0 or x > 1e9 for x in result):
        raise ValidationError("job_requirements")
    return result


def _lines(data: bytes):
    for count, raw in enumerate(io.BytesIO(data), 1):
        if count > 500000:
            raise ValidationError("line_limit")
        if len(raw) > 8192:
            raise ValidationError("invalid_gcode")
        try:
            line = raw.decode("utf-8-sig" if count == 1 else "utf-8").rstrip("\r\n")
        except UnicodeError:
            raise ValidationError("invalid_gcode") from None
        if any(ord(c) < 32 and c != "\t" for c in line):
            raise ValidationError("invalid_gcode")
        yield line


def inspect(
    data: bytes,
    volume: tuple[float, float, float] = (270, 270, 270),
    nozzle_limit: float = 300,
    bed_limit: float = 100,
) -> Inspection:
    meta = {}
    for line in _lines(data):
        if line.lstrip().startswith(";"):
            key, separator, value = line.lstrip()[1:].strip().partition("=")
            key = key.strip()
            if separator and key in METADATA:
                if key in meta:
                    raise ValidationError("job_requirements")
                meta[key] = value.strip()
    if set(meta) != METADATA:
        raise ValidationError("job_requirements")
    mm = _array(meta["filament used [mm]"])
    count = len(mm)
    grams = _array(meta["filament used [g]"], count)
    nozzles = _array(meta["nozzle_diameter"], count)
    diameters = _array(meta["filament_diameter"], count)
    materials = re.split(r"[;,]", meta["filament_type"])
    materials = [x.strip().upper() for x in materials]
    layer = _array(meta["layer_height"], 1)[0]
    if (
        len(materials) != count
        or any(x not in {"PLA", "PETG", "ABS", "ASA", "TPU"} for x in materials)
        or any(x not in {0.2, 0.4, 0.6, 0.8} for x in nozzles)
        or any(x != 1.75 for x in diameters)
        or not 0 < layer <= min(nozzles) * 0.8
    ):
        raise ValidationError("job_requirements")
    xyz = [None, None, None]
    homed = False
    low = [math.inf] * 3
    high = [-math.inf] * 3
    absolute = None
    xy_plane = False
    e_absolute = None
    e_position = None
    net_extrusion = [0.0] * count
    extrusion_peak = [0.0] * count
    tool = None
    temps = [0.0] * count
    waited = [False] * count
    nozzle_max = [0.0] * count
    bed_max = 0.0
    extruding = set()
    used = {i for i in range(count) if mm[i] > 0 or grams[i] > 0}
    for line in _lines(data):
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        # This one extended command has a verified, narrow numeric contract.
        # Never pass other macros or arbitrary key/value parameters through.
        parts = code.split()
        if parts[0] == "SET_VELOCITY_LIMIT":
            named = {}
            for part in parts[1:]:
                item = re.fullmatch(rf"([A-Z_]+)=({NUMBER})", part)
                if not item or item[1] in named:
                    raise ValidationError("invalid_gcode")
                value = float(item[2])
                if not math.isfinite(value) or abs(value) > 1e9:
                    raise ValidationError("invalid_gcode")
                named[item[1]] = value
            if set(named) - {"ACCEL", "ACCEL_TO_DECEL"}:
                raise ValidationError("unsupported_parameters")
            if (
                "ACCEL" not in named
                or not 0 < named["ACCEL"] <= 10000
                or not 0 < named.get("ACCEL_TO_DECEL", named["ACCEL"]) <= named["ACCEL"]
            ):
                raise ValidationError("job_requirements")
            continue
        match = re.match(r"([GMT]\d+)(?=\s|[A-Z]|$)", code)
        if not match:
            raise ValidationError("unsupported_command")
        command = match[1]
        tail = code[match.end() :].replace(" ", "").replace("\t", "")
        params = {}
        parameter_text = {}
        offset = 0
        for p in PARAMETER.finditer(tail):
            if p.start() != offset or p[1] in params:
                raise ValidationError("invalid_gcode")
            value = float(p[2])
            if not math.isfinite(value) or abs(value) > 1e9:
                raise ValidationError("invalid_gcode")
            params[p[1]] = value
            parameter_text[p[1]] = p[2]
            offset = p.end()
        if offset != len(tail):
            raise ValidationError("invalid_gcode")
        if set(params) & {"G", "M"}:
            raise ValidationError("invalid_gcode")
        allowed = {
            "G0": "XYZEF",
            "G1": "XYZEF",
            "G2": "XYZEFIJ",
            "G3": "XYZEFIJ",
            "G4": "PS",
            "G17": "",
            "G21": "",
            "G28": "",
            "G90": "",
            "G91": "",
            "G92": "E",
            "M82": "",
            "M83": "",
            "M104": "ST",
            "M109": "ST",
            "M140": "S",
            "M190": "S",
            "M106": "SP",
            "M107": "P",
            "M73": "PR",
            "M204": "S",
            "M400": "",
        }
        if command.startswith("T"):
            if command not in {"T0", "T1", "T2", "T3"} or params or int(command[1:]) >= count:
                raise ValidationError("unsupported_tool")
            tool = int(command[1:])
            e_position = None
            # Matched U1 selection can park/pick and apply XYZ offsets without
            # restoring the old carriage position. Even same-tool early return
            # depends on live grip/park state. Reestablish G-code XYZ explicitly;
            # this does not certify the firmware-owned toolchanger path.
            xyz = [None, None, None]
            continue
        if command not in allowed:
            raise ValidationError("unsupported_command")
        if set(params) - set(allowed[command]):
            raise ValidationError("unsupported_parameters")
        if command in {"G90", "G91"}:
            absolute = command == "G90"
        elif command == "G17":
            # Firmware plane is persistent across files/clients. Establish it
            # here rather than assuming the module's startup default is active.
            xy_plane = True
        elif command in {"M82", "M83"}:
            e_absolute = command == "M82"
        elif command == "G28":
            # Homing is firmware-owned. Do not invent its final coordinates.
            homed = True
            xyz = [None, None, None]
            # U1 Z-probe preprocessing may reselect from physical grip state.
            tool = None
            e_position = None
        elif command == "G92":
            if set(params) != {"E"}:
                raise ValidationError("unsupported_parameters")
            e_position = params["E"]
        elif command in {"M104", "M109", "M140", "M190"}:
            if "S" not in params:
                raise ValidationError("invalid_gcode")
            value = params["S"]
            if not 0 <= value <= (nozzle_limit if command in {"M104", "M109"} else bed_limit):
                raise ValidationError("temperature_limit")
            if command in {"M140", "M190"}:
                bed_max = max(bed_max, value)
            else:
                selected = params.get("T", tool)
                if (
                    selected is None
                    or selected != int(selected)
                    or not 0 <= selected < count
                    or ("T" in params and not re.fullmatch(r"[+-]?\d+", parameter_text["T"]))
                ):
                    raise ValidationError("unsupported_tool")
                selected = int(selected)
                if value > 0:
                    # A heated head needs declared requirements and fresh
                    # material/feed evidence even when it never executes E.
                    used.add(selected)
                temps[selected] = value
                waited[selected] = command == "M109" and value >= 170
                nozzle_max[selected] = max(nozzle_max[selected], value)
        elif command in {"G0", "G1", "G2", "G3"}:
            if absolute is None or ("E" in params and e_absolute is None):
                raise ValidationError("position_unknown")
            if command in {"G2", "G3"}:
                if not xy_plane or not absolute or not homed or any(x is None for x in xyz):
                    raise ValidationError("position_unknown")
                offset_x, offset_y = params.get("I", 0), params.get("J", 0)
                if not (offset_x or offset_y):
                    raise ValidationError("unsupported_parameters")
                # Matched gcode_arcs.py generates XY points on this circle,
                # then appends the exact endpoint (even for unequal radii).
                # Bound the whole circle in O(1), plus the endpoint below.
                # This deliberately overbounds partial sweeps and is independent
                # of firmware segmentation/resolution. Z interpolates linearly.
                radius = math.hypot(offset_x, offset_y)
                for i, center in enumerate((xyz[0] + offset_x, xyz[1] + offset_y)):
                    minimum, maximum = center - radius, center + radius
                    if not 0 <= minimum <= maximum <= volume[i]:
                        raise ValidationError("movement_bounds")
                    low[i] = min(low[i], minimum)
                    high[i] = max(high[i], maximum)
            for i, axis in enumerate("XYZ"):
                if axis in params:
                    if not homed or (not absolute and xyz[i] is None):
                        raise ValidationError("position_unknown")
                    xyz[i] = params[axis] if absolute else xyz[i] + params[axis]
                    if not 0 <= xyz[i] <= volume[i]:
                        raise ValidationError("movement_bounds")
                    low[i] = min(low[i], xyz[i])
                    high[i] = max(high[i], xyz[i])
            if any(x is None for x in xyz):
                raise ValidationError("position_unknown")
            if "F" in params and not 0 < params["F"] <= 60000:
                raise ValidationError("job_requirements")
            if "E" in params:
                # Klipper's G91 affects E even after M82. Tool activation can
                # reset its E base; require an explicit G92 before absolute E.
                absolute_e = absolute and e_absolute
                if absolute_e and e_position is None:
                    raise ValidationError("position_unknown")
                delta = params["E"] - e_position if absolute_e else params["E"]
                e_position = (
                    params["E"]
                    if absolute_e
                    else None
                    if e_position is None
                    else e_position + params["E"]
                )
                if tool is None:
                    raise ValidationError("unsupported_tool")
                net_extrusion[tool] += delta
                extrusion_peak[tool] = max(extrusion_peak[tool], net_extrusion[tool])
                if delta != 0:
                    extruding.add(tool)
                    if not waited[tool] or temps[tool] < 170:
                        raise ValidationError("cold_extrusion")
        elif command in {"M106", "M107"}:
            if (
                "P" in params
                and (params["P"] != 2 or not re.fullmatch(r"[+-]?\d+", parameter_text["P"]))
            ) or (command == "M106" and ("S" not in params or not 0 <= params["S"] <= 255)):
                raise ValidationError("job_requirements")
        elif command == "M73" and (
            "P" not in params
            or not 0 <= params["P"] <= 100
            or not 0 <= params.get("R", 0) <= 1000000
        ):
            raise ValidationError("job_requirements")
        elif command == "M204" and (set(params) != {"S"} or not 0 < params["S"] <= 10000):
            raise ValidationError("job_requirements")
        elif command == "G4" and (not params or any(not 0 <= x <= 60000 for x in params.values())):
            raise ValidationError("job_requirements")
    used |= extruding
    if not used or not extruding or any(mm[i] <= 0 or grams[i] <= 0 for i in used):
        raise ValidationError("consumption_missing")
    if any(extrusion_peak[i] > mm[i] + 0.1 for i in used):
        raise ValidationError("consumption_understated")
    if any(nozzle_max[i] < 170 for i in used) or bed_max <= 0:
        raise ValidationError("job_requirements")
    if any(not math.isfinite(x) for x in [*low, *high]):
        raise ValidationError("position_unknown")
    return Inspection(
        used_tools=sorted(used),
        filament_mm=mm,
        filament_g=grams,
        material=materials,
        nozzle_diameter=nozzles,
        filament_diameter=diameters,
        layer_height=layer,
        nozzle_max=nozzle_max,
        bed_max=bed_max,
        bounds_min=low,
        bounds_max=high,
    )
