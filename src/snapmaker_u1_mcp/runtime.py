"""Bounded reported coordinate evidence, never a calibrated movement certificate."""

import hashlib
import json
import math

from .models import ExclusionEvidence, HeadEvidence, MatrixEvidence, MeshEvidence, RuntimeEvidence
from .transport import EXTRUDERS

RUNTIME_OBJECTS = (
    "toolhead",
    "gcode_move",
    *EXTRUDERS,
    "bed_mesh",
    "exclude_object",
    "pause_resume",
)


def signed_number(value):
    # Exact types exclude booleans; the bound is a normalization/resource policy,
    # not a physical movement limit. Negative coordinates/offsets are legitimate.
    if type(value) in {int, float} and -1e6 <= value <= 1e6 and math.isfinite(value):
        return float(value)
    return None


def vector(value, length):
    if not isinstance(value, list) or len(value) != length:
        return None
    result = [signed_number(v) for v in value]
    return result if None not in result else None


def hashed(value):
    return hashlib.sha256(
        json.dumps(value, allow_nan=False, separators=(",", ":")).encode()
    ).hexdigest()


def matrix(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 128:
        return None
    if not isinstance(value[0], list) or len(value[0]) > 128:
        return None
    columns = len(value[0])
    if columns == 0 and value != [[]]:
        return None
    rows = [vector(row, columns) for row in value]
    if any(row is None for row in rows):
        return None
    return MatrixEvidence(rows=len(rows), columns=columns, sha256=hashed(rows))


def physical(value):
    return EXTRUDERS.index(value) + 1 if value in EXTRUDERS else None


def normalize_runtime(snapshot: dict) -> RuntimeEvidence:
    missing, inconsistent = [], []

    def raw(name):
        value = snapshot.get(name)
        return value if isinstance(value, dict) else {}

    def field(name, key, normalize):
        value = normalize(raw(name).get(key))
        if value is None:
            missing.append(f"{name}.{key}")
        return value

    def boolean(v):
        return v if type(v) is bool else None

    def index(v):
        return v if type(v) is int and 0 <= v <= 3 else None

    def positive(v):
        value = signed_number(v)
        return value if value is not None and value > 0 else None

    def bounded(v, low, high):
        value = signed_number(v)
        return value if value is not None and low <= value <= high else None

    def nozzle(v):
        value = signed_number(v)
        return value if value in {0.2, 0.4, 0.6, 0.8} else None

    def homed(v):
        return (
            v if isinstance(v, str) and v in {"", "x", "y", "z", "xy", "xz", "yz", "xyz"} else None
        )

    def label(v):
        return isinstance(v, str) and len(v) <= 256

    def excluded(v):
        if (
            isinstance(v, list)
            and len(v) <= 1024
            and all(label(name) for name in v)
            and len(set(v)) == len(v)
        ):
            return sorted(v)
        return None

    names = field("exclude_object", "excluded_objects", excluded)
    current = raw("exclude_object").get("current_object")
    current_known = "current_object" in raw("exclude_object") and (
        current is None or label(current)
    )
    if not current_known:
        missing.append("exclude_object.current_object")
    exclusion = ExclusionEvidence(
        excluded_count=len(names) if names is not None else None,
        excluded_sha256=hashed(names) if names is not None else None,
        current_object_present=(current is not None) if current_known else None,
        current_object_sha256=hashed(current) if current_known and current is not None else None,
        in_excluded_region=field("exclude_object", "in_excluded_region", boolean),
    )
    # Region state is updated by moves and can lag START/END/RESET. Neither it
    # nor an empty exclusion list establishes transform installation/removal.

    heads = []
    for i, name in enumerate(EXTRUDERS):
        queue = raw(name).get("motion_queue")
        queue_known = "motion_queue" in raw(name) and (
            queue is None or (isinstance(queue, str) and queue in EXTRUDERS)
        )
        if not queue_known:
            missing.append(f"{name}.motion_queue")
        report = raw(name).get("real_extruder_stats")
        tool, status = None, None
        if isinstance(report, list) and len(report) == 2 and type(report[1]) is int:
            tool = physical(report[0])
            if report[1] in {0, 1} and tool is not None:
                status = report[1]
            elif report[1] == 2 and report[0] == "unknown extruder":
                status = 2
        if status is None:
            missing.append(f"{name}.real_extruder_stats")
        heads.append(
            HeadEvidence(
                physical_tool=i + 1,
                reported_nozzle_diameter=field(name, "nozzle_diameter", nozzle),
                reported_nozzle_volume_type=field(
                    name,
                    "nozzle_volume_type",
                    lambda v: v if isinstance(v, str) and v in {"standard", "high_flow"} else None,
                ),
                pressure_advance=field(name, "pressure_advance", lambda v: bounded(v, 0, 1e6)),
                pressure_advance_smooth_time=field(
                    name, "smooth_time", lambda v: bounded(v, 0, 0.2)
                ),
                motion_queue_named=(queue is not None) if queue_known else None,
                motion_queue_physical_tool=physical(queue) if queue_known else None,
                reported_index=field(name, "extruder_index", index),
                reported_offset=field(name, "extruder_offset", lambda v: vector(v, 3)),
                activating_move=field(name, "activating_move", boolean),
                park_state=field(
                    name,
                    "state",
                    lambda v: (
                        v if isinstance(v, str) and v in {"PARKED", "ACTIVATE", "UNKNOWN"} else None
                    ),
                ),
                active_pin=field(name, "active_pin", boolean),
                park_pin=field(name, "park_pin", boolean),
                grab_valid_pin=field(name, "grab_valid_pin", boolean),
                activation_report_tool=tool,
                activation_status=status,
            )
        )
    if any(h.reported_index is not None and h.reported_index != i for i, h in enumerate(heads)):
        inconsistent.append("extruder_index_mismatch")
    reports = {(h.activation_report_tool, h.activation_status) for h in heads}
    gripped = None
    selected = field("toolhead", "extruder", physical)
    if all(h.activation_status is not None for h in heads):
        if len(reports) != 1:
            inconsistent.append("activation_reports_disagree")
        else:
            tool, status = next(iter(reports))
            states = [h.park_state for h in heads]
            if status == 0:
                if (
                    states.count("ACTIVATE") == 1
                    and states.count("PARKED") == 3
                    and states[tool - 1] == "ACTIVATE"
                ):
                    gripped = tool
                else:
                    inconsistent.append("activation_state_mismatch")
                if tool != selected:
                    inconsistent.append("selection_report_mismatch")
            elif status == 1:
                if states != ["PARKED"] * 4:
                    inconsistent.append("activation_state_mismatch")
                # The matched source reports toolhead's selected name in the
                # all-parked case; it still does not imply a gripped tool.
                if tool != selected:
                    inconsistent.append("selection_report_mismatch")
    mesh = MeshEvidence(
        profile_sha256=field(
            "bed_mesh",
            "profile_name",
            lambda v: hashed(v) if isinstance(v, str) and len(v) <= 256 else None,
        ),
        mesh_min=field("bed_mesh", "mesh_min", lambda v: vector(v, 2)),
        mesh_max=field("bed_mesh", "mesh_max", lambda v: vector(v, 2)),
        probed_matrix=field("bed_mesh", "probed_matrix", matrix),
        mesh_matrix=field("bed_mesh", "mesh_matrix", matrix),
    )
    if (
        mesh.profile_sha256 is not None
        and mesh.mesh_matrix
        and mesh.probed_matrix
        and mesh.mesh_min is not None
        and mesh.mesh_max is not None
    ):
        empty = raw("bed_mesh").get("profile_name") == ""
        widths = [mesh.mesh_matrix.columns, mesh.probed_matrix.columns]
        if empty and widths == [0, 0] and mesh.mesh_min == mesh.mesh_max == [0, 0]:
            mesh.reported_state = "empty"
        elif not empty and all(w > 0 for w in widths):
            mesh.reported_state = "populated"
        else:
            inconsistent.append("mesh_state_mismatch")
    data = dict(
        pause_resume_is_paused=field("pause_resume", "is_paused", boolean),
        homed_axes=field("toolhead", "homed_axes", homed),
        selected_physical_tool=selected,
        reported_gripped_tool=gripped,
        toolhead_position=field("toolhead", "position", lambda v: vector(v, 4)),
        axis_minimum=field("toolhead", "axis_minimum", lambda v: vector(v, 4)),
        axis_maximum=field("toolhead", "axis_maximum", lambda v: vector(v, 4)),
        homing_origin=field("gcode_move", "homing_origin", lambda v: vector(v, 4)),
        gcode_move_position=field("gcode_move", "position", lambda v: vector(v, 4)),
        gcode_position=field("gcode_move", "gcode_position", lambda v: vector(v, 4)),
        absolute_coordinates=field("gcode_move", "absolute_coordinates", boolean),
        absolute_extrude=field("gcode_move", "absolute_extrude", boolean),
        speed_factor=field("gcode_move", "speed_factor", positive),
        extrude_factor=field("gcode_move", "extrude_factor", positive),
    )
    return RuntimeEvidence(
        **data,
        tools=heads,
        mesh=mesh,
        exclusion=exclusion,
        missing_fields=missing,
        inconsistencies=inconsistent,
    )
