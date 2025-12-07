#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import tempfile
import threading
import requests
import logging
import time
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                           QStackedWidget, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPalette
from PyQt5 import uic
import ctypes

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('installer_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
    from PyQt5.QtWidgets import (QPushButton, QProgressBar, QLabel, QScrollArea, 
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
            label.setAlignment(Qt.AlignCenter)
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
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            self.setLayout(layout)

    class Page2_2(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout()
            label = QLabel("选择附加选项")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            self.setLayout(layout)

    class Page3(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout()
            label = QLabel("正在安装...")
            label.setAlignment(Qt.AlignCenter)
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
        logger.info("开始获取版本信息")
        try:
            response = requests.get('http://pcfs.eno.ink:3001/api/info', timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"成功获取版本信息: {data}")
            self.info_received.emit(data)
        except Exception as e:
            logger.error(f"获取版本信息失败: {str(e)}")
            self.error_occurred.emit(f"获取版本信息失败: {str(e)}")
    
    def download_file(self, url, filename):
        """下载文件"""
        logger.info(f"开始下载文件: {url} -> {filename}")
        try:
            temp_dir = tempfile.gettempdir()
            self.temp_file_path = os.path.join(temp_dir, filename)
            logger.info(f"临时文件路径: {self.temp_file_path}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            logger.info(f"文件总大小: {total_size} bytes")
            downloaded = 0
            
            last_progress = -1
            with open(self.temp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):  # 增加块大小到32KB
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            # 确保进度不超过100
                            progress = min(progress, 100)
                            # 只在进度有变化时才更新
                            if progress != last_progress:
                                logger.debug(f"下载进度: {progress}% ({downloaded}/{total_size} bytes)")
                                self.download_progress.emit(progress)
                                last_progress = progress
                                # 只在进度变化时添加很小的延迟让UI刷新
                                time.sleep(0.001)  # 1毫秒延迟
                        else:
                            # 如果无法获取总大小，使用模拟进度
                            if downloaded % (1024 * 1024) == 0:  # 每MB更新一次
                                simulated_progress = min(int((downloaded / (50 * 1024 * 1024)) * 100), 95)  # 假设50MB文件
                                if simulated_progress != last_progress:
                                    logger.debug(f"模拟下载进度: {simulated_progress}% ({downloaded} bytes)")
                                    self.download_progress.emit(simulated_progress)
                                    last_progress = simulated_progress
            
            logger.info(f"文件下载完成: {self.temp_file_path}")
            self.download_complete.emit(self.temp_file_path)
            
        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            self.error_occurred.emit(f"下载失败: {str(e)}")

def apply_theme(self, is_dark=None):
    """应用主题到应用程序"""
    if is_dark is None:
        is_dark = is_dark_theme()
    
    app = QApplication.instance()
    
    if QFLUENT_AVAILABLE:
        # 设置 QFluentWidgets 主题
        try:
            if is_dark:
                setTheme(Theme.DARK)
            else:
                setTheme(Theme.LIGHT)
        except:
            pass
    
    # 应用自定义样式
    if is_dark:
        # 深色主题样式
        dark_stylesheet = """
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #444444;
                color: #ffffff;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #555555;
            }
            QPushButton:pressed {
                background-color: #5a5a5a;
                border-color: #666666;
            }
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                color: #ffffff;
                padding: 6px 10px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
                outline: none;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QCheckBox {
                color: #ffffff;
                background-color: transparent;
            }
            QRadioButton {
                color: #ffffff;
                background-color: transparent;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            SmoothScrollArea {
                background-color: transparent;
                border: none;
            }
            CardWidget {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
            }
        """
        self.setStyleSheet(dark_stylesheet)
        
        # 设置深色调色板
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor("#2a2a2a"))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1e1e1e"))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#000000"))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor("#3a3a3a"))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor("#ff0000"))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor("#2a82da"))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor("#0078d4"))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        app.setPalette(dark_palette)
    else:
        # 浅色主题样式
        light_stylesheet = """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
                background-color: #f5f5f5;
                color: #000000;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                color: #000000;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #999999;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
                border-color: #666666;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                color: #000000;
                padding: 6px 10px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
                outline: none;
            }
            QLabel {
                color: #000000;
                background-color: transparent;
            }
            QCheckBox {
                color: #000000;
                background-color: transparent;
            }
            QRadioButton {
                color: #000000;
                background-color: transparent;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            SmoothScrollArea {
                background-color: transparent;
                border: none;
            }
            CardWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """
        self.setStyleSheet(light_stylesheet)
        
        # 恢复默认调色板
        app.setPalette(app.style().standardPalette())

