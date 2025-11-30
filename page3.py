#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap

from qfluentwidgets import (SmoothScrollArea, TitleLabel, ProgressBar, StrongBodyLabel, 
                            CardWidget, SubtitleLabel, PrimaryPushButton, InfoBar, InfoBarPosition)


class Page3(QWidget):
    install_progress = pyqtSignal(int)
    install_complete = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.install_config = {}
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
        
        # 标题
        self.title_label = TitleLabel("正在安装 Bloret Launcher / Installing Bloret Launcher")
        scroll_layout.addWidget(self.title_label)
        
        # 进度条区域
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)
        
        self.progress_bar = ProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = StrongBodyLabel("0%")
        progress_layout.addWidget(self.progress_label)
        
        scroll_layout.addLayout(progress_layout)
        
        # 添加间距
        scroll_layout.addSpacing(40)
        
        # 介绍卡片
        intro_card = CardWidget()
        intro_layout = QVBoxLayout(intro_card)
        intro_layout.setSpacing(15)
        
        # 卡片标题
        card_title = SubtitleLabel("来认识一下 Bloret Launcher / Come and get to know Bloret Launcher")
        intro_layout.addWidget(card_title)
        
        # 图片展示区域
        image_layout = QHBoxLayout()
        image_layout.addStretch()
        
        # 尝试加载图片
        self.image_label = StrongBodyLabel()
        self.image_label.setFixedSize(382, 297)
        self.image_label.setScaledContents(True)
        
        try:
            pixmap = QPixmap("ui/BLroundHome.png")
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap)
            else:
                self.image_label.setText("图片加载失败")
                self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except:
            self.image_label.setText("图片加载失败")
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        image_layout.addWidget(self.image_label)
        image_layout.addStretch()
        
        intro_layout.addLayout(image_layout)
        
        scroll_layout.addWidget(intro_card)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()
        
        # 完成按钮（初始隐藏）
        self.finish_button = PrimaryPushButton("完成 / Finish")
        self.finish_button.setMinimumWidth(350)
        self.finish_button.clicked.connect(self.on_finish)
        self.finish_button.setVisible(False)
        button_layout.addWidget(self.finish_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # 设置样式
        self.setStyleSheet("""
            Page3 {
                background-color: transparent;
            }
        """)
        
        # 连接信号
        self.install_progress.connect(self.update_progress)
        self.install_complete.connect(self.on_install_complete)
        
    def start_installation(self, install_config):
        """开始安装"""
        self.install_config = install_config
        self.progress_bar.setValue(0)
        self.progress_label.setText("0%")
        
        # 在后台线程中执行安装
        self.install_thread = threading.Thread(target=self.simulate_installation)
        self.install_thread.daemon = True
        self.install_thread.start()
        
    def simulate_installation(self):
        """模拟安装过程"""
        try:
            # 模拟不同的安装步骤
            steps = [
                ("正在创建安装目录...", 10),
                ("正在复制文件...", 30),
                ("正在注册组件...", 50),
                ("正在创建快捷方式...", 70),
                ("正在完成安装...", 90),
                ("安装完成！", 100)
            ]
            
            for step_text, progress in steps:
                # 更新进度
                self.install_progress.emit(progress)
                
                # 模拟耗时操作
                time.sleep(0.5)
                
                if progress == 100:
                    self.install_complete.emit()
                    
        except Exception as e:
            # 如果安装失败，显示错误信息
            QTimer.singleShot(0, lambda: self.show_install_error(str(e)))
            
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(f"{value}%")
        
        # 根据进度更新标题
        if value < 30:
            self.title_label.setText("正在准备安装... / Preparing installation...")
        elif value < 70:
            self.title_label.setText("正在安装文件... / Installing files...")
        elif value < 100:
            self.title_label.setText("即将完成... / Almost done...")
        else:
            self.title_label.setText("安装完成！/ Installation complete!")
            
    def on_install_complete(self):
        """安装完成"""
        self.progress_bar.setValue(100)
        self.progress_label.setText("100%")
        self.finish_button.setVisible(True)
        
        # 显示成功消息
        InfoBar.success(
            title='安装完成',
            content='Bloret Launcher 已成功安装！',
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
        
    def show_install_error(self, error_msg):
        """显示安装错误"""
        InfoBar.error(
            title='安装失败',
            content=f'安装过程中出现错误: {error_msg}',
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )
        
    def on_finish(self):
        """完成安装"""
        if self.parent:
            self.parent.close()