#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                           QStackedWidget, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont

# 尝试导入 QFluentWidgets
try:
    from qfluentwidgets import (FluentWindow, NavigationItemPosition, setTheme, Theme, 
                                SubtitleLabel, PushButton, PrimaryPushButton, 
                                ProgressBar, StateToolTip, InfoBar, InfoBarPosition,
                                LargeTitleLabel, TitleLabel, BodyLabel, StrongBodyLabel,
                                SmoothScrollArea, CardWidget, RadioButton, LineEdit,
                                CheckBox)
    QFLUENT_AVAILABLE = True
except ImportError:
    QFLUENT_AVAILABLE = False
    print("警告: 未安装 QFluentWidgets，将使用标准 Qt 组件")
    # 使用标准 Qt 组件作为后备
    from PyQt6.QtWidgets import (QPushButton, QProgressBar, QLabel, QScrollArea, 
                               QFrame, QRadioButton, QLineEdit, QCheckBox)

# 页面类
try:
    from page1 import Page1
    from page2_1 import Page2_1
    from page2_2 import Page2_2
    from page3 import Page3
except ImportError:
    # 如果页面模块不存在，创建简单的后备页面
    class Page1(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout()
            label = QLabel("欢迎使用 Bloret Launcher 安装向导")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(16)
            label.setFont(font)
            layout.addWidget(label)
            self.setLayout(layout)

    class Page2_1(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout()
            label = QLabel("选择安装路径")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            self.setLayout(layout)

    class Page2_2(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout()
            label = QLabel("选择附加选项")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            self.setLayout(layout)

    class Page3(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout()
            label = QLabel("正在安装...")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            self.setLayout(layout)


class BloretInstaller(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("Bloret Launcher 安装向导")
        
        # 尝试设置窗口图标
        try:
            icon_path = "ui/bloret.ico"
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except:
            pass
            
        self.resize(800, 700)
        
        # 安装配置
        self.install_config = {
            'install_path': '',
            'create_desktop_shortcut': False,
            'create_start_menu_item': False,
            'installation_type': 'quick'  # 'quick' or 'custom'
        }
        
        # 初始化 UI
        self.initUI()
        
    def initUI(self):
        # 创建中央窗口和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建堆叠窗口
        self.stacked_widget = QStackedWidget()
        
        # 创建页面
        self.page1 = Page1(self)
        self.page2_1 = Page2_1(self)
        self.page2_2 = Page2_2(self)
        self.page3 = Page3(self)
        
        # 添加页面到堆叠窗口
        self.stacked_widget.addWidget(self.page1)
        self.stacked_widget.addWidget(self.page2_1)
        self.stacked_widget.addWidget(self.page2_2)
        self.stacked_widget.addWidget(self.page3)
        
        # 添加到主布局
        main_layout.addWidget(self.stacked_widget)
        
        # 连接页面信号
        self.connect_signals()
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
            }
        """)
        
    def connect_signals(self):
        """连接页面信号"""
        # 页面1信号
        if hasattr(self.page1, 'quick_install_button'):
            self.page1.quick_install_button.clicked.connect(self.on_quick_install)
        if hasattr(self.page1, 'custom_installation_button'):
            self.page1.custom_installation_button.clicked.connect(self.on_custom_installation)
        
        # 页面2.1信号
        if hasattr(self.page2_1, 'next_button'):
            self.page2_1.next_button.clicked.connect(self.on_page2_1_next)
        
        # 页面2.2信号
        if hasattr(self.page2_2, 'next_button'):
            self.page2_2.next_button.clicked.connect(self.on_page2_2_next)
        
        # 页面3信号
        if hasattr(self.page3, 'next_button'):
            self.page3.next_button.clicked.connect(self.on_install_complete)
        elif hasattr(self.page3, 'finish_button'):
            self.page3.finish_button.clicked.connect(self.on_install_complete)
        
    def on_quick_install(self):
        """快速安装"""
        self.install_config['installation_type'] = 'quick'
        self.install_config['install_path'] = os.path.expandvars(r'%APPDATA%\Bloret-Launcher\Bloret-Launcher')
        self.stacked_widget.setCurrentWidget(self.page2_2)
        
    def on_custom_installation(self):
        """自定义安装"""
        self.install_config['installation_type'] = 'custom'
        self.stacked_widget.setCurrentWidget(self.page2_1)
        
    def on_page2_1_next(self):
        """页面2.1下一步"""
        # 获取安装路径
        if hasattr(self.page2_1, 'appdata_radio') and self.page2_1.appdata_radio.isChecked():
            self.install_config['install_path'] = os.path.expandvars(r'%APPDATA%\Bloret-Launcher\Bloret-Launcher')
        elif hasattr(self.page2_1, 'custom_radio') and self.page2_1.custom_radio.isChecked():
            if hasattr(self.page2_1, 'custom_path_edit'):
                custom_path = self.page2_1.custom_path_edit.text()
                if not custom_path:
                    self.show_error("请选择安装路径")
                    return
                self.install_config['install_path'] = custom_path
            else:
                self.show_error("无法获取自定义路径")
                return
        else:
            self.install_config['install_path'] = os.path.expandvars(r'%APPDATA%\Bloret-Launcher\Bloret-Launcher')
            
        self.stacked_widget.setCurrentWidget(self.page2_2)
        
    def on_page2_2_next(self):
        """页面2.2下一步"""
        # 获取附加选项
        if hasattr(self.page2_2, 'desktop_shortcut_checkbox'):
            self.install_config['create_desktop_shortcut'] = self.page2_2.desktop_shortcut_checkbox.isChecked()
        if hasattr(self.page2_2, 'start_menu_checkbox'):
            self.install_config['create_start_menu_item'] = self.page2_2.start_menu_checkbox.isChecked()
        
        # 开始安装
        self.start_installation()
        
    def start_installation(self):
        """开始安装过程"""
        self.stacked_widget.setCurrentWidget(self.page3)
        
        # 如果页面3有start_installation方法，调用它
        if hasattr(self.page3, 'start_installation'):
            self.page3.start_installation(self.install_config)
        
    def on_install_complete(self):
        """安装完成"""
        self.show_success("安装完成", "Bloret Launcher 已成功安装！")
        
        # 延迟关闭
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self.close)
        
    def show_error(self, message):
        """显示错误信息"""
        if QFLUENT_AVAILABLE:
            InfoBar.error(
                title='错误',
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        else:
            # 使用标准消息框作为后备
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", message)
            
    def show_success(self, title, message):
        """显示成功信息"""
        if QFLUENT_AVAILABLE:
            InfoBar.success(
                title=title,
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            # 使用标准消息框作为后备
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, title, message)


def main():
    """主函数"""
    # 启用高 DPI 缩放
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    except:
        pass
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置主题
    if QFLUENT_AVAILABLE:
        try:
            setTheme(Theme.AUTO)
        except:
            pass
    
    # 创建安装向导
    installer = BloretInstaller()
    installer.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()