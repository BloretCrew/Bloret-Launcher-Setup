#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import tempfile
import threading
import requests
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                           QStackedWidget, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, pyqtSignal, QThread, QObject
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


class NetworkWorker(QObject):
    """网络请求工作线程"""
    info_received = pyqtSignal(dict)
    download_progress = pyqtSignal(int)
    download_complete = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.temp_file_path = None
        
    def fetch_info(self):
        """获取版本信息"""
        try:
            response = requests.get('https://launcher.bloret.net/api/info', timeout=10)
            response.raise_for_status()
            data = response.json()
            self.info_received.emit(data)
        except Exception as e:
            self.error_occurred.emit(f"获取版本信息失败: {str(e)}")
    
    def download_file(self, url, filename):
        """下载文件"""
        try:
            temp_dir = tempfile.gettempdir()
            self.temp_file_path = os.path.join(temp_dir, filename)
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(self.temp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.download_progress.emit(progress)
            
            self.download_complete.emit(self.temp_file_path)
            
        except Exception as e:
            self.error_occurred.emit(f"下载失败: {str(e)}")


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
            'installation_type': 'quick',  # 'quick' or 'custom'
            'latest_version': '25.0',  # 默认版本
            'download_url': '',
            'downloaded_file': ''
        }
        
        # 网络工作线程
        self.network_thread = None
        self.network_worker = None
        self.downloading_dialog = None
        
        # 初始化 UI
        self.initUI()
        
        # 启动时获取版本信息
        self.fetch_version_info()
        
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
        
        # 切换到安装页面
        self.stacked_widget.setCurrentWidget(self.page3)
        
        # 开始下载和安装流程
        if self.install_config['download_url']:
            # 如果有下载链接，先下载再安装
            self.start_download()
        else:
            # 如果没有下载链接，直接模拟安装
            self.start_installation()
        
    def start_installation(self):
        """开始安装过程"""
        self.stacked_widget.setCurrentWidget(self.page3)
        
        # 如果页面3有start_installation方法，调用它
        if hasattr(self.page3, 'start_installation'):
            self.page3.start_installation(self.install_config)
        
    def fetch_version_info(self):
        """获取版本信息"""
        # 创建网络工作线程
        self.network_thread = QThread()
        self.network_worker = NetworkWorker()
        self.network_worker.moveToThread(self.network_thread)
        
        # 连接信号
        self.network_thread.started.connect(self.network_worker.fetch_info)
        self.network_worker.info_received.connect(self.on_version_info_received)
        self.network_worker.error_occurred.connect(self.on_network_error)
        
        # 启动线程
        self.network_thread.start()
    
    def on_version_info_received(self, data):
        """接收到版本信息"""
        try:
            self.install_config['latest_version'] = data.get('latestVersion', 'Unknown')
            self.install_config['download_url'] = data.get('downloads', {}).get('stable', {}).get('gitcode', {}).get('exe', '')
            
            # 更新页面1的版本显示
            latest_version = self.install_config['latest_version']
            if hasattr(self.page1, 'update_version'):
                self.page1.update_version(latest_version)
            
            print(f"最新版本: {self.install_config['latest_version']}")
            print(f"下载链接: {self.install_config['download_url']}")
        except Exception as e:
            print(f"处理版本信息失败: {e}")
            self.on_network_error(f"处理版本信息失败: {e}")
        
        # 清理线程
        self.cleanup_network_thread()
    
    def start_download(self):
        """开始下载文件"""
        if not self.install_config['download_url']:
            self.show_error("下载链接无效")
            return
        
        # 显示下载进度窗口
        self.show_downloading_dialog()
        
        # 创建网络工作线程
        self.network_thread = QThread()
        self.network_worker = NetworkWorker()
        self.network_worker.moveToThread(self.network_thread)
        
        # 连接信号
        self.network_thread.started.connect(lambda: self.network_worker.download_file(
            self.install_config['download_url'], 
            'Bloret-Launcher-Setup.exe'
        ))
        self.network_worker.download_progress.connect(self.update_download_progress)
        self.network_worker.download_complete.connect(self.on_download_complete)
        self.network_worker.error_occurred.connect(self.on_download_error)
        
        # 启动线程
        self.network_thread.start()
    
    def show_downloading_dialog(self):
        """显示下载进度窗口"""
        try:
            from qfluentwidgets import Dialog, ProgressBar, BodyLabel
            
            self.downloading_dialog = Dialog(
                "正在下载",
                "Bloret Launcher 安装文件",
                self
            )
            
            # 创建下载进度界面
            download_widget = QWidget()
            download_layout = QVBoxLayout(download_widget)
            
            self.download_progress_bar = ProgressBar()
            self.download_progress_label = BodyLabel("0%")
            
            download_layout.addWidget(self.download_progress_bar)
            download_layout.addWidget(self.download_progress_label)
            
            self.downloading_dialog.setContentWidget(download_widget)
            self.downloading_dialog.setModal(True)
            self.downloading_dialog.show()
            
        except ImportError:
            # 如果 QFluentWidgets 不可用，使用标准对话框
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel
            
            self.downloading_dialog = QDialog(self)
            self.downloading_dialog.setWindowTitle("正在下载")
            self.downloading_dialog.setModal(True)
            self.downloading_dialog.resize(300, 150)
            
            layout = QVBoxLayout()
            
            label = QLabel("Bloret Launcher 安装文件")
            self.download_progress_bar = QProgressBar()
            self.download_progress_label = QLabel("0%")
            
            layout.addWidget(label)
            layout.addWidget(self.download_progress_bar)
            layout.addWidget(self.download_progress_label)
            
            self.downloading_dialog.setLayout(layout)
            self.downloading_dialog.show()
    
    def update_download_progress(self, progress):
        """更新下载进度"""
        if self.downloading_dialog and hasattr(self, 'download_progress_bar'):
            self.download_progress_bar.setValue(progress)
            self.download_progress_label.setText(f"{progress}%")
    
    def on_download_complete(self, file_path):
        """下载完成"""
        self.install_config['downloaded_file'] = file_path
        
        # 隐藏下载进度窗口
        if self.downloading_dialog:
            self.downloading_dialog.hide()
            self.downloading_dialog = None
        
        # 清理线程
        self.cleanup_network_thread()
        
        # 继续安装流程
        self.start_installation()
    
    def on_download_error(self, error_msg):
        """下载错误"""
        # 隐藏下载进度窗口
        if self.downloading_dialog:
            self.downloading_dialog.hide()
            self.downloading_dialog = None
        
        # 清理线程
        self.cleanup_network_thread()
        
        # 显示错误
        self.show_error(error_msg)
    
    def on_network_error(self, error_msg):
        """网络错误"""
        self.cleanup_network_thread()
        print(f"网络错误: {error_msg}")
    
    def cleanup_network_thread(self):
        """清理网络线程"""
        if self.network_thread:
            self.network_thread.quit()
            self.network_thread.wait()
            self.network_thread = None
        if self.network_worker:
            self.network_worker = None
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