#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont

from qfluentwidgets import (SmoothScrollArea, StrongBodyLabel, LargeTitleLabel, 
                            SubtitleLabel, BodyLabel, PushButton, PrimaryPushButton)


class Page1(QWidget):
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
        
        # 创建标题区域
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)
        
        # Logo
        logo_label = StrongBodyLabel()
        logo_label.setFixedSize(100, 100)
        logo_label.setScaledContents(True)
        
        # 尝试加载 Logo
        try:
            pixmap = QPixmap("ui/bloret.png")
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap)
        except:
            logo_label.setText("LOGO")
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(logo_label)
        
        # 标题和描述
        title_layout = QVBoxLayout()
        title_layout.setSpacing(10)
        
        # 主标题
        main_title = LargeTitleLabel("Bloret Launcher")
        title_layout.addWidget(main_title)
        
        # 副标题
        subtitle = SubtitleLabel("Conveniently manage your Minecraft, conveniently play Bloret.\n便捷地管理你的 Minecraft，便捷地游玩 Bloret。")
        subtitle.setWordWrap(True)
        title_layout.addWidget(subtitle)
        
        # 安装信息
        info_layout = QHBoxLayout()
        info_layout.setSpacing(5)
        
        info_label = BodyLabel("将安装 / About to install :")
        app_label = StrongBodyLabel("Bloret Launcher")
        version_label = StrongBodyLabel("25.0")
        
        info_layout.addWidget(info_label)
        info_layout.addWidget(app_label)
        info_layout.addWidget(version_label)
        info_layout.addStretch()
        
        title_layout.addLayout(info_layout)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        scroll_layout.addLayout(header_layout)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()
        
        # 自定义安装按钮
        self.custom_installation_button = PushButton("自定义安装 / Custom Installation")
        self.custom_installation_button.setMinimumWidth(200)
        button_layout.addWidget(self.custom_installation_button)
        
        # 快速安装按钮
        self.quick_install_button = PrimaryPushButton("快速安装 / Quick Installation")
        self.quick_install_button.setMinimumWidth(350)
        button_layout.addWidget(self.quick_install_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # 设置样式
        self.setStyleSheet("""
            Page1 {
                background-color: transparent;
            }
        """)