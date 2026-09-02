"""Small Windows integration adapters with deterministic test seams."""

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


class SingleInstanceLock:
    """Portable testable lock; Windows uses exclusive file creation semantics."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._handle = None

    def acquire(self) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._handle = open(self.path, "x", encoding="ascii")
            self._handle.write(str(os.getpid()))
            self._handle.flush()
            return True
        except FileExistsError:
            return False

    def release(self) -> None:
        if self._handle:
            self._handle.close()
            self._handle = None
        self.path.unlink(missing_ok=True)

    def __enter__(self):
        if not self.acquire():
            raise WindowsSupportError("another installer instance is already running")
        return self

    def __exit__(self, *_args) -> None:
        self.release()


class ShortcutAdapter:
    """Boundary for Windows shortcuts; no silent fake shortcut on unsupported hosts."""

    def create(self, target: Path, shortcut: Path, description: str = "Bloret Launcher") -> None:
        if sys.platform != "win32":
            raise WindowsSupportError("shortcut creation requires Windows")
        try:
            import winshell
        except ImportError as exc:
            raise WindowsSupportError("Windows shortcut dependency is unavailable") from exc
        shortcut.parent.mkdir(parents=True, exist_ok=True)
        winshell.CreateShortcut(Path=str(shortcut), Target=str(target), Description=description)
