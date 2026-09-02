"""Preflight checks with injectable platform probes."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable

from .windows import require_windows_x64


def check_target(target: Path, *, platform_check: Callable[[], None] = require_windows_x64, free_space: Callable[[Path], int] | None = None, minimum_bytes: int = 1) -> None:
    platform_check()
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    probe = free_space or (lambda path: shutil.disk_usage(path).free)
    if probe(target) < minimum_bytes:
        raise OSError("insufficient disk space")
    probe_file = target / ".blsetup-write-test"
    try:
        probe_file.write_bytes(b"ok")
    finally:
        probe_file.unlink(missing_ok=True)
