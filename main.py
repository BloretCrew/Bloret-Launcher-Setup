from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QWidget
from PyQt5.QtGui import QPixmap, QFont
from qfluentwidgets import FluentWindow, PushButton, SmoothScrollArea, TitleLabel
import sys

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Form")
        self.setGeometry(0, 0, 688, 590)
        self.setStyleSheet("@import url('https://cdn.jsdelivr.net/gh/zhiyiYo/PyQt-Fluent-Widgets@main/qfluentwidgets.qss');")

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(24, 24, 24, 0)

        title_label = TitleLabel("Bloret Launcher 在线安装程序")
        main_layout.addWidget(title_label)

        scroll_area = SmoothScrollArea()
        scroll_area.setStyleSheet("background: transparent; border: none")
        scroll_area.setWidgetResizable(True)

        scroll_contents = QWidget()
        scroll_contents.setGeometry(0, 0, 640, 511)
        scroll_layout = QVBoxLayout(scroll_contents)

        spacer_top = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        scroll_layout.addItem(spacer_top)

        icon_label = QLabel()
        icon_label.setMinimumSize(100, 100)
        icon_label.setMaximumSize(100, 100)
        icon_label.setPixmap(QPixmap("bloret.png"))
        icon_label.setScaledContents(True)
        scroll_layout.addWidget(icon_label)

        launcher_label = QLabel("Bloret Launcher")
        launcher_label.setFont(QFont("", 23))
        scroll_layout.addWidget(launcher_label)

        description_label = QLabel("让我们开始安装吧！这只需要几秒钟时间。")
        scroll_layout.addWidget(description_label)

        spacer_middle = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        scroll_layout.addItem(spacer_middle)

        button_layout = QHBoxLayout()
        spacer_button = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer_button)

        start_button = PushButton("立即开始！")
        start_button.setMinimumSize(300, 0)
        button_layout.addWidget(start_button)

        scroll_layout.addLayout(button_layout)

        scroll_area.setWidget(scroll_contents)
        main_layout.addWidget(scroll_area)

        opengl_widget = QWidget()
        main_layout.addWidget(opengl_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
