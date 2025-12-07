#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QProgressBar, QLabel, QFrame
from PyQt5 import uic
import time

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

def test_download_dialog():
    """测试下载进度窗口"""
    app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = QDialog()
    main_window.setWindowTitle("测试主窗口")
    main_window.resize(600, 400)
    main_window.show()
    
    # 测试UI文件加载
    ui_path = os.path.join(os.path.dirname(__file__), "ui", "downloading.ui")
    print(f"UI文件路径: {ui_path}")
    print(f"UI文件存在: {os.path.exists(ui_path)}")
    
    if os.path.exists(ui_path):
        try:
            # 创建下载进度对话框
            download_dialog = QDialog(main_window)
            download_dialog.setWindowTitle("正在下载")
            download_dialog.setModal(True)
            download_dialog.resize(400, 182)
            
            # 加载UI文件
            download_dialog = uic.loadUi(ui_path, download_dialog)
            
            # 获取组件
            if QFLUENT_AVAILABLE:
                progress_bar = download_dialog.findChild(ProgressBar, "ProgressBar")
                body_label = download_dialog.findChild(BodyLabel, "BodyLabel")
                subtitle_label = download_dialog.findChild(SubtitleLabel, "SubtitleLabel")
            else:
                progress_bar = download_dialog.findChild(QProgressBar, "ProgressBar")
                body_label = download_dialog.findChild(QLabel, "BodyLabel")
                subtitle_label = download_dialog.findChild(QLabel, "SubtitleLabel")
            
            print(f"进度条: {progress_bar}")
            print(f"描述标签: {body_label}")
            print(f"标题标签: {subtitle_label}")
            
            # 显示对话框
            download_dialog.show()
            
            # 模拟进度更新
            for i in range(0, 101, 10):
                if progress_bar:
                    if hasattr(progress_bar, 'setValue'):
                        progress_bar.setValue(i)
                    elif hasattr(progress_bar, 'setProgress'):
                        progress_bar.setProgress(i)
                
                if body_label:
                    body_label.setText(f"{i}%")
                
                app.processEvents()
                time.sleep(0.5)
            
            print("测试完成！")
            
        except Exception as e:
            print(f"UI文件加载失败: {e}")
            # 创建简化版本
            create_simple_dialog(main_window)
    else:
        print("UI文件不存在，创建简化版本")
        create_simple_dialog(main_window)
    
    sys.exit(app.exec())

def create_simple_dialog(parent):
    """创建简化版本对话框"""
    dialog = QDialog(parent)
    dialog.setWindowTitle("正在下载")
    dialog.setModal(True)
    dialog.resize(400, 182)
    
    layout = QVBoxLayout()
    
    # 创建卡片样式
    card = QFrame()
    card.setMinimumSize(0, 120)
    card.setFrameStyle(QFrame.Box)
    card.setStyleSheet("""
        QFrame {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 10px;
        }
    """)
    
    card_layout = QVBoxLayout()
    
    # 标题
    title_label = QLabel("资源仍在下载中 / The resource is still downloading")
    title_label.setWordWrap(True)
    title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
    card_layout.addWidget(title_label)
    
    # 描述
    desc_label = QLabel("待资源文件下载完成后，安装将会开始 / The installation will begin once the resource files have finished downloading.")
    desc_label.setWordWrap(True)
    desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
    card_layout.addWidget(desc_label)
    
    # 进度条
    progress_bar = QProgressBar()
    progress_bar.setMinimumSize(0, 10)
    progress_bar.setValue(0)
    card_layout.addWidget(progress_bar)
    
    card.setLayout(card_layout)
    layout.addWidget(card)
    
    dialog.setLayout(layout)
    dialog.show()

if __name__ == "__main__":
    test_download_dialog()