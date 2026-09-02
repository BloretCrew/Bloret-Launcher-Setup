"""Windows-only integration points kept behind small, testable adapters."""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path


class WindowsSupportError(RuntimeError):
    """Raised when the installer is run outside its supported platform."""


def require_windows_x64() -> None:
    if sys.platform != "win32" or platform.machine().lower() not in {"amd64", "x86_64"}:
        raise WindowsSupportError("Bloret Launcher Setup requires Windows x64")


def default_install_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise WindowsSupportError("APPDATA is unavailable")
    return Path(appdata) / "Bloret-Launcher" / "Bloret-Launcher"


def user_cache_dir() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        raise WindowsSupportError("LOCALAPPDATA is unavailable")
    return Path(local) / "Bloret-Launcher" / "Setup" / "cache"