class BloretInstaller(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("Bloret Launcher 安装向导")
        
        # 应用初始主题
        apply_theme(self)
        
        # 监听系统主题变化
        try:
            QApplication.instance().paletteChanged.connect(self.on_system_theme_changed)
        except:
            pass
        
        # 尝试设置窗口图标
        try:
            icon_path = "ui/bloret.ico"
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except:
            pass
            
        self.resize(670, 452)
        
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
        
        # 设置样式 - 主题将在apply_theme中统一处理
        # 这里不再设置默认样式，避免覆盖主题设置
        
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
        logger.info("开始安装流程")
        self.stacked_widget.setCurrentWidget(self.page3)
        
        # 如果页面3有start_installation方法，调用它
        if hasattr(self.page3, 'start_installation'):
            logger.info("调用page3的start_installation方法")
            logger.info(f"安装配置: {self.install_config}")
            self.page3.start_installation(self.install_config)
        else:
            logger.warning("page3没有start_installation方法")
        
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
            self.install_config['download_url'] = data.get('downloads', {}).get('stable', {}).get('gitcode', {}).get('zip', '')
            
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
        """开始下载"""
        logger.info("开始下载流程")
        if not self.install_config['download_url']:
            logger.error("下载链接无效")
            self.show_error("下载链接无效")
            return
        
        logger.info(f"下载URL: {self.install_config['download_url']}")
        
        # 显示下载进度窗口
        logger.info("显示下载进度窗口")
        self.show_downloading_dialog()
        
        # 创建网络工作线程
        logger.info("创建网络工作线程")
        self.network_thread = QThread()
        self.network_worker = NetworkWorker()
        self.network_worker.moveToThread(self.network_thread)
        logger.info("网络工作对象已移动到线程")
        
        # 连接信号
        logger.info("连接网络线程信号")
        self.network_thread.started.connect(lambda: self.network_worker.download_file(
            self.install_config['download_url'], 
            'Bloret-Launcher-Setup.zip'
        ))
        self.network_worker.download_progress.connect(self.update_download_progress)
        self.network_worker.download_complete.connect(self.on_download_complete)
        self.network_worker.error_occurred.connect(self.on_download_error)
        logger.info("信号连接完成")
        
        # 启动线程
        logger.info("启动网络线程")
        self.network_thread.start()
        logger.info("网络线程已启动")
    
    def show_downloading_dialog(self):
        """显示下载进度窗口"""
        logger.info("开始显示下载进度窗口")
        try:
            # 使用现有的UI文件
            ui_path = os.path.join(os.path.dirname(__file__), "ui", "downloading.ui")
            logger.info(f"UI文件路径: {ui_path}")
            logger.info(f"UI文件存在: {os.path.exists(ui_path)}")
            
            if os.path.exists(ui_path):
                from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel
                
                self.downloading_dialog = QDialog(self)
                self.downloading_dialog.setWindowTitle("正在下载")
                self.downloading_dialog.setModal(True)
                self.downloading_dialog.resize(400, 182)
                
                # 设置对话框样式
                self.downloading_dialog.setStyleSheet("""
                    QDialog {
                        background-color: #ffffff;
                    }
                """)
                
                # 直接使用UI文件创建对话框
                self.downloading_dialog = uic.loadUi(ui_path, self.downloading_dialog)
                
                # 获取进度条和标签引用
                self.download_progress_bar = self.downloading_dialog.findChild(QProgressBar, "ProgressBar")
                self.download_progress_label = self.downloading_dialog.findChild(QLabel, "BodyLabel")
                logger.info(f"初始查找 - QProgressBar: {self.download_progress_bar}, QLabel: {self.download_progress_label}")
                
                # 如果找不到QProgressBar类型的进度条，尝试查找QFluentWidgets的ProgressBar
                if not self.download_progress_bar:
                    try:
                        from qfluentwidgets import ProgressBar
                        self.download_progress_bar = self.downloading_dialog.findChild(ProgressBar, "ProgressBar")
                        logger.info(f"使用QFluentWidgets ProgressBar: {self.download_progress_bar}")
                    except ImportError:
                        logger.warning("QFluentWidgets ProgressBar导入失败")
                else:
                    logger.info(f"使用标准QProgressBar: {self.download_progress_bar}")
                
                # 如果找不到QLabel类型的标签，尝试查找QFluentWidgets的BodyLabel
                if not self.download_progress_label:
                    try:
                        from qfluentwidgets import BodyLabel
                        self.download_progress_label = self.downloading_dialog.findChild(BodyLabel, "BodyLabel")
                        logger.info(f"使用QFluentWidgets BodyLabel: {self.download_progress_label}")
                    except ImportError:
                        logger.warning("QFluentWidgets BodyLabel导入失败")
                else:
                    logger.info(f"使用标准QLabel: {self.download_progress_label}")
                
                # 设置初始值
                if self.download_progress_bar:
                    self.download_progress_bar.setValue(0)
                    logger.info("设置进度条初始值为0")
                if self.download_progress_label:
                    self.download_progress_label.setText("0%")
                    logger.info("设置标签初始文本为0%")
                
                # 居中显示对话框
                dialog_x = self.x() + (self.width() - self.downloading_dialog.width()) // 2
                dialog_y = self.y() + (self.height() - self.downloading_dialog.height()) // 2
                self.downloading_dialog.move(dialog_x, dialog_y)
                logger.info(f"对话框居中显示: 位置({dialog_x}, {dialog_y})")
                
                self.downloading_dialog.show()
                logger.info("下载进度窗口已显示")
                
                # 强制刷新
                QApplication.processEvents()
                logger.info("UI强制刷新完成")
            else:
                # 如果UI文件不存在，使用代码创建
                from qfluentwidgets import ProgressBar, BodyLabel, SubtitleLabel, CardWidget
                from PyQt5.QtWidgets import QDialog, QVBoxLayout
                
                self.downloading_dialog = QDialog(self)
                self.downloading_dialog.setWindowTitle("正在下载")
                self.downloading_dialog.setModal(True)
                self.downloading_dialog.resize(400, 182)
                
                # 创建下载进度界面，模仿UI文件的结构
                main_layout = QVBoxLayout()
                
                # 创建卡片组件
                card = CardWidget()
                card.setMinimumSize(0, 120)
                
                card_layout = QVBoxLayout()
                
                # 标题标签
                title_label = SubtitleLabel("资源仍在下载中 / The resource is still downloading")
                title_label.setWordWrap(True)
                card_layout.addWidget(title_label)
                
                # 描述标签
                desc_label = BodyLabel("待资源文件下载完成后，安装将会开始 / The installation will begin once the resource files have finished downloading.")
                desc_label.setWordWrap(True)
                card_layout.addWidget(desc_label)
                
                # 进度条
                self.download_progress_bar = ProgressBar()
                self.download_progress_bar.setMinimumSize(0, 10)
                self.download_progress_bar.setValue(0)
                card_layout.addWidget(self.download_progress_bar)
                
                card.setLayout(card_layout)
                main_layout.addWidget(card)
                
                self.downloading_dialog.setLayout(main_layout)
                
                # 居中显示对话框
                self.downloading_dialog.move(
                    self.x() + (self.width() - self.downloading_dialog.width()) // 2,
                    self.y() + (self.height() - self.downloading_dialog.height()) // 2
                )
                
                self.downloading_dialog.show()
                
                # 强制刷新
                QApplication.processEvents()
            
        except ImportError:
            # 如果 QFluentWidgets 不可用，使用标准对话框
            from PyQt5.QtWidgets import QDialog, QProgressBar, QLabel, QVBoxLayout, QFrame
            
            self.downloading_dialog = QDialog(self)
            self.downloading_dialog.setWindowTitle("正在下载")
            self.downloading_dialog.setModal(True)
            self.downloading_dialog.resize(400, 182)
            
            # 创建主布局
            main_layout = QVBoxLayout()
            
            # 创建卡片样式的容器
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
            
            # 标题标签
            title_label = QLabel("资源仍在下载中 / The resource is still downloading")
            title_label.setWordWrap(True)
            title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
            card_layout.addWidget(title_label)
            
            # 描述标签
            desc_label = QLabel("待资源文件下载完成后，安装将会开始 / The installation will begin once the resource files have finished downloading.")
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
            card_layout.addWidget(desc_label)
            
            # 进度条
            self.download_progress_bar = QProgressBar()
            self.download_progress_bar.setMinimumSize(0, 10)
            self.download_progress_bar.setValue(0)
            card_layout.addWidget(self.download_progress_bar)
            
            card.setLayout(card_layout)
            main_layout.addWidget(card)
            
            self.downloading_dialog.setLayout(main_layout)
            
            # 居中显示对话框
            self.downloading_dialog.move(
                self.x() + (self.width() - self.downloading_dialog.width()) // 2,
                self.y() + (self.height() - self.downloading_dialog.height()) // 2
            )
            
            self.downloading_dialog.show()
            
            # 强制刷新
            QApplication.processEvents()
    
    def update_download_progress(self, progress):
        """更新下载进度"""
        logger.debug(f"更新下载进度: {progress}%")
        if self.downloading_dialog and hasattr(self, 'download_progress_bar'):
            # 尝试设置进度条值
            try:
                if hasattr(self.download_progress_bar, 'setValue'):
                    self.download_progress_bar.setValue(progress)
                    logger.debug(f"使用setValue方法设置进度条: {progress}%")
                elif hasattr(self.download_progress_bar, 'setProgress'):
                    self.download_progress_bar.setProgress(progress)
                    logger.debug(f"使用setProgress方法设置进度条: {progress}%")
                else:
                    # 如果都不存在，直接设置属性
                    self.download_progress_bar.value = progress
                    logger.debug(f"直接设置进度条属性值: {progress}%")
            except Exception as e:
                logger.error(f"更新进度条失败: {e}")
                logger.error(f"进度条类型: {type(self.download_progress_bar)}")
            
            # 更新标签文本
            if hasattr(self, 'download_progress_label') and self.download_progress_label:
                try:
                    self.download_progress_label.setText(f"{progress}%")
                    logger.debug(f"更新标签文本: {progress}%")
                except Exception as e:
                    logger.error(f"更新标签文本失败: {e}")
            
            # 强制刷新UI
            try:
                if self.downloading_dialog:
                    self.downloading_dialog.repaint()
                    QApplication.processEvents()
                    logger.debug("UI强制刷新完成")
            except Exception as e:
                logger.error(f"UI刷新失败: {e}")
        else:
            logger.warning(f"无法更新进度: downloading_dialog={self.downloading_dialog}, 进度条存在={hasattr(self, 'download_progress_bar')}")
    
    def on_download_complete(self, file_path):
        """下载完成"""
        logger.info(f"下载完成: {file_path}")
        self.install_config['downloaded_file'] = file_path
        
        # 隐藏下载进度窗口
        if self.downloading_dialog:
            logger.info("隐藏下载进度窗口")
            self.downloading_dialog.hide()
            self.downloading_dialog = None
        else:
            logger.warning("下载进度窗口不存在")
        
        # 清理线程
        logger.info("开始清理网络线程")
        self.cleanup_network_thread()
        
        # 继续安装流程
        logger.info("开始安装流程")
        self.start_installation()
    
    def on_download_error(self, error_msg):
        """下载错误"""
        logger.error(f"下载错误: {error_msg}")
        # 隐藏下载进度窗口
        if self.downloading_dialog:
            logger.info("隐藏下载进度窗口")
            self.downloading_dialog.hide()
            self.downloading_dialog = None
        else:
            logger.warning("下载进度窗口不存在")
        
        # 清理线程
        logger.info("开始清理网络线程")
        self.cleanup_network_thread()
        
        # 显示错误
        logger.info("显示错误信息")
        self.show_error(error_msg)
    
    def on_network_error(self, error_msg):
        """网络错误"""
        self.cleanup_network_thread()
        print(f"网络错误: {error_msg}")
    
    def cleanup_network_thread(self):
        """清理网络线程"""
        logger.info("开始清理网络线程")
        if self.network_thread:
            logger.info("正在停止网络线程")
            self.network_thread.quit()
            self.network_thread.wait()
            self.network_thread = None
            logger.info("网络线程已清理")
        else:
            logger.warning("网络线程不存在")
        if self.network_worker:
            logger.info("清理网络工作对象")
            self.network_worker = None
        else:
            logger.warning("网络工作对象不存在")
        logger.info("网络线程清理完成")
    
    def on_install_complete(self):
        """安装完成"""
        self.show_success("安装完成", "Bloret Launcher 已成功安装！")
        
        # 延迟关闭
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(2000, self.close)
        
    def show_error(self, message):
        """显示错误信息"""
        if QFLUENT_AVAILABLE:
            InfoBar.error(
                title='错误',
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        else:
            # 使用标准消息框作为后备
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", message)
            
    def show_success(self, title, message):
        """显示成功信息"""
        if QFLUENT_AVAILABLE:
            InfoBar.success(
                title=title,
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            # 使用标准消息框作为后备
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, title, message)
    
    def on_system_theme_changed(self):
        """系统主题变化时的处理"""
        # 重新应用主题
        self.apply_theme()
        
        # 通知所有页面重新应用主题
        for page in [self.page1, self.page2_1, self.page2_2, self.page3]:
            if hasattr(page, 'apply_theme'):
                page.apply_theme()
            else:
                # 如果页面没有apply_theme方法，直接应用主题样式
                is_dark = is_dark_theme()
                if QFLUENT_AVAILABLE:
                    try:
                        if is_dark:
                            setTheme(Theme.DARK)
                        else:
                            setTheme(Theme.LIGHT)
                    except:
                        pass
    
    def toggle_theme_for_testing(self):
        """测试用：手动切换主题"""
        current_theme = is_dark_theme()
        # 模拟切换主题（仅用于测试）
        self.apply_theme(not current_theme)
        
        # 通知所有页面重新应用主题
        for page in [self.page1, self.page2_1, self.page2_2, self.page3]:
            if hasattr(page, 'apply_theme'):
                page.apply_theme(not current_theme)

def is_dark_theme():
    try:
        # 定义注册表路径和键名
        reg_path = "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"
        reg_key = "AppsUseLightTheme"
        
        # 打开注册表键
        hkey = ctypes.wintypes.HKEY()
        if ctypes.windll.advapi32.RegOpenKeyExW(0x80000001, reg_path, 0, 0x20019, ctypes.byref(hkey)) != 0:
            return False
        
        # 读取键值
        value = ctypes.c_int()
        size = ctypes.c_uint(4)
        if ctypes.windll.advapi32.RegQueryValueExW(hkey, reg_key, 0, None, ctypes.byref(value), ctypes.byref(size)) != 0:
            ctypes.windll.advapi32.RegCloseKey(hkey)
            return False
        
        # 关闭注册表键
        ctypes.windll.advapi32.RegCloseKey(hkey)
        
        # 返回主题状态
        return value.value == 0  # 0 表示深色主题，1 表示浅色主题
    except Exception as e:
        print(f"检测主题时发生错误: {e}")
        return False


def main():
    """主函数"""
    # 启用高 DPI 缩放
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    except:
        pass
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建安装向导 - 主题将在初始化时自动应用
    installer = BloretInstaller()
    installer.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()