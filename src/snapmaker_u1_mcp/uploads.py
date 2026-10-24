"""Preparation and no-start upload transactions. Never replay an issued POST."""

import asyncio
import hashlib
import json
import time
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .adapter import U1Reader, now
from .files import FileTransport
from .gcode import Inspection, ValidationError, inspect, read_file
from .models import Issue, Observation
from .receipts import Store
from .transport import Moonraker, ReadError


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


UNAVAILABLE = {
    "coordinator_busy",
    "timeout",
    "connection_failed",
    "authentication_required",
    "unsupported",
    "http_error",
    "uploads_disabled",
    "files_not_configured",
    "response_too_large",
    "unsupported_encoding",
    "invalid_response",
    "redirect_refused",
}


def failure_outcome(code):
    return "unavailable" if code in UNAVAILABLE else "rejected"


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation_id: str

    @field_validator("operation_id", check_fields=False)
    @classmethod
    def operation_uuid(cls, value):
        if str(UUID(value)) != value or UUID(value).version != 4:
            raise ValueError("Use a canonical UUID4")
        return value


class PrepareInput(StrictInput):
    local_path: str = Field(min_length=1, max_length=4096, repr=False)
    plate: int = Field(ge=1, le=1000)
    logical_to_physical: list[int] = Field(min_length=1, max_length=4)

    @field_validator("logical_to_physical")
    @classmethod
    def mapping(cls, value):
        if any(not 1 <= v <= 4 for v in value):
            raise ValueError("Physical tools must be one through four")
        return value


class UploadInput(StrictInput):
    preparation_id: str

    @field_validator("preparation_id")
    @classmethod
    def preparation_uuid(cls, value):
        return cls.operation_uuid(value)


class Preparation(BaseModel):
    preparation_id: str
    plate: int
    sha256: str
    size_bytes: int
    expires_at: datetime
    logical_to_physical: list[int]
    inspection: Inspection
    authorizes_start: Literal[False] = False


class Upload(BaseModel):
    preparation_id: str
    state: Literal["inflight", "unknown", "failed", "verified"]
    remote_path: str  # generated basename relative to the gcodes root only
    sha256: str
    remote_sha256: str | None = None
    response_flags_confirmed: bool = False
    reconciled: bool = False
    expires_at: datetime
    authorizes_start: Literal[False] = False
    hardware_accepted: Literal[False] = False


class Transaction(Observation[Preparation | Upload]):
    source: Literal["local_and_http"] = "local_and_http"
    operation_id: str


def result(operation, start, *, outcome="ok", data=None, code=None):
    return Transaction(
        outcome=outcome,
        operation_id=operation,
        observation_started_at=start,
        observed_at=now(),
        data=data,
        errors=[
            Issue(
                code=code,
                message=(
                    "Upload effect is uncertain; inspect the receipt before a new operation."
                    if outcome == "unknown"
                    else "Blocked; check the error code, file requirements and printer evidence."
                ),
            )
        ]
        if code
        else [],
    )


