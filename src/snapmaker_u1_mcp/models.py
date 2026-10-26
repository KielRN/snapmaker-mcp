"""Public schemas intentionally exclude raw upstream data and machine locations."""

from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field


class Issue(BaseModel):
    code: str
    message: str


T = TypeVar("T")


class Observation(BaseModel, Generic[T]):
    outcome: Literal["ok", "partial", "unavailable", "rejected", "unknown"]
    observation_started_at: datetime
    observed_at: datetime
    source: Literal["live_http"] = "live_http"
    source_eventtime: float | None = None
    errors: list[Issue] = Field(default_factory=list)
    data: T | None = None


class Temperature(BaseModel):
    physical_tool: int | None = None
    temperature: float | None = None
    target: float | None = None


class PrinterException(BaseModel):
    id: int | None = None
    index: int | None = None
    code: int | None = None
    level: int | None = None
    blocking: bool | None = None


class MatrixEvidence(BaseModel):
    rows: int
    columns: int
    sha256: str


class MeshEvidence(BaseModel):
    profile_sha256: str | None = None
    reported_state: Literal["populated", "empty", "unknown"] = "unknown"
    mesh_min: list[float] | None = None
    mesh_max: list[float] | None = None
    probed_matrix: MatrixEvidence | None = None
    mesh_matrix: MatrixEvidence | None = None


class HeadEvidence(BaseModel):
    physical_tool: int
    # Optional defaults deserialize historical receipts, never certify new ones.
    reported_nozzle_diameter: float | None = None
    reported_nozzle_volume_type: Literal["standard", "high_flow"] | None = None
    pressure_advance: float | None = None
    pressure_advance_smooth_time: float | None = None
    # False is an explicit null NAME report, not proof of a detached stepper.
    motion_queue_named: bool | None = None
    motion_queue_physical_tool: int | None = None
    reported_index: int | None = None
    reported_offset: list[float] | None = None
    activating_move: bool | None = None
    park_state: Literal["PARKED", "ACTIVATE", "UNKNOWN"] | None = None
    active_pin: bool | None = None
    park_pin: bool | None = None
    grab_valid_pin: bool | None = None
    activation_report_tool: int | None = None
    activation_status: int | None = None


class ExclusionEvidence(BaseModel):
    excluded_count: int | None = None
    excluded_sha256: str | None = None
    # False means explicit upstream null; None means missing or malformed.
    current_object_present: bool | None = None
    current_object_sha256: str | None = None
    in_excluded_region: bool | None = None
    # No supported status field exposes next_transform or the running chain.
    move_transform_installed: Literal[None] = None


class RuntimeEvidence(BaseModel):
    # Independent saved-pause flag; optional only for historical receipts.
    pause_resume_is_paused: bool | None = None
    homed_axes: str | None = None
    selected_physical_tool: int | None = None
    reported_gripped_tool: int | None = None
    toolhead_position: list[float] | None = None
    axis_minimum: list[float] | None = None
    axis_maximum: list[float] | None = None
    homing_origin: list[float] | None = None
    gcode_move_position: list[float] | None = None
    gcode_position: list[float] | None = None
    absolute_coordinates: bool | None = None
    absolute_extrude: bool | None = None
    speed_factor: float | None = None
    extrude_factor: float | None = None
    tools: list[HeadEvidence]
    mesh: MeshEvidence
    # Default permits historical receipt deserialization; policy prevents reuse.
    exclusion: ExclusionEvidence = Field(default_factory=ExclusionEvidence)
    missing_fields: list[str]
    inconsistencies: list[str]
    atomic: Literal[False] = False
    running_code_attested: Literal[False] = False
    offset_basis: str = "Reported extruder_offset; firmware may return zero fallback."
    unestablished_dependencies: list[str] = Field(
        default_factory=lambda: [
            "gcode_base_position",
            "per_head_homing_origin",
            "offset_calibration_provenance",
            "mesh_fade_and_tool_offset",
            "mesh_lookup_offsets",
            "mesh_calibration_provenance",
            "exclusion_transform_lifecycle",
            "transform_chain",
            "toolchanger_motion_envelope",
            "stepper_trapq_attachment",
            "saved_calibration_k",
            "hidden_feed_thermal_consumption",
            "pause_restore_state",
            "pause_end_callback_effects",
        ]
    )


class RuntimeBinding(BaseModel):
    observation_started_at: datetime
    observed_at: datetime
    source_eventtime_start: float
    source_eventtime_end: float
    data: RuntimeEvidence
    atomic_across_requests: Literal[False] = False


class Status(BaseModel):
    connected: bool = True
    klipper_state: str | None
    print_state: str | None
    virtual_sd_active: bool | None
    busy: bool | None
    idle: bool | None
    progress: float | None
    print_duration_seconds: float | None
    current_layer: int | None
    total_layers: int | None
    selected_physical_tool: int | None
    temperatures: list[Temperature]
    bed: Temperature
    exceptions_known: bool
    exceptions: list[PrinterException]
    missing_objects: list[str]
    runtime_evidence: RuntimeEvidence
    atomic_across_requests: bool = False


class RFID(BaseModel):
    vendor: str | None = None
    material_type: str | None = None
    sub_type: str | None = None
    color_rgba: str | None = None
    sku: int | None = None
    read_state: int | None = None


class MaterialTool(BaseModel):
    physical_tool: int
    api_extruder: str
    gcode_tool: str
    used_by_job: bool | None
    rfid: RFID
    configured_material_type: str | None
    feed_module_present: bool | None
    feed_filament_detected: bool | None
    feed_state: str | None
    feed_error: str | None
    toolhead_sensor_enabled: bool | None
    toolhead_filament_detected: bool | None
    loaded_state: Literal["loaded", "not_loaded", "unknown"]


class Materials(BaseModel):
    tools: list[MaterialTool]
    logical_to_physical: list[int | None]
    mapping_complete: bool
    missing_objects: list[str]
    loaded_state_basis: str = "Feed channel plus enabled toolhead sensor; RFID is identity only."


class CameraCapability(BaseModel):
    availability: Literal["unknown"] = "unknown"
    configured_webcams: int | None = None
    session_transport: Literal["unverified"] = "unverified"
    reason: str = "Webcam listing does not establish U1 camera session or image support."


class Capabilities(BaseModel):
    firmware_version: str | None
    moonraker_version: str | None
    transports: list[str]
    implemented_tools: list[str]
    unimplemented_tools: list[str]
    observed_objects: list[str]
    missing_objects: list[str]
    camera: CameraCapability
    file_preparation_configured: bool = False
    uploads_enabled: bool = False
    compatibility: str = (
        "Reads observed on hardware; uploads simulated only; controls/camera unverified."
    )
