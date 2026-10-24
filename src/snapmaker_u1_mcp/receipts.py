"""Private SQLite journal; durable transitions and nonblocking OS serialization."""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .gcode import ValidationError


class Store:
    def __init__(self, path: Path):
        self.connection = sqlite3.connect(path, timeout=0)
        self.connection.execute("PRAGMA synchronous=FULL")
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS operations "
            "(id TEXT PRIMARY KEY, kind TEXT NOT NULL, fingerprint TEXT NOT NULL, "
            "payload TEXT NOT NULL)"
        )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS claims "
            "(preparation TEXT PRIMARY KEY, operation TEXT UNIQUE NOT NULL)"
        )
        self.connection.commit()
        self.lock_path = path.with_suffix(path.suffix + ".lock")

    def close(self):
        self.connection.close()

    @contextmanager
    def exclusive(self):
        with self.lock_path.open("a+b") as lock:
            lock.seek(0)
            try:
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                raise ValidationError("coordinator_busy") from None
            try:
                yield
            finally:
                lock.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(lock, fcntl.LOCK_UN)

    def get(self, operation: str):
        row = self.connection.execute(
            "SELECT kind, fingerprint, payload FROM operations WHERE id=?", (operation,)
        ).fetchone()
        return (row[0], row[1], json.loads(row[2])) if row else None

    def save(self, operation: str, kind: str, fingerprint: str, payload: dict):
        with self.connection:
            self.connection.execute(
                "INSERT INTO operations VALUES (?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
                (operation, kind, fingerprint, json.dumps(payload, allow_nan=False)),
            )

    def begin_upload(self, preparation: str, operation: str, fingerprint: str, payload: dict):
        """Claim and journal the intent in a single durable transaction."""
        try:
            with self.connection:
                self.connection.execute(
                    "INSERT INTO claims VALUES (?, ?)", (preparation, operation)
                )
                self.connection.execute(
                    "INSERT INTO operations VALUES (?, ?, ?, ?)",
                    (operation, "upload", fingerprint, json.dumps(payload)),
                )
        except sqlite3.IntegrityError:
            raise ValidationError("preparation_already_used") from None
