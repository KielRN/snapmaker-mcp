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
                }:
                    raise ValueError
            return cls(
                printer_url=os.environ.get("U1_PRINTER_URL", config.get("printer_url", "")),
                api_key=os.environ.get("U1_API_KEY"),
                timeout_seconds=config.get("timeout_seconds", 5.0),
                max_bytes=config.get("max_bytes", 262144),
            )
        except (OSError, ValueError, TypeError, RecursionError):
            raise ValueError("Local U1 configuration is missing or invalid") from None
