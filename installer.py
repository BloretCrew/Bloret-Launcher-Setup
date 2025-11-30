#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QIcon

from qfluentwidgets import (FluentWindow, NavigationItemPosition, setTheme, Theme, 
                            SubtitleLabel, PushButton, PrimaryPushButton, 
                            ProgressBar, StateToolTip, InfoBar, InfoBarPosition)

from page1 import Page1
from page2_1 import Page2_1
from page2_2 import Page2_2
from page3 import Page3


class BloretInstaller(FluentWindow):
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("Bloret Launcher 安装向导")
        self.setWindowIcon(QIcon("ui/bloret.ico"))
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
        
        # 设置中央窗口
        self.setCentralWidget(self.stacked_widget)
        
        # 连接页面信号
        self.connect_signals()
        
    def connect_signals(self):
        # 页面1信号
        self.page1.quick_install_button.clicked.connect(self.on_quick_install)
        self.page1.custom_installation_button.clicked.connect(self.on_custom_installation)
        
        # 页面2.1信号
        self.page2_1.next_button.clicked.connect(self.on_page2_1_next)
        
        # 页面2.2信号
        self.page2_2.next_button.clicked.connect(self.on_page2_2_next)
        
        # 页面3信号
        self.page3.next_button.clicked.connect(self.on_install_complete)
        
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
        if self.page2_1.appdata_radio.isChecked():
            self.install_config['install_path'] = os.path.expandvars(r'%APPDATA%\Bloret-Launcher\Bloret-Launcher')
        else:
            custom_path = self.page2_1.custom_path_edit.text()
            if not custom_path:
                InfoBar.error(
                    title='错误',
                    content='请选择安装路径',
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                return
            self.install_config['install_path'] = custom_path
            
        self.stacked_widget.setCurrentWidget(self.page2_2)
        
    def on_page2_2_next(self):
        """页面2.2下一步"""
        # 获取附加选项
        self.install_config['create_desktop_shortcut'] = self.page2_2.desktop_shortcut_checkbox.isChecked()
        self.install_config['create_start_menu_item'] = self.page2_2.start_menu_checkbox.isChecked()
        
        # 开始安装
        self.start_installation()
        
    def start_installation(self):
        """开始安装过程"""
        self.stacked_widget.setCurrentWidget(self.page3)
        
        # 模拟安装过程
        self.page3.start_installation(self.install_config)
        
    def on_install_complete(self):
        """安装完成"""
        InfoBar.success(
            title='安装完成',
            content='Bloret Launcher 已成功安装！',
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
        
        # 延迟关闭
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self.close)


def main():
    # 启用高 DPI 缩放
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置主题
    setTheme(Theme.AUTO)
    
    # 创建安装向导
    installer = BloretInstaller()
    installer.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()