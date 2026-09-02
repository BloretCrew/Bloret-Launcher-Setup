"""Application orchestration: domain events plus injected side effects."""

from __future__ import annotations

import json
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from .domain import InstallCommand, InstallEvent, InstallWorkflow
from .manifest import PackageManifest
from .services import atomic_install, download_package, extract_archive, rollback


class Preflight(Protocol):
    def __call__(self, target: Path) -> None: ...


class ManifestFetcher(Protocol):
    def __call__(self, url: str) -> PackageManifest: ...


def fetch_manifest(url: str) -> PackageManifest:
    with urllib.request.urlopen(url, timeout=30) as response:
        return PackageManifest.from_json(response.read())


@dataclass
class RunnerDependencies:
    preflight: Preflight
    manifest_fetcher: ManifestFetcher = fetch_manifest
    downloader: Callable = download_package
    extractor: Callable = extract_archive
    installer: Callable = atomic_install
    rollbacker: Callable = rollback


class InstallRunner:
    """Runs the complete install transaction without importing Qt."""

    def __init__(self, dependencies: RunnerDependencies, emit: Callable[[InstallEvent], None] | None = None) -> None:
        self.dependencies = dependencies
        self.workflow = InstallWorkflow(emit)
        self.cancel_requested = False

    def cancel(self) -> None:
        self.cancel_requested = True

    def run(self, manifest_url: str, target: Path, cache: Path) -> InstallEvent:
        backup = None
        try:
            self.dependencies.preflight(target)
            self.workflow.dispatch(InstallCommand.CHECK_OK)
            manifest = self.dependencies.manifest_fetcher(manifest_url)
            self.workflow.dispatch(InstallCommand.MANIFEST_OK, version=manifest.version)
            target = Path(target)
            cache = Path(cache)
            cache.mkdir(parents=True, exist_ok=True)
            self.workflow.dispatch(InstallCommand.PREPARED)
            package = cache / f"package-{manifest.version}.zip"
            self.dependencies.downloader(
                manifest, package, cancel=lambda: self.cancel_requested,
                progress=lambda value: self.workflow.dispatch(InstallCommand.DOWNLOAD_PROGRESS, progress=value),
                retries=0,
            )
            self.workflow.dispatch(InstallCommand.DOWNLOAD_OK)
            with tempfile.TemporaryDirectory(prefix="blsetup-staging-", dir=cache) as directory:
                staging = Path(directory) / "payload"
                self.dependencies.extractor(package, staging)
                if self.cancel_requested:
                    raise RuntimeError("cancelled")
                self.workflow.dispatch(InstallCommand.VERIFY_OK)
                backup = self.dependencies.installer(staging, target)
            self.workflow.dispatch(InstallCommand.INSTALL_OK)
            return self.workflow.history[-1]
        except Exception as exc:
            if self.cancel_requested or str(exc) == "cancelled":
                if self.workflow.state.value not in {"cancelled", "completed"}:
                    self.workflow.dispatch(InstallCommand.CANCEL, reason="user")
                return self.workflow.history[-1]
            if self.workflow.state.value not in {"failed", "cancelled", "completed"}:
                self.workflow.dispatch(InstallCommand.FAIL, rollback=backup is not None, recoverable=backup is not None, error_id=type(exc).__name__)
            if backup is not None:
                self.dependencies.rollbacker(target, backup)
                if self.workflow.state.value == "rolling_back":
                    self.workflow.dispatch(InstallCommand.ROLLBACK_OK)
            return self.workflow.history[-1]
