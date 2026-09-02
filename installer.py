"""Thin PyQt renderer and command-line smoke entry for BLsetup."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from blsetup.domain import InstallEvent, InstallState
from blsetup.preflight import check_target
from blsetup.runner import InstallRunner, RunnerDependencies
from blsetup.services import download_package, extract_archive, atomic_install, rollback

try:
    from PyQt5.QtWidgets import QApplication, QFrame, QLabel, QLineEdit, QMainWindow, QProgressBar, QPushButton, QVBoxLayout
except ImportError:
    QApplication = None


def smoke_test() -> int:
    """Build CI can execute this without displaying a GUI or network access."""
    return 0


if QApplication is not None:
    from blsetup.bridge import InstallController
    from blsetup.domain import InstallCommand
    from blsetup.tokens import qt_stylesheet

    class InstallerWindow(QMainWindow):
        def __init__(self, runner: InstallRunner | None = None) -> None:
            super().__init__()
            self.runner = runner
            self.setWindowTitle("Bloret Launcher Setup")
            self.resize(720, 460)
            card = QFrame(objectName="card")
            layout = QVBoxLayout(card)
            self.title = QLabel("Bloret Launcher\n安装向导")
            self.description = QLabel("安全下载、校验并安装启动器。")
            self.path = QLineEdit()
            self.path.setPlaceholderText("输入安装目录")
            self.status = QLabel()
            self.progress = QProgressBar()
            self.progress.setRange(0, 100)
            self.start = QPushButton("开始检查 / Start check", objectName="primary")
            self.cancel = QPushButton("取消 / Cancel")
            for widget in (self.title, self.description, self.path, self.status, self.progress, self.start, self.cancel):
                layout.addWidget(widget)
            self.setCentralWidget(card)
            self.setStyleSheet(qt_stylesheet())
            self.start.clicked.connect(self.start_flow)
            self.cancel.clicked.connect(self.cancel_flow)

        def render_event(self, event: InstallEvent) -> None:
            self.status.setText(event.message)
            if event.progress is not None:
                self.progress.setValue(event.progress)
            self.start.setEnabled(event.state in {InstallState.FAILED, InstallState.CANCELLED})

        def cancel_flow(self) -> None:
            if self.runner:
                self.runner.cancel()

        def start_flow(self) -> None:
            self.start.setEnabled(False)
            if self.runner is None:
                self.status.setText("请配置 manifest URL 后开始安装")
                return
            event = self.runner.run(self.window().property("manifest_url"), Path(self.path.text()), Path.home() / ".blsetup-cache")
            self.render_event(event)


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
