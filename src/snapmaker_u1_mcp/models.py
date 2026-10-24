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
    compatibility: str = "Read observations only; mutations and camera sessions remain unverified."
