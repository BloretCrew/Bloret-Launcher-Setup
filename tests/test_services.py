import hashlib
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from blsetup.manifest import ManifestError, PackageManifest, safe_archive_member
from blsetup.services import atomic_install, extract_archive, rollback


class ServicesTests(unittest.TestCase):
    def test_manifest_and_safe_paths(self):
        with TemporaryDirectory() as directory:
            package = Path(directory) / "package.zip"
            package.write_bytes(b"zip")
            data = package.read_bytes()
            manifest = PackageManifest.from_mapping({"schema_version": 1, "version": "1.0.0", "package": {"url": package.as_uri(), "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}})
            self.assertEqual(manifest.version, "1.0.0")
        with self.assertRaises(ManifestError):
            safe_archive_member("../escape.txt")
        with self.assertRaises(ManifestError):
            safe_archive_member("C:\\escape.txt")

    def test_extract_and_atomic_rollback(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "package.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("bin/launcher.txt", "new")
            staging = root / "staging"
            extract_archive(archive, staging)
            target = root / "install"
            target.mkdir()
            (target / "old.txt").write_text("old")
            backup = atomic_install(staging, target)
            self.assertEqual((target / "bin/launcher.txt").read_text(), "new")
            rollback(target, backup)
            self.assertEqual((target / "old.txt").read_text(), "old")


if __name__ == "__main__":
    unittest.main()
