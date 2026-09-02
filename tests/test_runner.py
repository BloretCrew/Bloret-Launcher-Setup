import hashlib
import tempfile
import zipfile
from pathlib import Path

from blsetup.domain import InstallState
from blsetup.manifest import PackageManifest
from blsetup.runner import InstallRunner, RunnerDependencies


def test_runner_integrates_file_manifest_and_install(tmp_path):
    package = tmp_path / "payload.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("launcher.txt", "hello")
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(
        '{"schema_version":1,"version":"2.0.0","package":'
        f'{{"url":"{package.as_uri()}","size":{package.stat().st_size},"sha256":"{digest}"}}}}'
    )
    target = tmp_path / "target"
    cache = tmp_path / "cache"
    dependencies = RunnerDependencies(preflight=lambda _: None)
    runner = InstallRunner(dependencies)
    event = runner.run(manifest_file.as_uri(), target, cache)
    assert event.state is InstallState.COMPLETED
    assert (target / "launcher.txt").read_text() == "hello"


def test_runner_reports_cancel_without_production_url(tmp_path):
    runner = InstallRunner(RunnerDependencies(preflight=lambda _: None))
    runner.cancel()
    event = runner.run("file:///does-not-exist", tmp_path / "target", tmp_path / "cache")
    assert event.state is InstallState.CANCELLED
