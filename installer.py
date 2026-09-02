"""Thin PyQt renderer for the BLsetup domain workflow."""

from __future__ import annotations

import sys

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication, QFrame, QLabel, QLineEdit, QMainWindow, QProgressBar, QPushButton, QVBoxLayout, QWidget
except ImportError:  # Allows domain-only Linux checks without a GUI dependency.
    QApplication = None

from blsetup.bridge import InstallController
from blsetup.domain import InstallCommand, InstallEvent, InstallState
from blsetup.tokens import qt_stylesheet


class InstallerWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.controller = InstallController()
        self.controller.subscribe(self.render_event)
        self.setWindowTitle("Bloret Launcher Setup")
        self.resize(720, 460)

        card = QFrame(objectName="card")
        layout = QVBoxLayout(card)
        self.title = QLabel("Bloret Launcher\n安装向导")
        self.title.setStyleSheet("font-size: 26px; font-weight: 600;")
        self.description = QLabel("安全下载、校验并安装启动器。")
        self.path = QLineEdit()
        self.path.setPlaceholderText("安装目录由 Windows 适配器提供")
        self.status = QLabel()
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.start = QPushButton("开始检查 / Start check", objectName="primary")
        self.cancel = QPushButton("取消 / Cancel")
        layout.addWidget(self.title)
        layout.addWidget(self.description)
        layout.addWidget(self.path)
        layout.addWidget(self.status)
        layout.addWidget(self.progress)
        layout.addWidget(self.start)
        layout.addWidget(self.cancel)
        self.setCentralWidget(card)
        self.setStyleSheet(qt_stylesheet())
        self.start.clicked.connect(self.start_flow)
        self.cancel.clicked.connect(lambda: self.controller.dispatch(InstallCommand.CANCEL))
        self.render_event(self.controller.workflow.history[-1])

    def start_flow(self) -> None:
        self.start.setEnabled(False)
        for command in (InstallCommand.CHECK_OK, InstallCommand.MANIFEST_OK, InstallCommand.PREPARED):
            self.controller.dispatch(command)
        self.controller.dispatch(InstallCommand.DOWNLOAD_PROGRESS, progress=0)

    def render_event(self, event: InstallEvent) -> None:
        self.status.setText(event.message)
        if event.progress is not None:
            self.progress.setValue(event.progress)
        if event.state in {InstallState.COMPLETED, InstallState.FAILED, InstallState.CANCELLED}:
            self.start.setEnabled(event.state is InstallState.FAILED)


def main() -> int:
    if QApplication is None:
        raise RuntimeError("PyQt5 is required to run the Windows GUI")
    app = QApplication(sys.argv)
    window = InstallerWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
