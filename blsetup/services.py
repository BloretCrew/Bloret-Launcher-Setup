"""Side-effect adapters for package download and transactional installation."""

from __future__ import annotations

import os
import shutil
import tempfile
import time
import urllib.request
import zipfile
from collections.abc import Callable, Iterator
from pathlib import Path

from .manifest import ManifestError, PackageManifest, safe_archive_member, sha256_file


class InstallError(RuntimeError):
    """A controlled, user-displayable installer error."""


class CancelledError(InstallError):
    """Raised when the caller cancels a transfer or installation."""


def download_package(
    manifest: PackageManifest,
    destination: Path,
    *,
    cancel: Callable[[], bool] | None = None,
    progress: Callable[[int], None] | None = None,
    retries: int = 2,
) -> Path:
    """Download to a temporary sibling and atomically publish after size/hash checks."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(retries + 1):
        temporary = destination.with_name(f".{destination.name}.{os.getpid()}.part")
        try:
            with urllib.request.urlopen(manifest.url, timeout=30) as response, open(temporary, "wb") as output:
                total = 0
                while True:
                    if cancel and cancel():
                        raise CancelledError("download cancelled")
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > manifest.size:
                        raise InstallError("download exceeded manifest size")
                    output.write(chunk)
                    if progress:
                        progress(min(99, total * 100 // manifest.size))
            if total != manifest.size or sha256_file(str(temporary)) != manifest.sha256:
                raise InstallError("download size or SHA-256 does not match manifest")
            os.replace(temporary, destination)
            if progress:
                progress(100)
            return destination
        except CancelledError:
            temporary.unlink(missing_ok=True)
            raise
        except Exception as exc:
            temporary.unlink(missing_ok=True)
            if attempt >= retries:
                if isinstance(exc, InstallError):
                    raise
                raise InstallError("package download failed") from exc
            time.sleep(0.2 * (attempt + 1))
    raise AssertionError("unreachable")


def extract_archive(archive: Path, staging: Path, *, max_unpacked_size: int = 8 * 1024 * 1024 * 1024) -> None:
    """Extract a ZIP without traversal, links, or unbounded expansion."""
    staging.mkdir(parents=True, exist_ok=False)
    unpacked = 0
    with zipfile.ZipFile(archive) as source:
        for member in source.infolist():
            relative = safe_archive_member(member.filename)
            if member.is_dir():
                (staging / relative).mkdir(parents=True, exist_ok=True)
                continue
            if member.external_attr >> 16 & 0o170000 == 0o120000:
                raise ManifestError("archive contains a symbolic link")
            unpacked += member.file_size
            if unpacked > max_unpacked_size:
                raise InstallError("archive expands beyond the supported limit")
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open(member) as input_stream, open(target, "xb") as output:
                shutil.copyfileobj(input_stream, output)


def atomic_install(staging: Path, target: Path) -> Path | None:
    """Swap staging into place and retain an adjacent backup for rollback."""
    if not staging.is_dir():
        raise InstallError("staging directory does not exist")
    target.parent.mkdir(parents=True, exist_ok=True)
    backup = target.with_name(f".{target.name}.backup")
    if backup.exists():
        shutil.rmtree(backup)
    if target.exists():
        os.replace(target, backup)
    try:
        os.replace(staging, target)
    except Exception as exc:
        if backup.exists() and not target.exists():
            os.replace(backup, target)
        raise InstallError("atomic installation failed") from exc
    return backup if backup.exists() else None


def rollback(target: Path, backup: Path | None) -> None:
    if target.exists():
        shutil.rmtree(target)
    if backup and backup.exists():
        os.replace(backup, target)


def cleanup_paths(paths: Iterator[Path]) -> None:
    for path in paths:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink(missing_ok=True)
