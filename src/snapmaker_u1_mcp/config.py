"""Machine-local configuration; invalid values are never included in errors."""

import json
import math
import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Settings:
    printer_url: str = field(repr=False)
    api_key: str | None = field(default=None, repr=False)
    timeout_seconds: float = 5.0
    max_bytes: int = 262144
    allowed_roots: tuple[Path, ...] = field(default=(), repr=False)
    receipt_db: Path | None = field(default=None, repr=False)
    enable_uploads: bool = False
    nozzle_diameters: tuple[float, ...] = ()
    max_gcode_bytes: int = 33554432
    upload_timeout_seconds: float = 30.0
    receipt_ttl_seconds: int = 600

    def __post_init__(self):
        try:
            url = urlsplit(self.printer_url)
            valid = (
                url.scheme in {"http", "https"}
                and url.hostname
                and not url.username
                and not url.password
                and url.path in {"", "/"}
                and not url.query
                and not url.fragment
                and url.port != 0
                and not any(c.isspace() or ord(c) < 32 for c in self.printer_url)
            )
        except (ValueError, TypeError):
            valid = False
        if not valid:
            raise ValueError(
                "Configure a single HTTP(S) printer origin without credentials or path"
            )
        if (
            type(self.timeout_seconds) not in {int, float}
            or not math.isfinite(self.timeout_seconds)
            or not 0 < self.timeout_seconds <= 30
        ):
            raise ValueError("Read timeout must be greater than zero and at most 30 seconds")
        if type(self.max_bytes) is not int or not 1024 <= self.max_bytes <= 1048576:
            raise ValueError("Response limit must be between 1024 and 1048576 bytes")
        if self.api_key is not None and (
            not isinstance(self.api_key, str)
            or not self.api_key
            or not self.api_key.isascii()
            or any(ord(c) < 33 or ord(c) > 126 for c in self.api_key)
        ):
            raise ValueError("API key must be a nonempty printable header value")
        try:
            if type(self.enable_uploads) is not bool:
                raise ValueError
            if (
                type(self.max_gcode_bytes) is not int
                or not 1024 <= self.max_gcode_bytes <= 134217728
            ):
                raise ValueError
            if (
                type(self.upload_timeout_seconds) not in {int, float}
                or not math.isfinite(self.upload_timeout_seconds)
                or not 0 < self.upload_timeout_seconds <= 120
            ):
                raise ValueError
            if (
                type(self.receipt_ttl_seconds) is not int
                or not 1 <= self.receipt_ttl_seconds <= 600
            ):
                raise ValueError
            if self.nozzle_diameters and (
                len(self.nozzle_diameters) != 4
                or any(
                    type(x) not in {int, float} or x not in {0.2, 0.4, 0.6, 0.8}
                    for x in self.nozzle_diameters
                )
            ):
                raise ValueError
            roots = tuple(Path(p).resolve(strict=True) for p in self.allowed_roots)
            if any(not Path(p).is_absolute() for p in self.allowed_roots) or any(
                not p.is_dir() or p.drive.startswith("\\\\") for p in roots
            ):
                raise ValueError
            object.__setattr__(self, "allowed_roots", roots)
            if self.receipt_db is not None:
                db = Path(self.receipt_db)
                if not db.is_absolute() or not db.parent.is_dir():
                    raise ValueError
                object.__setattr__(self, "receipt_db", db.resolve())
            if roots and self.receipt_db is None:
                raise ValueError
            if self.enable_uploads and (not roots or len(self.nozzle_diameters) != 4):
                raise ValueError
        except (OSError, ValueError, TypeError, RuntimeError):
            raise ValueError("Local file preparation/upload configuration is invalid") from None

    @classmethod
    def from_env(cls) -> "Settings":
        """Environment origin overrides an optional ignored local JSON configuration."""
        try:
            config = {}
            if path := os.environ.get("U1_CONFIG_FILE"):
                p = Path(path)
                if p.stat().st_size > 16384:
                    raise ValueError
                config = json.loads(p.read_text(encoding="utf-8-sig"))
                if not isinstance(config, dict) or set(config) - {
                    "printer_url",
                    "timeout_seconds",
                    "max_bytes",
                    "allowed_roots",
                    "receipt_db",
                    "enable_uploads",
                    "nozzle_diameters",
                    "max_gcode_bytes",
                    "upload_timeout_seconds",
                    "receipt_ttl_seconds",
                }:
                    raise ValueError
            return cls(
                printer_url=os.environ.get("U1_PRINTER_URL", config.get("printer_url", "")),
                api_key=os.environ.get("U1_API_KEY"),
                timeout_seconds=config.get("timeout_seconds", 5.0),
                max_bytes=config.get("max_bytes", 262144),
                allowed_roots=tuple(config.get("allowed_roots", [])),
                receipt_db=Path(config["receipt_db"]) if config.get("receipt_db") else None,
                enable_uploads=config.get("enable_uploads", False),
                nozzle_diameters=tuple(config.get("nozzle_diameters", [])),
                max_gcode_bytes=config.get("max_gcode_bytes", 33554432),
                upload_timeout_seconds=config.get("upload_timeout_seconds", 30.0),
                receipt_ttl_seconds=config.get("receipt_ttl_seconds", 600),
            )
        except (OSError, ValueError, TypeError, RecursionError):
            raise ValueError("Local U1 configuration is missing or invalid") from None
