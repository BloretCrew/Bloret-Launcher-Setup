import hashlib
import zipfile
from pathlib import Path

import pytest

from blsetup.manifest import ManifestError, PackageManifest, safe_archive_member
from blsetup.services import atomic_install, extract_archive, rollback


def manifest_for(path: Path) -> PackageManifest:
    data = path.read_bytes()
    return PackageManifest.from_mapping({
        "schema_version": 1,
        "version": "1.0.0",
        "package": {"url": path.as_uri(), "size": len(data), "sha256": hashlib.sha256(data).hexdigest()},
    })


def test_manifest_and_safe_paths(tmp_path):
    package = tmp_path / "package.zip"
    package.write_bytes(b"zip")
    assert manifest_for(package).version == "1.0.0"
    with pytest.raises(ManifestError):
        safe_archive_member("../escape.txt")
    with pytest.raises(ManifestError):
        safe_archive_member("C:\\escape.txt")


def test_extract_and_atomic_rollback(tmp_path):
    archive = tmp_path / "package.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("bin/launcher.txt", "new")
    staging = tmp_path / "staging"
    extract_archive(archive, staging)
    target = tmp_path / "install"
    target.mkdir()
    (target / "old.txt").write_text("old")
    backup = atomic_install(staging, target)
    assert (target / "bin/launcher.txt").read_text() == "new"
    rollback(target, backup)
    assert (target / "old.txt").read_text() == "old"
