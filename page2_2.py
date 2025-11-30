#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

from qfluentwidgets import (SmoothScrollArea, TitleLabel, CardWidget, SubtitleLabel, 
                            CheckBox, PrimaryPushButton)


class Page2_2(QWidget):
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
        title = TitleLabel("还需要其他项目吗？\nDo you need anything else?")
        title.setWordWrap(True)
        scroll_layout.addWidget(title)
        
        # 附加选项卡片
        options_card = CardWidget()
        options_layout = QVBoxLayout(options_card)
        options_layout.setSpacing(15)
        
        # 卡片标题
        card_title = SubtitleLabel("添加附加项目 / Add additional items")
        options_layout.addWidget(card_title)
        
        # 桌面快捷方式选项
        self.desktop_shortcut_checkbox = CheckBox("添加桌面快捷方式 / Add desktop shortcut")
        options_layout.addWidget(self.desktop_shortcut_checkbox)
        
        # 启动菜单项选项
        self.start_menu_checkbox = CheckBox("添加启动菜单项 Bloret Launcher / Add startup menu item Bloret Launcher")
        options_layout.addWidget(self.start_menu_checkbox)
        
        # 设置默认状态
        self.desktop_shortcut_checkbox.setChecked(True)
        self.start_menu_checkbox.setChecked(True)
        
        scroll_layout.addWidget(options_card)
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
            Page2_2 {
                background-color: transparent;
            }
        """)
        
    def get_options(self):
        """获取用户选择的附加选项"""
        return {
            'create_desktop_shortcut': self.desktop_shortcut_checkbox.isChecked(),
            'create_start_menu_item': self.start_menu_checkbox.isChecked()
        }