"""Crash/restart recovery marker with atomic JSON writes."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RecoveryMarker:
    target: str
    backup: str | None
    version: str


class RecoveryStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def write(self, marker: RecoveryMarker) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(marker.__dict__, ensure_ascii=False), encoding="utf-8")
        os.replace(temporary, self.path)

    def read(self) -> RecoveryMarker | None:
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return RecoveryMarker(str(data["target"]), data.get("backup"), str(data["version"]))
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def clear(self) -> None:
        self.path.unlink(missing_ok=True)
