#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import tempfile
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QProgressBar, QLabel, QFrame
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal, QObject
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

class MockNetworkWorker(QObject):
    """模拟网络工作线程"""
    download_progress = pyqtSignal(int)
    download_complete = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
    def mock_download(self):
        """模拟下载过程"""
        try:
            # 模拟下载进度
            for i in range(0, 101, 5):
                self.download_progress.emit(i)
                time.sleep(0.1)  # 模拟下载延迟
            
            # 模拟下载完成
            temp_file = os.path.join(tempfile.gettempdir(), "test-download.zip")
            with open(temp_file, 'w') as f:
                f.write("mock content")
            self.download_complete.emit(temp_file)
            
        except Exception as e:
            print(f"模拟下载失败: {e}")

class DownloadDialogTester(QDialog):
    """下载对话框测试器"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("下载进度窗口测试")
        self.resize(600, 400)
        self.downloading_dialog = None
        
        # 创建测试按钮
        from PyQt5.QtWidgets import QPushButton, QVBoxLayout
        layout = QVBoxLayout()
        
        test_button = QPushButton("测试下载进度窗口")
        test_button.clicked.connect(self.test_download_dialog)
        layout.addWidget(test_button)
        
        self.setLayout(layout)
        
    def test_download_dialog(self):
        """测试下载进度对话框"""
        self.show_downloading_dialog()
        
        # 创建工作线程
        self.thread = QThread()
        self.worker = MockNetworkWorker()
        self.worker.moveToThread(self.thread)
        
        # 连接信号
        self.thread.started.connect(self.worker.mock_download)
        self.worker.download_progress.connect(self.update_download_progress)
        self.worker.download_complete.connect(self.on_download_complete)
        
        # 启动线程
        self.thread.start()
    
    def show_downloading_dialog(self):
        """显示下载进度窗口"""
        try:
            # 使用现有的UI文件
            ui_path = os.path.join(os.path.dirname(__file__), "ui", "downloading.ui")
            print(f"UI文件路径: {ui_path}")
            print(f"UI文件存在: {os.path.exists(ui_path)}")
            
            if os.path.exists(ui_path):
                from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel
                
                self.downloading_dialog = QDialog(self)
                self.downloading_dialog.setWindowTitle("正在下载")
                self.downloading_dialog.setModal(True)
                self.downloading_dialog.resize(400, 182)
                
                # 直接使用UI文件创建对话框
                self.downloading_dialog = uic.loadUi(ui_path, self.downloading_dialog)
                
                # 获取进度条和标签引用
                if QFLUENT_AVAILABLE:
                    self.download_progress_bar = self.downloading_dialog.findChild(ProgressBar, "ProgressBar")
                    self.download_progress_label = self.downloading_dialog.findChild(BodyLabel, "BodyLabel")
                else:
                    self.download_progress_bar = self.downloading_dialog.findChild(QProgressBar, "ProgressBar")
                    self.download_progress_label = self.downloading_dialog.findChild(QLabel, "BodyLabel")
                
                print(f"进度条: {self.download_progress_bar}")
                print(f"标签: {self.download_progress_label}")
                
                # 设置初始值
                if self.download_progress_bar:
                    self.download_progress_bar.setValue(0)
                if self.download_progress_label:
                    self.download_progress_label.setText("0%")
                
                # 居中显示对话框
                self.downloading_dialog.move(
                    self.x() + (self.width() - self.downloading_dialog.width()) // 2,
                    self.y() + (self.height() - self.downloading_dialog.height()) // 2
                )
                
                self.downloading_dialog.show()
                
                # 强制刷新
                from PyQt5.QtWidgets import QApplication
                QApplication.processEvents()
                
                print("下载进度窗口已显示！")
                
            else:
                print("UI文件不存在")
                
        except Exception as e:
            print(f"显示下载进度窗口失败: {e}")
            import traceback
            traceback.print_exc()
    
    def update_download_progress(self, progress):
        """更新下载进度"""
        print(f"更新进度: {progress}%")
        if self.downloading_dialog and hasattr(self, 'download_progress_bar'):
            # 尝试设置进度条值
            try:
                if hasattr(self.download_progress_bar, 'setValue'):
                    self.download_progress_bar.setValue(progress)
                elif hasattr(self.download_progress_bar, 'setProgress'):
                    self.download_progress_bar.setProgress(progress)
                else:
                    # 如果都不存在，直接设置属性
                    self.download_progress_bar.value = progress
            except Exception as e:
                print(f"更新进度条失败: {e}")
            
            # 更新标签文本
            if hasattr(self, 'download_progress_label') and self.download_progress_label:
                try:
                    self.download_progress_label.setText(f"{progress}%")
                except Exception as e:
                    print(f"更新标签文本失败: {e}")
            
            # 强制刷新UI
            try:
                if self.downloading_dialog:
                    self.downloading_dialog.repaint()
                    from PyQt5.QtWidgets import QApplication
                    QApplication.processEvents()
            except:
                pass
    
    def on_download_complete(self, file_path):
        """下载完成"""
        print(f"下载完成: {file_path}")
        if self.downloading_dialog:
            self.downloading_dialog.hide()
            self.downloading_dialog = None
        
        # 清理线程
        if hasattr(self, 'thread'):
            self.thread.quit()
            self.thread.wait()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    tester = DownloadDialogTester()
    tester.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()