class Coordinator:
    def __init__(self, client: Moonraker, *, clock=time.time):
        self.client = client
        self.settings = client.settings
        self.reader = U1Reader(client)
        self.files = FileTransport(client)
        self.store = Store(self.settings.receipt_db) if self.settings.receipt_db else None
        self.clock = clock
        self.lock = asyncio.Lock()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.store:
            self.store.close()

    def _policy(self):
        return digest(
            {
                "origin": self.settings.printer_url.rstrip("/"),
                "roots": [str(p) for p in self.settings.allowed_roots],
                "nozzles": self.settings.nozzle_diameters,
                "maximum": self.settings.max_gcode_bytes,
                "validator": 1,
            }
        )

    async def _evidence(self, inspection: Inspection, mapping: list[int]) -> str:
        info = await self.client.get("/printer/info")
        status = await self.reader.status()
        if status.data is None and status.errors:
            raise ValidationError(status.errors[0].code)
        if status.data is None or status.data.idle is not True:
            raise ValidationError("printer_not_idle")
        materials = await self.reader.materials()
        data = materials.data
        if data is None and materials.errors:
            raise ValidationError(materials.errors[0].code)
        if data is None or not data.mapping_complete:
            raise ValidationError("material_evidence_missing")
        if (
            len(mapping) != len(inspection.filament_mm)
            or mapping != data.logical_to_physical[: len(mapping)]
        ):
            raise ValidationError("mapping_changed")
        for logical in inspection.used_tools:
            physical = mapping[logical] - 1
            tool = data.tools[physical]
            if tool.loaded_state != "loaded":
                raise ValidationError("material_not_loaded")
            if (
                tool.rfid.read_state != 0
                or tool.rfid.material_type != inspection.material[logical]
                or tool.configured_material_type != inspection.material[logical]
            ):
                raise ValidationError("material_mismatch")
            if (
                len(self.settings.nozzle_diameters) != 4
                or self.settings.nozzle_diameters[physical] != inspection.nozzle_diameter[logical]
            ):
                raise ValidationError("nozzle_mismatch")
        # Bind previous job identity privately; the public status deliberately omits filenames.
        raw = await self.client.get(
            "/printer/objects/query", {"print_stats": "", "virtual_sdcard": ""}
        )
        snapshot = raw.get("status", {})
        job = snapshot.get("print_stats", {})
        sd = snapshot.get("virtual_sdcard", {})
        if (
            job.get("state") != status.data.print_state
            or sd.get("is_active") is not False
            or not isinstance(job.get("filename"), str)
        ):
            raise ValidationError("printer_not_idle")
        if (
            not isinstance(info.get("hostname"), str)
            or not info["hostname"]
            or not isinstance(info.get("software_version"), str)
        ):
            raise ValidationError("printer_identity_missing")
        return digest(
            {
                "policy": self._policy(),
                "identity": [info["hostname"], info["software_version"]],
                "materials": data.model_dump(),
                "state": status.data.print_state,
                "job": job["filename"],
            }
        )

    async def prepare(self, request: PrepareInput) -> Transaction:
        start = now()
        if not self.store or not self.settings.allowed_roots:
            return result(
                request.operation_id, start, outcome="unavailable", code="files_not_configured"
            )
        async with self.lock:
            try:
                with self.store.exclusive():
                    return await self._prepare(request, start)
            except (ValidationError, ReadError) as error:
                return result(
                    request.operation_id,
                    start,
                    outcome=failure_outcome(error.code),
                    code=error.code,
                )

    async def _prepare(self, request, start):
        path, content = await asyncio.to_thread(
            read_file,
            request.local_path,
            self.settings.allowed_roots,
            self.settings.max_gcode_bytes,
        )
        sha = hashlib.sha256(content).hexdigest()
        fingerprint = digest(
            {**request.model_dump(), "local_path": str(path), "sha": sha, "policy": self._policy()}
        )
        old = self.store.get(request.operation_id)
        if old:
            if old[:2] != ("prepare", fingerprint):
                raise ValidationError("operation_conflict")
            return Transaction.model_validate(old[2]["result"])
        inspection = await asyncio.to_thread(inspect, content)
        evidence = await self._evidence(inspection, request.logical_to_physical)
        expires = self.clock() + self.settings.receipt_ttl_seconds
        receipt = Preparation(
            preparation_id=request.operation_id,
            plate=request.plate,
            sha256=sha,
            size_bytes=len(content),
            expires_at=datetime.fromtimestamp(expires, UTC),
            logical_to_physical=request.logical_to_physical,
            inspection=inspection,
        )
        response = result(request.operation_id, start, data=receipt)
        self.store.save(
            request.operation_id,
            "prepare",
            fingerprint,
            {
                "path": str(path),
                "evidence": evidence,
                "policy": self._policy(),
                "expiry": expires,
                "result": response.model_dump(mode="json"),
            },
        )
        return response

    async def upload(self, request: UploadInput) -> Transaction:
        start = now()
        if not self.store:
            return result(
                request.operation_id, start, outcome="unavailable", code="files_not_configured"
            )
        async with self.lock:
            try:
                with self.store.exclusive():
                    return await self._upload(request, start)
            except (ValidationError, ReadError) as error:
                return result(
                    request.operation_id,
                    start,
                    outcome=failure_outcome(error.code),
                    code=error.code,
                )

    async def _upload(self, request, start):
        fingerprint = digest(request.model_dump())
        old = self.store.get(request.operation_id)
        if old:
            if old[:2] != ("upload", fingerprint):
                raise ValidationError("operation_conflict")
            payload = old[2]
            if payload["state"] not in {"inflight", "unknown"}:
                return Transaction.model_validate(payload["result"])
            # Reconciliation is read-only, including when configuration disables new uploads.
            return await self._verify(request, start, fingerprint, payload, reconciled=True)
        preparation = self.store.get(request.preparation_id)
        if preparation is None or preparation[0] != "prepare":
            response = result(
                request.operation_id, start, outcome="rejected", code="preparation_missing"
            )
            self.store.save(
                request.operation_id,
                "upload",
                fingerprint,
                {"state": "failed", "result": response.model_dump(mode="json")},
            )
            return response
        payload = {"state": "failed", "preparation": preparation[2]}
        try:
            if not self.settings.enable_uploads:
                raise ValidationError("uploads_disabled")
            prep = Preparation.model_validate(preparation[2]["result"]["data"])
            if self.clock() >= preparation[2]["expiry"]:
                raise ValidationError("receipt_expired")
            if preparation[2]["policy"] != self._policy():
                raise ValidationError("evidence_changed")
            _, content = await asyncio.to_thread(
                read_file,
                preparation[2]["path"],
                self.settings.allowed_roots,
                self.settings.max_gcode_bytes,
            )
            if hashlib.sha256(content).hexdigest() != prep.sha256:
                raise ValidationError("file_changed")
            fresh = await self._evidence(prep.inspection, prep.logical_to_physical)
            if fresh != preparation[2]["evidence"]:
                raise ValidationError("evidence_changed")
            name = f"u1-{UUID(request.operation_id).hex}-{prep.sha256}.gcode"
            # Never overwrite any preexisting remote object, even if its bytes match.
            if await self.files.download(name, prep.size_bytes) is not None:
                raise ValidationError("remote_collision")
            # Close the read/POST gap as far as this non-atomic protocol allows.
            if await self._evidence(prep.inspection, prep.logical_to_physical) != fresh:
                raise ValidationError("evidence_changed")
            if self.clock() >= preparation[2]["expiry"]:
                raise ValidationError("receipt_expired")
            data = Upload(
                preparation_id=request.preparation_id,
                state="inflight",
                remote_path=name,
                sha256=prep.sha256,
                expires_at=prep.expires_at,
            )
            payload.update(state="inflight", data=data.model_dump(mode="json"))
            # Commit BEFORE issuing any bytes. Cancellation/process death leaves reconcilable state.
            self.store.begin_upload(
                request.preparation_id, request.operation_id, fingerprint, payload
            )
        except (ValidationError, ReadError) as error:
            response = result(
                request.operation_id, start, outcome=failure_outcome(error.code), code=error.code
            )
            payload["state"] = "failed"
            payload["result"] = response.model_dump(mode="json")
            self.store.save(request.operation_id, "upload", fingerprint, payload)
            return response
        try:
            await self.files.upload(name, content)
            payload["data"]["response_flags_confirmed"] = True
            self.store.save(request.operation_id, "upload", fingerprint, payload)
        except ValidationError as error:
            if error.code in {"timeout", "connection_failed"}:
                return await self._verify(request, start, fingerprint, payload, reconciled=True)
            # An invalid acknowledgment may conceal a write or an unintended start.
            return self._finish(
                request,
                start,
                fingerprint,
                payload,
                "unknown" if error.code != "printer_error" else "rejected",
                error.code,
                terminal=True,
            )
        return await self._verify(request, start, fingerprint, payload)

    async def _verify(self, request, start, fingerprint, payload, reconciled=False):
        data = Upload.model_validate(payload["data"])
        try:
            preparation = payload["preparation"]
            if preparation["policy"] != self._policy():
                raise ValidationError("evidence_changed")
            prep = Preparation.model_validate(preparation["result"]["data"])
            if (
                await self._evidence(prep.inspection, prep.logical_to_physical)
                != preparation["evidence"]
            ):
                raise ValidationError("evidence_changed")
            remote = await self.files.download(data.remote_path, prep.size_bytes)
            if remote is None:
                raise ValidationError("remote_not_observed")
            sha = hashlib.sha256(remote).hexdigest()
            if len(remote) != prep.size_bytes or sha != data.sha256:
                raise ValidationError("hash_mismatch")
            data.remote_sha256 = sha
            data.reconciled = reconciled
            data.state = "verified"
            payload["data"] = data.model_dump(mode="json")
            return self._finish(request, start, fingerprint, payload, "ok")
        except (ValidationError, ReadError) as error:
            return self._finish(
                request,
                start,
                fingerprint,
                payload,
                "unknown",
                error.code,
                terminal=error.code == "hash_mismatch",
            )

    def _finish(self, request, start, fingerprint, payload, outcome, code=None, terminal=False):
        payload["state"] = "verified" if outcome == "ok" else "failed" if terminal else "unknown"
        data = Upload.model_validate(payload["data"])
        data.state = payload["state"]
        response = result(request.operation_id, start, outcome=outcome, data=data, code=code)
        payload["result"] = response.model_dump(mode="json")
        payload["data"] = data.model_dump(mode="json")
        self.store.save(request.operation_id, "upload", fingerprint, payload)
        return response
