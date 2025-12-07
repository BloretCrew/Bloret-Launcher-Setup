#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt5.QtCore import Qt

from qfluentwidgets import (SmoothScrollArea, TitleLabel, CardWidget, SubtitleLabel, 
                            RadioButton, LineEdit, PushButton, PrimaryPushButton, InfoBar, InfoBarPosition)


class Page2_1(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # 创建滚动区域
        scroll_area = SmoothScrollArea()
        scroll_area.setStyleSheet("background: transparent; border: none")
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # 添加顶部间距
        scroll_layout.addSpacing(40)
        
        # 标题
        title = TitleLabel("你想要将 Bloret Launcher 安装在哪里？\nWhere do you want to install the Bloret Launcher?")
        title.setWordWrap(True)
        scroll_layout.addWidget(title)
        
        # 安装路径选择卡片
        path_card = CardWidget()
        path_layout = QVBoxLayout(path_card)
        path_layout.setSpacing(15)
        
        # 卡片标题
        card_title = SubtitleLabel("选择安装位置 / Choose installation location")
        path_layout.addWidget(card_title)
        
        # 默认路径选项
        self.appdata_radio = RadioButton()
        default_path = os.path.expandvars(r'C:\Users\%USERNAME%\AppData\Roaming\Bloret-Launcher\Bloret-Launcher')
        self.appdata_radio.setText(default_path)
        self.appdata_radio.setChecked(True)
        path_layout.addWidget(self.appdata_radio)
        
        # 自定义路径选项
        custom_layout = QHBoxLayout()
        custom_layout.setSpacing(10)
        
        self.custom_radio = RadioButton()
        self.custom_radio.setText("")
        custom_layout.addWidget(self.custom_radio)
        
        # 自定义路径输入框
        self.custom_path_edit = LineEdit()
        self.custom_path_edit.setPlaceholderText("选择自定义安装路径...")
        self.custom_path_edit.setEnabled(False)
        custom_layout.addWidget(self.custom_path_edit)
        
        # 浏览按钮
        self.browse_button = PushButton("选择文件夹")
        self.browse_button.setEnabled(False)
        self.browse_button.clicked.connect(self.browse_folder)
        custom_layout.addWidget(self.browse_button)
        
        path_layout.addLayout(custom_layout)
        
        # 连接单选按钮信号
        self.appdata_radio.toggled.connect(self.on_radio_changed)
        self.custom_radio.toggled.connect(self.on_radio_changed)
        
        scroll_layout.addWidget(path_card)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()
        
        # 下一步按钮
        self.next_button = PrimaryPushButton("下一步 / Next")
        self.next_button.setMinimumWidth(350)
        button_layout.addWidget(self.next_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # 设置样式
        self.setStyleSheet("""
            Page2_1 {
                background-color: transparent;
            }
        """)
        
    def on_radio_changed(self):
        """处理单选按钮状态变化"""
        if self.custom_radio.isChecked():
            self.custom_path_edit.setEnabled(True)
            self.browse_button.setEnabled(True)
        else:
            self.custom_path_edit.setEnabled(False)
            self.browse_button.setEnabled(False)
            
    def browse_folder(self):
        """浏览文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择安装路径",
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.custom_path_edit.setText(folder)
            
    def get_install_path(self):
        """获取选择的安装路径"""
        if self.appdata_radio.isChecked():
            return os.path.expandvars(r'%APPDATA%\Bloret-Launcher\Bloret-Launcher')
        else:
            return self.custom_path_edit.text()
    
    def apply_theme(self, is_dark=None):
        """应用主题到页面"""
        if is_dark is None:
            from installer import is_dark_theme
            is_dark = is_dark_theme()
        
        # 页面已经使用QFluentWidgets组件，它们会自动跟随主题
        # 这里可以添加额外的主题特定样式调整
        if is_dark:
            self.setStyleSheet("""
                Page2_1 {
                    background-color: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                Page2_1 {
                    background-color: transparent;
                }
            """)