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
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, pyqtSignal, QThread, QObject, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPalette
from PyQt5 import uic
import ctypes
import traceback

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
    """网络请求工作线程 - 整合测试程序的成功实现"""
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
        """下载文件 - 整合测试程序的成功实现"""
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
            last_update_time = time.time()
            with open(self.temp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=16384):  # 减小块大小到16KB，增加更新频率
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            # 确保进度不超过100
                            progress = min(progress, 100)
                            current_time = time.time()
                            # 只在进度有变化且间隔超过100ms时才更新，避免过于频繁
                            if progress != last_progress and (current_time - last_update_time) > 0.1:
                                # 减少日志频率，只在关键进度点记录
                                if progress % 10 == 0:
                                    logger.debug(f"下载进度: {progress}%")
                                self.download_progress.emit(progress)
                                last_progress = progress
                                last_update_time = current_time
                                # 不再添加延迟，让下载更流畅
                        else:
                            # 如果无法获取总大小，使用模拟进度
                            if downloaded % (512 * 1024) == 0:  # 每512KB更新一次，更频繁
                                simulated_progress = min(int((downloaded / (50 * 1024 * 1024)) * 100), 95)  # 假设50MB文件
                                current_time = time.time()
                                if simulated_progress != last_progress and (current_time - last_update_time) > 0.1:
                                    # 减少日志频率，只在关键进度点记录
                                    if simulated_progress % 10 == 0:
                                        logger.debug(f"模拟下载进度: {simulated_progress}%")
                                    self.download_progress.emit(simulated_progress)
                                    last_progress = simulated_progress
                                    last_update_time = current_time
            
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
    def __init__(self, fetch_version=True):
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
            
        self.resize(700, 452)
        
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
        # 用于防止并发创建下载对话框
        import threading as _threading
        self._downloading_dialog_lock = _threading.Lock()
        
        # 初始化 UI
        self.initUI()
        
        # 启动时获取版本信息（测试时可传入 fetch_version=False 以避免网络线程）
        if fetch_version:
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
        logger.info("快速安装按钮被点击")
        self.install_config['installation_type'] = 'quick'
        self.install_config['install_path'] = os.path.expandvars(r'%APPDATA%\Bloret-Launcher\Bloret-Launcher')
        self.install_config['create_desktop_shortcut'] = True
        self.install_config['create_start_menu_item'] = True
        
        logger.info(f"快速安装配置: {self.install_config}")
        logger.info("直接跳转到安装页面")
        
        # 直接跳转到page3开始下载和安装
        self.stacked_widget.setCurrentWidget(self.page3)
        
        # 开始下载和安装流程
        if self.install_config['download_url']:
            # 如果有下载链接，先下载再安装
            logger.info("开始下载流程")
            self.start_download()
        else:
            # 如果没有下载链接，直接模拟安装
            logger.info("没有下载链接，直接开始安装流程")
            self.start_installation()
        
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
        """开始下载 - 整合测试程序的成功实现"""
        logger.info("开始下载流程")
        # 防止重复触发下载流程
        if getattr(self, '_download_starting', False):
            logger.info('下载流程已在启动中，跳过重复调用')
            return
        self._download_starting = True
        if not self.install_config['download_url']:
            logger.error("下载链接无效")
            self.show_error("下载链接无效")
            try:
                self._download_starting = False
            except Exception:
                pass
            return
        
        logger.info(f"下载URL: {self.install_config['download_url']}")
        
        # 显示下载进度窗口
        logger.info("显示下载进度窗口")
        self.show_downloading_dialog()
        
        # 确保对话框完全显示后再启动线程 - 参考测试程序
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
        time.sleep(0.1)  # 给UI一点时间完全初始化
        QApplication.processEvents()
        
        # 创建网络工作线程 - 参考测试程序
        logger.info("创建网络工作线程")
        self.network_thread = QThread()
        self.network_worker = NetworkWorker()
        self.network_worker.moveToThread(self.network_thread)
        logger.info("网络工作对象已移动到线程")
        
        # 连接信号 - 参考测试程序
        logger.info("连接网络线程信号")
        self.network_thread.started.connect(lambda: self.network_worker.download_file(
            self.install_config['download_url'], 
            'Bloret-Launcher-Setup.zip'
        ))
        self.network_worker.download_progress.connect(self.update_download_progress)
        self.network_worker.download_complete.connect(self.on_download_complete)
        self.network_worker.error_occurred.connect(self.on_download_error)
        logger.info("信号连接完成")
        
        # 启动线程 - 参考测试程序
        logger.info("启动网络线程")
        self.network_thread.start()
        logger.info("网络线程已启动")
        # 允许后续的下载启动（仅阻止创建阶段的并发）
        try:
            self._download_starting = False
        except Exception:
            pass
    
    def show_downloading_dialog(self):
        """显示下载进度窗口 - 整合测试程序的成功实现"""
        logger.info("开始显示下载进度窗口")
        # 如果已经存在正在显示的下载对话框或正在创建中，则直接返回（避免重复弹窗）
        try:
            logger.debug("show_downloading_dialog 调用堆栈:\n%s", ''.join(traceback.format_stack(limit=10)))
            # 使用锁序列化对话框创建，避免并发创建
            with self._downloading_dialog_lock:
                if getattr(self, '_downloading_dialog_opening', False):
                    logger.info("下载对话框正在创建，跳过重复创建")
                    return
                if getattr(self, 'downloading_dialog', None) is not None and self.downloading_dialog.isVisible():
                    logger.info("下载对话框已存在并可见，跳过创建")
                    return
                # 标记正在创建，防止并发创建两个对话框
                self._downloading_dialog_opening = True
        except Exception:
            # 如果检查可见性失败，继续创建新的对话框
            logger.exception('检查现有对话框时出错，继续创建新的对话框')
        try:
            # 在创建新对话框前，再次扫描顶层窗口以尝试复用已存在的下载对话框（防止外部触发重复创建）
            try:
                from PyQt5.QtWidgets import QApplication
                for w in QApplication.topLevelWidgets():
                    try:
                        if getattr(w, 'windowTitle', None) and callable(w.windowTitle) and w.windowTitle() == "正在下载":
                            logger.info("发现现存的下载对话框，复用该对话框")
                            self.downloading_dialog = w
                            if not self.downloading_dialog.isVisible():
                                self.downloading_dialog.show()
                                QApplication.processEvents()
                            return
                    except Exception:
                        continue
            except Exception:
                logger.exception('扫描顶层窗口以复用对话框时出错')

            # 使用现有的UI文件
            ui_path = os.path.join(os.path.dirname(__file__), "ui", "downloading.ui")
            logger.info(f"UI文件路径: {ui_path}")
            logger.info(f"UI文件存在: {os.path.exists(ui_path)}")
            
            if os.path.exists(ui_path):
                from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel
                
                # 导入QFluentWidgets组件（如果可用）
                if QFLUENT_AVAILABLE:
                    from qfluentwidgets import ProgressBar, BodyLabel
                
                self.downloading_dialog = QDialog(self)
                self.downloading_dialog.setWindowTitle("正在下载")
                self.downloading_dialog.setModal(True)
                self.downloading_dialog.resize(400, 182)
                
                # 直接使用UI文件创建对话框
                self.downloading_dialog = uic.loadUi(ui_path, self.downloading_dialog)
                
                # 获取进度条和标签引用 - 参考测试程序
                # 为了可靠刷新，优先使用 PyQt5 的 QProgressBar/QLabel，替换掉 QFluentWidgets 的组件
                if QFLUENT_AVAILABLE:
                    # 先尝试找到 QFluentWidgets 的控件
                    fluent_pb = self.downloading_dialog.findChild(ProgressBar, "ProgressBar")
                    fluent_lbl = self.downloading_dialog.findChild(BodyLabel, "BodyLabel")
                    from PyQt5.QtWidgets import QProgressBar, QLabel
                    if fluent_pb is not None:
                        try:
                            parent = fluent_pb.parent()
                            new_pb = QProgressBar(parent)
                            new_pb.setObjectName('ProgressBar')
                            new_pb.setRange(0, 100)
                            new_pb.setValue(0)
                            # 插入到父布局中，尽量保持位置
                            playout = parent.layout() if parent is not None else None
                            if playout is not None:
                                idx = playout.indexOf(fluent_pb)
                                playout.insertWidget(idx, new_pb)
                            fluent_pb.hide()
                            self.download_progress_bar = new_pb
                        except Exception:
                            logger.exception('替换 QFluent ProgressBar 失败，使用原始控件')
                            self.download_progress_bar = fluent_pb
                    else:
                        # 没找到 fluent pb，尝试找标准控件
                        self.download_progress_bar = self.downloading_dialog.findChild(QProgressBar, "ProgressBar")

                    if fluent_lbl is not None:
                        try:
                            parent = fluent_lbl.parent()
                            new_lbl = QLabel(parent)
                            new_lbl.setObjectName('BodyLabel')
                            new_lbl.setText('0%')
                            playout = parent.layout() if parent is not None else None
                            if playout is not None:
                                idx = playout.indexOf(fluent_lbl)
                                playout.insertWidget(idx + 1, new_lbl)
                            fluent_lbl.hide()
                            self.download_progress_label = new_lbl
                        except Exception:
                            logger.exception('替换 QFluent BodyLabel 失败，使用原始控件')
                            self.download_progress_label = fluent_lbl
                    else:
                        self.download_progress_label = self.downloading_dialog.findChild(QLabel, "BodyLabel")
                else:
                    self.download_progress_bar = self.downloading_dialog.findChild(QProgressBar, "ProgressBar")
                    self.download_progress_label = self.downloading_dialog.findChild(QLabel, "BodyLabel")
                
                logger.info(f"进度条: {self.download_progress_bar}")
                logger.info(f"标签: {self.download_progress_label}")
                
                # 设置初始值
                if self.download_progress_bar:
                    try:
                        self.download_progress_bar.setRange(0, 100)
                        self.download_progress_bar.setValue(0)
                    except Exception:
                        logger.exception('设置进度条初始值失败')
                if self.download_progress_label:
                    try:
                        self.download_progress_label.setText("0%")
                    except Exception:
                        logger.exception('设置进度标签初始文本失败')
                
                # 居中显示对话框
                self.downloading_dialog.move(
                    self.x() + (self.width() - self.downloading_dialog.width()) // 2,
                    self.y() + (self.height() - self.downloading_dialog.height()) // 2
                )
                
                self.downloading_dialog.show()
                logger.info("下载进度窗口已显示")

                # 强制刷新并调整布局以避免初始不可见的问题
                try:
                    QApplication.processEvents()
                    self.downloading_dialog.adjustSize()
                    self.downloading_dialog.updateGeometry()
                    self.downloading_dialog.repaint()
                except Exception:
                    logger.exception('显示对话框后刷新/调整布局失败')
                logger.info("UI强制刷新完成")

            # Ensure there is always a usable progress bar and label (fallback)
            try:
                # 如果 UI 文件中未找到进度条或标签，优先将回退控件加入到对话框布局中
                layout = None
                try:
                    layout = self.downloading_dialog.layout()
                except Exception:
                    layout = None

                if not hasattr(self, 'download_progress_bar') or self.download_progress_bar is None:
                    from PyQt5.QtWidgets import QProgressBar, QLabel
                    pb = QProgressBar()
                    pb.setObjectName('fallback_progress_bar')
                    pb.setRange(0, 100)
                    pb.setValue(0)
                    if layout is not None:
                        layout.addWidget(pb)
                    else:
                        pb.setParent(self.downloading_dialog)
                    pb.show()
                    self.download_progress_bar = pb

                if not hasattr(self, 'download_progress_label') or self.download_progress_label is None:
                    from PyQt5.QtWidgets import QLabel
                    lbl = QLabel('0%')
                    lbl.setObjectName('fallback_progress_label')
                    if layout is not None:
                        layout.addWidget(lbl)
                    else:
                        lbl.setParent(self.downloading_dialog)
                    lbl.show()
                    self.download_progress_label = lbl
            except Exception:
                logger.exception('创建回退进度控件失败')

            # 如果 UI 文件不存在，则使用代码创建回退对话框（确保不会在已加载 UI 的情况下再次创建）
            if not os.path.exists(ui_path):
                # 如果已经存在可见的下载对话框，则跳过回退对话框的创建
                try:
                    if getattr(self, 'downloading_dialog', None) is not None and self.downloading_dialog.isVisible():
                        logger.info('下载对话框已存在（回退创建被跳过）')
                        return
                except Exception:
                    pass

                try:
                    from qfluentwidgets import ProgressBar, BodyLabel, SubtitleLabel, CardWidget
                except Exception:
                    ProgressBar = None
                    BodyLabel = None
                    SubtitleLabel = None
                    CardWidget = None

                from PyQt5.QtWidgets import QDialog, QVBoxLayout

                self.downloading_dialog = QDialog(self)
                self.downloading_dialog.setWindowTitle("正在下载")
                self.downloading_dialog.setModal(True)  # 使用模态对话框，类似测试程序
                self.downloading_dialog.resize(400, 182)
                
                # 创建下载进度界面，模仿UI文件的结构
                main_layout = QVBoxLayout()
                main_layout.setContentsMargins(12, 12, 12, 12)
                main_layout.setSpacing(10)

                # 创建卡片组件
                if CardWidget is not None:
                    card = CardWidget()
                else:
                    from PyQt5.QtWidgets import QFrame
                    card = QFrame()
                    card.setMinimumSize(0, 120)
                    card.setFrameStyle(QFrame.Box)
                    card.setStyleSheet("""
                        QFrame { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 10px; }
                    """)

                card_layout = QVBoxLayout()
                card_layout.setContentsMargins(8, 8, 8, 8)
                card_layout.setSpacing(8)

                # 标题标签
                if SubtitleLabel is not None:
                    title_label = SubtitleLabel("资源仍在下载中 / The resource is still downloading")
                else:
                    from PyQt5.QtWidgets import QLabel
                    title_label = QLabel("资源仍在下载中 / The resource is still downloading")
                    title_label.setStyleSheet('font-weight: bold;')
                title_label.setWordWrap(True)
                card_layout.addWidget(title_label)

                # 描述标签
                if BodyLabel is not None:
                    desc_label = BodyLabel("待资源文件下载完成后，安装将会开始 / The installation will begin once the resource files have finished downloading.")
                else:
                    from PyQt5.QtWidgets import QLabel
                    desc_label = QLabel("待资源文件下载完成后，安装将会开始 / The installation will begin once the resource files have finished downloading.")
                desc_label.setWordWrap(True)
                desc_label.setObjectName('BodyLabel')
                card_layout.addWidget(desc_label)

                # 进度条（优先使用标准 QProgressBar 以确保视觉刷新可靠）
                from PyQt5.QtWidgets import QProgressBar, QLabel, QSizePolicy
                self.download_progress_bar = QProgressBar()
                self.download_progress_bar.setObjectName('ProgressBar')
                self.download_progress_bar.setMinimumHeight(14)
                self.download_progress_bar.setRange(0, 100)
                self.download_progress_bar.setValue(0)
                self.download_progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                card_layout.addWidget(self.download_progress_bar)
                
                # 状态标签
                self.download_progress_label = QLabel('0%')
                self.download_progress_label.setObjectName('BodyLabel')
                self.download_progress_label.setAlignment(0x0004)  # Qt.AlignRight
                card_layout.addWidget(self.download_progress_label)

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
            self.downloading_dialog.setModal(True)  # 使用模态对话框，类似测试程序
            self.downloading_dialog.resize(420, 200)
            
            # 创建主布局
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(12, 12, 12, 12)
            main_layout.setSpacing(10)
            
            # 创建卡片样式的容器
            card = QFrame()
            card.setMinimumSize(0, 120)
            card.setFrameStyle(QFrame.Box)
            card.setStyleSheet("""
                QFrame { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 10px; }
            """)
            
            card_layout = QVBoxLayout()
            card_layout.setContentsMargins(8, 8, 8, 8)
            card_layout.setSpacing(8)
            
            # 标题标签
            title_label = QLabel("资源仍在下载中 / The resource is still downloading")
            title_label.setWordWrap(True)
            title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
            card_layout.addWidget(title_label)
            
            # 描述标签
            desc_label = QLabel("待资源文件下载完成后，安装将会开始 / The installation will begin once the resource files have finished downloading.")
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
            desc_label.setObjectName('BodyLabel')
            card_layout.addWidget(desc_label)
            
            # 进度条
            from PyQt5.QtWidgets import QSizePolicy
            self.download_progress_bar = QProgressBar()
            self.download_progress_bar.setObjectName('ProgressBar')
            self.download_progress_bar.setMinimumHeight(14)
            self.download_progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.download_progress_bar.setRange(0, 100)
            self.download_progress_bar.setValue(0)
            card_layout.addWidget(self.download_progress_bar)

            # 状态标签
            self.download_progress_label = QLabel('0%')
            self.download_progress_label.setObjectName('BodyLabel')
            self.download_progress_label.setAlignment(0x0004)  # Qt.AlignRight
            card_layout.addWidget(self.download_progress_label)
            
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
        finally:
            # 确保创建标志在任何路径下都被清理
            try:
                self._downloading_dialog_opening = False
            except Exception:
                pass
    def update_download_progress(self, progress):
        """更新下载进度 - 整合测试程序的成功实现"""
        logger.info(f"更新进度: {progress}%")
        
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
                logger.warning(f"更新进度条失败: {e}")
            
            # 更新标签文本
            if hasattr(self, 'download_progress_label') and self.download_progress_label:
                try:
                    self.download_progress_label.setText(f"{progress}%")
                except Exception as e:
                    logger.warning(f"更新标签文本失败: {e}")
            
            # 强制刷新UI
            try:
                if self.downloading_dialog:
                    # 尝试强制刷新并触发布局更新，解决进度在调整窗口大小后才显示的问题
                    try:
                        self.download_progress_bar.updateGeometry()
                    except Exception:
                        pass
                    try:
                        layout = self.downloading_dialog.layout()
                        if layout is not None:
                            try:
                                layout.activate()
                            except Exception:
                                pass
                    except Exception:
                        pass
                    try:
                        self.download_progress_bar.repaint()
                    except Exception:
                        pass
                    self.downloading_dialog.repaint()
                    from PyQt5.QtWidgets import QApplication
                    QApplication.processEvents()
            except Exception:
                logger.exception('刷新下载对话框时出错')

    def refresh_download_dialog(self):
        """定期刷新下载对话框（已废弃，不再使用定时刷新）"""
        # 完全移除了定时刷新逻辑，让Qt的事件循环自然处理
        pass
    
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
        # 弹出完成对话框，提供“完成”和“完成并打开”两个操作
        self.show_finish_dialog("安装完成", "Bloret Launcher 已成功安装！")

    def _open_installed_path(self):
        """尝试打开已安装的可执行或包含已下载文件的文件夹"""
        import subprocess
        try:
            path = None
            # 优先尝试已记录的安装可执行路径
            path = self.install_config.get('installed_exe') if hasattr(self, 'install_config') else None
            if not path:
                path = self.install_config.get('downloaded_file') if hasattr(self, 'install_config') else None
            if not path:
                # 没有已知路径，提示用户
                self.show_error('未找到要打开的文件或路径。')
                return
            if os.path.isdir(path):
                # 打开文件夹
                if os.name == 'nt':
                    os.startfile(path)
                else:
                    subprocess.Popen(['xdg-open', path])
            elif os.path.isfile(path):
                # 如果是文件，尝试打开文件或父目录
                if path.lower().endswith('.zip') or path.lower().endswith('.tar') or path.lower().endswith('.gz'):
                    folder = os.path.dirname(path)
                    if os.name == 'nt':
                        os.startfile(folder)
                    else:
                        subprocess.Popen(['xdg-open', folder])
                else:
                    # 可执行或其它文件，尝试直接打开
                    if os.name == 'nt':
                        os.startfile(path)
                    else:
                        subprocess.Popen([path])
        except Exception:
            logger.exception('打开已安装路径失败')
            self.show_error('打开已安装文件/路径时发生错误')

    def show_finish_dialog(self, title, message):
        """显示安装完成对话框，包含两个按钮：'完成' 和 '完成并打开'（后者使用 PrimaryPushButton）"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        dialog.resize(480, 160)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # 消息说明
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        main_layout.addWidget(msg_label)

        # 底部按钮栏（右对齐）
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        if QFLUENT_AVAILABLE:
            try:
                from qfluentwidgets import PushButton, PrimaryPushButton
                finish_btn = PushButton('完成')
                finish_and_open_btn = PrimaryPushButton('完成并打开')
            except Exception:
                from PyQt5.QtWidgets import QPushButton
                finish_btn = QPushButton('完成')
                finish_and_open_btn = QPushButton('完成并打开')
                # 给主按钮上色以示 Primary
                finish_and_open_btn.setStyleSheet('background-color: #0078d4; color: white;')
        else:
            from PyQt5.QtWidgets import QPushButton
            finish_btn = QPushButton('完成')
            finish_and_open_btn = QPushButton('完成并打开')
            finish_and_open_btn.setStyleSheet('background-color: #0078d4; color: white;')

        # 连接按钮事件
        def on_finish():
            try:
                dialog.accept()
            finally:
                try:
                    self.close()
                except Exception:
                    pass

        def on_finish_and_open():
            try:
                # 打开安装路径/可执行
                self._open_installed_path()
            finally:
                try:
                    dialog.accept()
                finally:
                    try:
                        self.close()
                    except Exception:
                        pass

        finish_btn.clicked.connect(on_finish)
        finish_and_open_btn.clicked.connect(on_finish_and_open)

        # 添加到布局（顺序：完成，完成并打开）
        btn_layout.addWidget(finish_btn)
        btn_layout.addWidget(finish_and_open_btn)

        main_layout.addLayout(btn_layout)

        dialog.setLayout(main_layout)

        # 使主按钮有初始焦点
        try:
            finish_and_open_btn.setFocus()
        except Exception:
            pass

        # 居中显示
        dialog.move(
            self.x() + (self.width() - dialog.width()) // 2,
            self.y() + (self.height() - dialog.height()) // 2
        )

        dialog.show()
        try:
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
        except Exception:
            pass
        # 将 dialog 保存在实例上方便测试/后续操作
        self._finish_dialog = dialog
        
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