"""Thin PyQt renderer and command-line smoke entry for BLsetup."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from blsetup.domain import InstallEvent, InstallState
from blsetup.runner import InstallRunner
from blsetup.windows import default_install_dir, user_cache_dir

try:
    from PyQt5.QtWidgets import QApplication, QFrame, QLabel, QLineEdit, QMainWindow, QProgressBar, QPushButton, QVBoxLayout
except ImportError:
    QApplication = None


def smoke_test() -> int:
    """Build CI can execute this without displaying a GUI or network access."""
    return 0


if QApplication is not None:
    from blsetup.tokens import qt_stylesheet

    class InstallerWindow(QMainWindow):
        def __init__(self, runner: InstallRunner | None = None) -> None:
            super().__init__()
            self.runner = runner
            self.setWindowTitle("Bloret Launcher Setup")
            self.resize(720, 520)
            card = QFrame(objectName="card")
            layout = QVBoxLayout(card)
            self.title = QLabel("Bloret Launcher\n安装向导")
            self.title.setStyleSheet("font-size: 26px; font-weight: 600;")
            self.description = QLabel("安全下载、校验并安装启动器。")
            self.manifest_url = QLineEdit()
            self.manifest_url.setPlaceholderText("Manifest URL (https://… 或离线 file://…)")
            self.path = QLineEdit()
            self.path.setPlaceholderText("安装目录")
            self.status = QLabel()
            self.progress = QProgressBar()
            self.progress.setRange(0, 100)
            self.start = QPushButton("开始安装 / Install", objectName="primary")
            self.cancel = QPushButton("取消 / Cancel")
            for widget in (self.title, self.description, self.manifest_url, self.path, self.status, self.progress, self.start, self.cancel):
                layout.addWidget(widget)
            self.setCentralWidget(card)
            self.setStyleSheet(qt_stylesheet())
            self._set_default_path()
            self.start.clicked.connect(self.start_flow)
            self.cancel.clicked.connect(self.cancel_flow)

        def _set_default_path(self) -> None:
            try:
                self.path.setText(str(default_install_dir()))
            except Exception:
                self.path.setPlaceholderText("Windows x64 默认安装目录不可用")

        def render_event(self, event: InstallEvent) -> None:
            self.status.setText(event.message)
            if event.progress is not None:
                self.progress.setValue(event.progress)
            self.start.setEnabled(event.state in {InstallState.FAILED, InstallState.CANCELLED})

        def cancel_flow(self) -> None:
            if self.runner:
                self.runner.cancel()

        def start_flow(self) -> None:
            if self.runner is None:
                self.status.setText("安装核心未配置 / Installer core unavailable")
                return
            self.start.setEnabled(False)
            self.runner.run(self.manifest_url.text().strip(), Path(self.path.text().strip()), user_cache_dir())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args(argv)
    if args.smoke_test:
        return smoke_test()
    if QApplication is None:
        raise RuntimeError("PyQt5 is required to run the Windows GUI")
    app = QApplication(sys.argv)
    window = InstallerWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
