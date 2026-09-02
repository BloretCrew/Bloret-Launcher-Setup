"""Versioned manifest validation for offline-safe installer operations."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Mapping
from urllib.parse import urlparse


class ManifestError(ValueError):
    """Raised for malformed or unsupported manifests."""


@dataclass(frozen=True)
class PackageManifest:
    schema_version: int
    version: str
    url: str
    size: int
    sha256: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "PackageManifest":
        try:
            schema = int(data["schema_version"])
            version = str(data["version"])
            package = data["package"]
            url = str(package["url"])
            size = int(package["size"])
            sha256 = str(package["sha256"]).lower()
        except (KeyError, TypeError, ValueError) as exc:
            raise ManifestError("manifest fields are incomplete") from exc
        parsed = urlparse(url)
        if schema != 1:
            raise ManifestError(f"unsupported manifest schema: {schema}")
        if not version or parsed.scheme not in {"https", "file"} or (parsed.scheme == "https" and not parsed.netloc):
            raise ManifestError("manifest contains an invalid package URL or version")
        if size < 1 or size > 4 * 1024 * 1024 * 1024:
            raise ManifestError("package size is outside the supported limit")
        if len(sha256) != 64 or any(char not in "0123456789abcdef" for char in sha256):
            raise ManifestError("package sha256 must be a hexadecimal SHA-256 digest")
        return cls(schema, version, url, size, sha256)

    @classmethod
    def from_json(cls, payload: bytes) -> "PackageManifest":
        try:
            data = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ManifestError("manifest is not valid UTF-8 JSON") from exc
        if not isinstance(data, Mapping):
            raise ManifestError("manifest root must be an object")
        return cls.from_mapping(data)


def sha256_file(path: str, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_archive_member(name: str) -> PurePosixPath:
    """Return a normalized relative member path or reject traversal."""
    if "\\" in name or not name or name.startswith("/"):
        raise ManifestError("archive contains an unsafe path")
    path = PurePosixPath(name)
    if path.is_absolute() or ":" in path.parts[0] or any(part in {"", ".", ".."} for part in path.parts):
        raise ManifestError("archive contains a path traversal entry")
    return path
