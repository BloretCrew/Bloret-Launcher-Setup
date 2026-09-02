from pathlib import Path

from blsetup.recovery import RecoveryMarker, RecoveryStore
from blsetup.windows import SingleInstanceLock


def test_single_instance_lock(tmp_path):
    path = tmp_path / "installer.lock"
    first, second = SingleInstanceLock(path), SingleInstanceLock(path)
    assert first.acquire()
    assert not second.acquire()
    first.release()
    assert second.acquire()
    second.release()


def test_recovery_marker_round_trip_and_clear(tmp_path):
    store = RecoveryStore(tmp_path / "recovery.json")
    marker = RecoveryMarker("C:/install", "C:/backup", "1.2.3")
    store.write(marker)
    assert store.read() == marker
    store.clear()
    assert store.read() is None
