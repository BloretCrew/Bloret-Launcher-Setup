#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QTextEdit
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal, QObject

# 尝试导入 QFluentWidgets
try:
    from qfluentwidgets import ProgressBar, BodyLabel
    QFLUENT_AVAILABLE = True
except ImportError:
    QFLUENT_AVAILABLE = False

class MockNetworkWorker(QObject):
    """模拟网络工作线程"""
    download_progress = pyqtSignal(int)
    download_complete = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
    def mock_download(self):
        """模拟下载过程"""
        try:
            for i in range(0, 101, 5):
                self.download_progress.emit(i)
                time.sleep(0.1)
            self.download_complete.emit("test-file.zip")
        except Exception as e:
            print(f"模拟下载失败: {e}")

class SimpleDownloadTest(QDialog):
    """简单下载测试"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("下载进度窗口测试")
        self.resize(400, 300)
        self.downloading_dialog = None
        
        # 创建UI
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        test_button = QPushButton("测试下载进度窗口")
        test_button.clicked.connect(self.test_download)
        layout.addWidget(test_button)
        
        self.setLayout(layout)
        
        self.log("测试程序初始化完成")
        self.log(f"QFluentWidgets 可用: {QFLUENT_AVAILABLE}")
    
    def log(self, message):
        """添加日志"""
        timestamp = time.strftime('%H:%M:%S')
        self.log_text.append(f"[{timestamp}] {message}")
        QApplication.processEvents()
        
    def test_download(self):
        """测试下载进度窗口"""
        self.log("开始测试下载进度窗口...")
        
        # 显示下载进度窗口
        self.log("显示下载进度窗口...")
        self.show_downloading_dialog()
        
        if self.downloading_dialog:
            self.log("下载进度窗口显示成功")
        else:
            self.log("错误: 下载进度窗口未显示")
            return
        
        # 启动模拟下载
        self.log("启动模拟下载...")
        self.thread = QThread()
        self.worker = MockNetworkWorker()
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.mock_download)
        self.worker.download_progress.connect(self.update_progress)
        self.worker.download_complete.connect(self.download_finished)
        
        self.thread.start()
    
    def show_downloading_dialog(self):
        """显示下载进度窗口"""
        try:
            ui_path = os.path.join(os.path.dirname(__file__), "ui", "downloading.ui")
            self.log(f"UI文件路径: {ui_path}")
            self.log(f"UI文件存在: {os.path.exists(ui_path)}")
            
            if os.path.exists(ui_path):
                self.downloading_dialog = QDialog(self)
                self.downloading_dialog.setWindowTitle("正在下载")
                self.downloading_dialog.setModal(True)
                self.downloading_dialog.resize(400, 182)
                
                # 加载UI文件
                self.downloading_dialog = uic.loadUi(ui_path, self.downloading_dialog)
                
                # 获取组件
                self.progress_bar = self.downloading_dialog.findChild(ProgressBar if QFLUENT_AVAILABLE else None, "ProgressBar")
                self.progress_label = self.downloading_dialog.findChild(BodyLabel if QFLUENT_AVAILABLE else None, "BodyLabel")
                
                self.log(f"进度条组件: {self.progress_bar}")
                self.log(f"标签组件: {self.progress_label}")
                
                # 设置初始值
                if self.progress_bar:
                    self.progress_bar.setValue(0)
                if self.progress_label:
                    self.progress_label.setText("0%")
                
                # 显示对话框
                self.downloading_dialog.show()
                self.log("下载进度窗口已显示")
                
            else:
                self.log("错误: UI文件不存在")
                
        except Exception as e:
            self.log(f"显示下载进度窗口失败: {e}")
            import traceback
            traceback.print_exc()
    
    def update_progress(self, progress):
        """更新进度"""
        self.log(f"进度: {progress}%")
        if self.downloading_dialog and hasattr(self, 'progress_bar'):
            if self.progress_bar:
                try:
                    if hasattr(self.progress_bar, 'setValue'):
                        self.progress_bar.setValue(progress)
                    elif hasattr(self.progress_bar, 'setProgress'):
                        self.progress_bar.setProgress(progress)
                except Exception as e:
                    self.log(f"更新进度条失败: {e}")
            
            if self.progress_label:
                try:
                    self.progress_label.setText(f"{progress}%")
                except Exception as e:
                    self.log(f"更新标签失败: {e}")
    
    def download_finished(self, file_path):
        """下载完成"""
        self.log(f"下载完成: {file_path}")
        if self.downloading_dialog:
            self.downloading_dialog.hide()
            self.downloading_dialog = None
        
        if hasattr(self, 'thread'):
            self.thread.quit()
            self.thread.wait()

def main():
    app = QApplication(sys.argv)
    test = SimpleDownloadTest()
    test.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()