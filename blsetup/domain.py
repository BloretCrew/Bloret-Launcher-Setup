"""UI-independent installation workflow state machine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping


class InstallState(str, Enum):
    CHECKING = "checking"
    RESOLVING = "resolving"
    PREPARING = "preparing"
    DOWNLOADING = "downloading"
    VERIFYING = "verifying"
    INSTALLING = "installing"
    ROLLING_BACK = "rolling_back"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InstallCommand(str, Enum):
    START = "start"
    CHECK_OK = "check_ok"
    MANIFEST_OK = "manifest_ok"
    PREPARED = "prepared"
    DOWNLOAD_PROGRESS = "download_progress"
    DOWNLOAD_OK = "download_ok"
    VERIFY_OK = "verify_ok"
    INSTALL_OK = "install_ok"
    FAIL = "fail"
    CANCEL = "cancel"
    ROLLBACK_OK = "rollback_ok"
    RETRY = "retry"


@dataclass(frozen=True)
class InstallEvent:
    state: InstallState
    message: str
    progress: int | None = None
    recoverable: bool = False
    error_id: str | None = None
    details: Mapping[str, Any] = field(default_factory=dict)


_TRANSITIONS: dict[InstallState, dict[InstallCommand, InstallState]] = {
    InstallState.CHECKING: {InstallCommand.CHECK_OK: InstallState.RESOLVING},
    InstallState.RESOLVING: {InstallCommand.MANIFEST_OK: InstallState.PREPARING},
    InstallState.PREPARING: {InstallCommand.PREPARED: InstallState.DOWNLOADING},
    InstallState.DOWNLOADING: {
        InstallCommand.DOWNLOAD_PROGRESS: InstallState.DOWNLOADING,
        InstallCommand.DOWNLOAD_OK: InstallState.VERIFYING,
    },
    InstallState.VERIFYING: {InstallCommand.VERIFY_OK: InstallState.INSTALLING},
    InstallState.INSTALLING: {InstallCommand.INSTALL_OK: InstallState.COMPLETED},
    InstallState.ROLLING_BACK: {InstallCommand.ROLLBACK_OK: InstallState.FAILED},
    InstallState.FAILED: {InstallCommand.RETRY: InstallState.CHECKING},
}

_MESSAGES = {
    InstallState.CHECKING: "正在检查环境 / Checking environment",
    InstallState.RESOLVING: "正在读取版本清单 / Reading manifest",
    InstallState.PREPARING: "正在准备安装 / Preparing installation",
    InstallState.DOWNLOADING: "正在下载 / Downloading",
    InstallState.VERIFYING: "正在校验 / Verifying package",
    InstallState.INSTALLING: "正在安装 / Installing",
    InstallState.ROLLING_BACK: "正在回滚 / Rolling back",
    InstallState.COMPLETED: "安装完成 / Installation complete",
    InstallState.FAILED: "安装失败 / Installation failed",
    InstallState.CANCELLED: "已取消 / Cancelled",
}


class InvalidTransition(ValueError):
    """Raised when a command is not valid for the current state."""


class InstallWorkflow:
    """Small deterministic state machine; side effects are supplied by callers."""

    def __init__(self, emit: Callable[[InstallEvent], None] | None = None) -> None:
        self.state = InstallState.CHECKING
        self._emit = emit
        self.history: list[InstallEvent] = []
        self._publish()

    @property
    def terminal(self) -> bool:
        return self.state in {
            InstallState.COMPLETED,
            InstallState.FAILED,
            InstallState.CANCELLED,
        }

    def dispatch(self, command: InstallCommand, **details: Any) -> InstallEvent:
        if command == InstallCommand.CANCEL:
            if self.terminal:
                raise InvalidTransition(f"cannot cancel from {self.state.value}")
            self.state = InstallState.CANCELLED
            return self._publish(details=details)
        if command == InstallCommand.FAIL:
            if self.terminal:
                raise InvalidTransition(f"cannot fail from {self.state.value}")
            self.state = InstallState.ROLLING_BACK if details.get("rollback") else InstallState.FAILED
            return self._publish(
                recoverable=bool(details.get("recoverable", True)),
                error_id=details.get("error_id"),
                details=details,
            )
        try:
            next_state = _TRANSITIONS[self.state][command]
        except KeyError as exc:
            raise InvalidTransition(f"{command.value} is not valid from {self.state.value}") from exc
        self.state = next_state
        progress = details.get("progress") if command == InstallCommand.DOWNLOAD_PROGRESS else None
        return self._publish(progress=progress, details=details)

    def _publish(
        self,
        *,
        progress: int | None = None,
        recoverable: bool = False,
        error_id: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> InstallEvent:
        event = InstallEvent(
            state=self.state,
            message=_MESSAGES[self.state],
            progress=progress,
            recoverable=recoverable,
            error_id=error_id,
            details=details or {},
        )
        self.history.append(event)
        if self._emit:
            self._emit(event)
        return event
