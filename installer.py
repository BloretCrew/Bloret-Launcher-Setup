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
                           QStackedWidget, QHBoxLayout, QLabel, QFileDialog)
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

# 页面类（已合并 page1.py / page2_1.py / page2_2.py / page3.py）
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
            logo_label.setAlignment(Qt.AlignCenter)
        
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
        self.version_label = StrongBodyLabel("25.0")  # 改为实例变量
        
        info_layout.addWidget(info_label)
        info_layout.addWidget(app_label)
        info_layout.addWidget(self.version_label)
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
    
    def update_version(self, version):
        """更新版本信息显示"""
        self.version_label.setText(version)
    
    def apply_theme(self, is_dark=None):
        """应用主题到页面"""
        if is_dark is None:
            from installer import is_dark_theme
            is_dark = is_dark_theme()
        
        # 页面已经使用QFluentWidgets组件，它们会自动跟随主题
        # 这里可以添加额外的主题特定样式调整
        if is_dark:
            self.setStyleSheet("""
                Page1 {
                    background-color: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                Page1 {
                    background-color: transparent;
                }
            """)


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
    
    def apply_theme(self, is_dark=None):
        """应用主题到页面"""
        if is_dark is None:
            from installer import is_dark_theme
            is_dark = is_dark_theme()
        
        # 页面已经使用QFluentWidgets组件，它们会自动跟随主题
        # 这里可以添加额外的主题特定样式调整
        if is_dark:
            self.setStyleSheet("""
                Page2_2 {
                    background-color: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                Page2_2 {
                    background-color: transparent;
                }
            """)


# Page3 内容（功能较多，来源于 page3.py）
logger = logging.getLogger(__name__)


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
        self.title_label = TitleLabel("正在安装 Bloret Launcher\nInstalling Bloret Launcher")
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
        card_title = SubtitleLabel("来认识一下 Bloret Launcher\nCome and get to know Bloret Launcher")
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
                self.image_label.setAlignment(Qt.AlignCenter)
        except:
            self.image_label.setText("图片加载失败")
            self.image_label.setAlignment(Qt.AlignCenter)
        
        image_layout.addWidget(self.image_label)
        image_layout.addStretch()
        
        intro_layout.addLayout(image_layout)
        
        scroll_layout.addWidget(intro_card)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # 底部按钮区域
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(15)
        self.button_layout.addStretch()
        
        # 完成按钮（初始隐藏）
        self.finish_button = PrimaryPushButton("完成 / Finish")
        self.finish_button.setMinimumWidth(180)
        self.finish_button.clicked.connect(self.on_finish_clicked)
        self.finish_button.setVisible(False)
        
        # # 完成并打开按钮（初始隐藏）
        # self.finish_open_button = PrimaryPushButton("完成并打开 / Finish and Open")
        # self.finish_open_button.setMinimumWidth(280)
        # self.finish_open_button.clicked.connect(self.on_finish_and_open_clicked)
        # self.finish_open_button.setVisible(False)
        
        self.button_layout.addWidget(self.finish_button)
        # self.button_layout.addWidget(self.finish_open_button)
        
        main_layout.addLayout(self.button_layout)
        
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
        logger.info(f"Page3: 开始安装流程")
        logger.info(f"安装配置: {install_config}")
        self.install_config = install_config
        self.progress_bar.setValue(0)
        self.progress_label.setText("0%")
        
        # 在后台线程中执行安装
        logger.info(f"创建安装线程")
        self.install_thread = threading.Thread(target=self.simulate_installation)
        self.install_thread.daemon = True
        self.install_thread.start()
        logger.info(f"安装线程已启动")
        
    def simulate_installation(self):
        """模拟安装过程"""
        logger.info(f"模拟安装过程开始")
        try:
            # 检查是否有下载的文件
            downloaded_file = self.install_config.get('downloaded_file', '')
            logger.info(f"检查下载的文件: {downloaded_file}")
            
            if downloaded_file and os.path.exists(downloaded_file):
                logger.info(f"找到下载的文件，执行实际安装: {downloaded_file}")
                # 如果有下载的文件，执行实际安装
                self.install_from_downloaded_file(downloaded_file)
            else:
                logger.info(f"未找到下载的文件，执行模拟安装")
                # 否则模拟安装
                self.simulate_install_steps()
                
        except Exception as e:
            logger.error(f"安装过程失败: {e}")
            logger.error(traceback.format_exc())
            # 如果安装失败，显示错误信息
            QTimer.singleShot(0, lambda: self.show_install_error(str(e)))
    
    def install_from_downloaded_file(self, file_path):
        """从下载的文件安装"""
        temp_extract_dir = None
        try:
            import subprocess
            import shutil
            import zipfile
            
            # 安装步骤
            steps = [
                ("正在准备安装环境...", 10),
                ("正在验证下载文件...", 20),
                ("正在解压安装文件...", 40),
                ("正在复制文件到目标目录...", 60),
                ("正在创建快捷方式...", 80),
                ("正在完成安装...", 95),
                ("安装完成！", 100)
            ]
            
            # 获取安装路径
            install_path = self.install_config.get('install_path', '')
            
            for step_text, progress in steps:
                self.install_progress.emit(progress)
                
                if progress == 40:
                    # 解压文件（如果是zip文件）
                    logger.info(f"进度40%: 处理文件 {file_path}")
                    if file_path.endswith('.zip'):
                        logger.info(f"检测到zip文件，开始解压: {file_path}")
                        # 创建临时解压目录
                        temp_extract_dir = os.path.join(os.path.dirname(file_path), 'bloret_temp')
                        logger.info(f"创建临时解压目录: {temp_extract_dir}")
                        os.makedirs(temp_extract_dir, exist_ok=True)
                        logger.info(f"临时解压目录创建成功: {temp_extract_dir}")
                        
                        # 解压zip文件
                        logger.info(f"开始解压zip文件到: {temp_extract_dir}")
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(temp_extract_dir)
                        logger.info(f"zip文件解压完成")
                        
                        # 查找解压后的安装程序
                        logger.info(f"在解压目录中查找安装程序: {temp_extract_dir}")
                        installer_exe = self.find_installer_exe(temp_extract_dir)
                        logger.info(f"找到的安装程序: {installer_exe}")
                        if installer_exe:
                            file_path = installer_exe  # 更新为解压后的安装程序路径
                            logger.info(f"更新安装程序路径为: {file_path}")
                        else:
                            raise Exception("在zip文件中未找到安装程序")
                    else:
                        logger.info(f"不是zip文件，直接使用原路径: {file_path}")
                    
                    time.sleep(2)
                elif progress == 60:
                    # 文件复制
                    logger.info(f"开始复制文件到安装目录: {install_path}")
                    try:
                        # 创建安装目录（如果不存在）
                        os.makedirs(install_path, exist_ok=True)
                        
                        # 如果是从解压目录复制文件
                        if temp_extract_dir and os.path.exists(temp_extract_dir):
                            logger.info(f"从解压目录复制文件: {temp_extract_dir} -> {install_path}")
                            import shutil
                            
                            # 复制所有文件和子目录，如果文件已存在则覆盖
                            for root, dirs, files in os.walk(temp_extract_dir):
                                # 计算相对路径
                                rel_path = os.path.relpath(root, temp_extract_dir)
                                if rel_path == '.':
                                    target_dir = install_path
                                else:
                                    target_dir = os.path.join(install_path, rel_path)
                                
                                # 创建目标目录
                                os.makedirs(target_dir, exist_ok=True)
                                
                                # 复制文件
                                for file in files:
                                    src_file = os.path.join(root, file)
                                    dst_file = os.path.join(target_dir, file)
                                    
                                    # 如果目标文件已存在，先删除再复制（覆盖）
                                    if os.path.exists(dst_file):
                                        logger.info(f"文件已存在，准备覆盖: {dst_file}")
                                        os.remove(dst_file)
                                    
                                    shutil.copy2(src_file, dst_file)
                                    logger.debug(f"复制文件: {src_file} -> {dst_file}")
                            
                            logger.info(f"文件复制完成，覆盖模式已启用")
                        else:
                            logger.warning(f"没有找到解压目录，跳过文件复制")
                            
                    except Exception as e:
                        logger.error(f"文件复制失败: {e}")
                        raise
                    
                    time.sleep(1)
                elif progress == 80:
                    # 创建快捷方式
                    self.create_shortcuts()
                    time.sleep(0.5)
                else:
                    time.sleep(0.3)
                
                if progress == 100:
                    # 安装完成 - 文件已经通过复制方式安装完成
                    logger.info(f"安装完成！文件已成功复制到: {install_path}")
                    logger.info(f"安装模式: 直接文件复制（覆盖模式已启用）")
                    self.install_complete.emit()
                    
        except Exception as e:
            logger.error(f"安装过程捕获异常: {e}")
            logger.error(traceback.format_exc())
            self.show_install_error(f"安装失败: {str(e)}")
        finally:
            # 清理临时文件 - 确保传递正确的参数
            logger.info(f"finally块: 准备清理临时文件")
            logger.info(f"finally块: file_path = {file_path}")
            logger.info(f"finally块: temp_extract_dir = {temp_extract_dir}")
            
            # 确定要清理的下载文件路径
            cleanup_file = None
            if 'downloaded_file' in self.install_config:
                cleanup_file = self.install_config['downloaded_file']
                logger.info(f"使用安装配置中的下载文件: {cleanup_file}")
            elif file_path and file_path.endswith('.zip'):
                cleanup_file = file_path
                logger.info(f"使用当前的zip文件路径: {cleanup_file}")
            
            self.cleanup_temp_files(cleanup_file, temp_extract_dir)
    
    def find_installer_exe(self, extract_dir):
        """在解压目录中查找安装程序"""
        try:
            logger.info(f"开始在目录中查找安装程序: {extract_dir}")
            # 常见的安装程序名称
            installer_names = ['setup.exe', 'install.exe', 'Bloret-Launcher-Setup.exe', 
                             'Bloret Launcher Setup.exe', 'BloretLauncherSetup.exe']
            
            exe_files = []

            # 遍历解压目录
            logger.debug(f"遍历解压目录: {extract_dir}")
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    file_lower = file.lower()
                    if file_lower.endswith('.exe'):
                        full_path = os.path.join(root, file)
                        # 检查是否匹配特定名称
                        if any(name in file_lower for name in [n.lower() for n in installer_names]):
                            logger.info(f"找到匹配名称的安装程序: {full_path}")
                            return full_path
                        # 收集所有exe文件
                        exe_files.append(full_path)
            
            # 如果没找到特定名称的exe，从收集的exe中寻找最大的文件（通常是主程序）
            if exe_files:
                logger.debug(f"未找到特定名称安装程序，正在分析 {len(exe_files)} 个exe文件...")
                # 按文件大小降序排序
                exe_files.sort(key=lambda x: os.path.getsize(x), reverse=True)
                largest_exe = exe_files[0]
                logger.info(f"选择最大的exe文件作为安装程序: {largest_exe} (Size: {os.path.getsize(largest_exe)} bytes)")
                return largest_exe
            
            logger.warning(f"在目录 {extract_dir} 中未找到任何exe文件")
            return None
        except Exception as e:
            logger.error(f"查找安装程序失败: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def cleanup_temp_files(self, downloaded_file, temp_extract_dir):
        """清理临时文件"""
        try:
            logger.info(f"开始清理临时文件...")
            logger.info(f"下载文件: {downloaded_file}")
            logger.info(f"临时解压目录: {temp_extract_dir}")
            
            # 清理下载的zip文件
            if downloaded_file and downloaded_file.endswith('.zip'):
                logger.debug(f"检查下载的zip文件是否存在: {os.path.exists(downloaded_file)}")
                if os.path.exists(downloaded_file):
                    logger.info(f"正在删除下载的zip文件: {downloaded_file}")
                    os.remove(downloaded_file)
                    logger.info(f"已删除下载的zip文件: {downloaded_file}")
                else:
                    logger.warning(f"下载的zip文件不存在: {downloaded_file}")
            else:
                logger.debug(f"无需清理下载文件: {downloaded_file}")
            
            # 清理临时解压目录
            if temp_extract_dir:
                logger.debug(f"检查临时解压目录是否存在: {os.path.exists(temp_extract_dir)}")
                if os.path.exists(temp_extract_dir):
                    logger.info(f"正在清理临时解压目录: {temp_extract_dir}")
                    import shutil
                    shutil.rmtree(temp_extract_dir)
                    logger.info(f"已清理临时解压目录: {temp_extract_dir}")
                else:
                    logger.warning(f"临时解压目录不存在: {temp_extract_dir}")
            else:
                logger.debug(f"无需清理临时解压目录")
                
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")
            logger.error(traceback.format_exc())
    
    def simulate_install_steps(self):
        """模拟安装步骤"""
        logger.info(f"开始模拟安装步骤")
        
        steps = [
            ("正在创建安装目录...", 10),
            ("正在复制文件...", 30),
            ("正在注册组件...", 50),
            ("正在创建快捷方式...", 70),
            ("正在完成安装...", 90),
            ("安装完成！", 100)
        ]
        
        for step_text, progress in steps:
            logger.debug(f"模拟安装步骤: {step_text} (进度: {progress}%)")
            self.install_progress.emit(progress)
            time.sleep(0.5)
            
            if progress == 100:
                logger.info(f"模拟安装步骤完成")
                self.install_complete.emit()
    
    def create_shortcuts(self):
        """创建快捷方式"""
        logger.info(f"开始创建快捷方式")
        
        try:
            install_path = self.install_config.get('install_path', '')
            create_desktop = self.install_config.get('create_desktop_shortcut', False)
            create_start_menu = self.install_config.get('create_start_menu_item', False)
            
            logger.info(f"安装路径: {install_path}")
            logger.info(f"桌面快捷方式: {create_desktop}")
            logger.info(f"开始菜单快捷方式: {create_start_menu}")
            
            if not install_path:
                logger.warning("安装路径为空，无法创建快捷方式")
                return
                
            # 直接使用固定的可执行文件名
            exe_path = os.path.join(install_path, "Bloret-Launcher.exe")
            if not os.path.exists(exe_path):
                logger.error(f"在安装路径中未找到可执行文件: {exe_path}")
                return
                
            logger.info(f"找到可执行文件: {exe_path}")
            
            # 获取应用名称（用于快捷方式名称）
            app_name = self.get_app_name_from_path(exe_path)
            logger.info(f"应用名称: {app_name}")
            
            shortcuts_created = []
            
            # 创建桌面快捷方式
            if create_desktop:
                desktop_path = self.get_desktop_path()
                if desktop_path:
                    shortcut_path = os.path.join(desktop_path, f"{app_name}.lnk")
                    if self.create_windows_shortcut(exe_path, shortcut_path, app_name):
                        shortcuts_created.append("桌面快捷方式")
                        logger.info(f"桌面快捷方式创建成功: {shortcut_path}")
                    else:
                        logger.error("桌面快捷方式创建失败")
                else:
                    logger.error("无法获取桌面路径")
            
            # 创建开始菜单快捷方式
            if create_start_menu:
                start_menu_path = self.get_start_menu_path()
                if start_menu_path:
                    # 直接在Programs目录下创建快捷方式，不创建子文件夹
                    shortcut_path = os.path.join(start_menu_path, f"{app_name}.lnk")
                    if self.create_windows_shortcut(exe_path, shortcut_path, app_name):
                        shortcuts_created.append("开始菜单快捷方式")
                        logger.info(f"开始菜单快捷方式创建成功: {shortcut_path}")
                    else:
                        logger.error("开始菜单快捷方式创建失败")
                else:
                    logger.error("无法获取开始菜单路径")
            
            if shortcuts_created:
                logger.info(f"快捷方式创建完成: {', '.join(shortcuts_created)}")
            else:
                logger.warning("未创建任何快捷方式")
                
        except Exception as e:
            logger.error(f"创建快捷方式失败: {e}")
            logger.error(traceback.format_exc())

    def update_progress(self, value):
        """更新进度条"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(value)
        if hasattr(self, 'progress_label'):
            self.progress_label.setText(f"{value}%")

    def on_install_complete(self):
        """安装完成时的UI更新"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(100)
        if hasattr(self, 'progress_label'):
            self.progress_label.setText("100%")
        if hasattr(self, 'title_label'):
            self.title_label.setText("安装完成\nInstallation Complete")
        if hasattr(self, 'finish_button'):
            self.finish_button.setVisible(True)

    def on_finish_clicked(self):
        """点击完成按钮"""
        QApplication.quit()

    def on_finish_and_open_clicked(self):
        """点击完成并打开按钮"""
        try:
            install_path = self.install_config.get('install_path', '')
            # 1. 展开环境变量（如 %APPDATA%）并获取绝对路径
            abs_install_path = os.path.abspath(os.path.expandvars(install_path))
            exe_path = os.path.join(abs_install_path, "Bloret-Launcher.exe")
            
            logger.info(f"准备启动程序: {exe_path}")
            
            if os.path.exists(exe_path):
                # 2. 使用 os.startfile 启动。
                # 这种方式在 Windows 上最稳妥，相当于“双击”，
                # 自动脱离父进程独立运行，且不会与调试器的 creationflags 产生 [WinError 87] 冲突。
                os.startfile(exe_path)
                logger.info("程序启动指令已通过 Shell 发出")
            else:
                logger.error(f"无法启动程序，文件不存在: {exe_path}")
                
        except Exception as e:
            logger.error(f"启动程序时发生异常: {e}")
            logger.error(traceback.format_exc())
        finally:
            # 3. 稍微延迟一下退出，确保 Shell 指令已成功送达系统
            QTimer.singleShot(200, QApplication.quit)

    def on_install_complete(self):
        """安装完成时的UI更新"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(100)
        if hasattr(self, 'progress_label'):
            self.progress_label.setText("100%")
        if hasattr(self, 'title_label'):
            self.title_label.setText("安装完成 / Installation Complete")
        
        # 显示两个按钮
        self.finish_button.setVisible(True)
        self.finish_open_button.setVisible(True)
    
    def get_app_name_from_path(self, exe_path):
        """从路径获取应用名称"""
        return os.path.splitext(os.path.basename(exe_path))[0]

    def get_desktop_path(self):
        """获取桌面路径"""
        return os.path.join(os.path.expanduser("~"), "Desktop")

    def get_start_menu_path(self):
        """获取开始菜单程序路径"""
        return os.path.join(os.environ.get('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs")

    def create_windows_shortcut(self, target_path, shortcut_path, description):
        """创建 Windows 快捷方式"""
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target_path
            shortcut.WorkingDirectory = os.path.dirname(target_path)
            shortcut.Description = description
            shortcut.IconLocation = target_path
            shortcut.save()
            return True
        except Exception as e:
            logger.error(f"通过 win32com 创建快捷方式失败: {e}")
            try:
                # 备用方案：使用 PowerShell 创建
                ps_script = f'$s=(New-Object -ComObject WScript.Shell).CreateShortcut("{shortcut_path}");$s.TargetPath="{target_path}";$s.Save()'
                import subprocess
                subprocess.run(['powershell', '-Command', ps_script], capture_output=True)
                return True
            except:
                return False


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
        """显示下载进度窗口"""
        logger.info("开始显示下载进度窗口")
        
        # 防止重复创建
        if hasattr(self, 'downloading_dialog') and self.downloading_dialog and self.downloading_dialog.isVisible():
            logger.info("下载对话框已存在并可见，跳过创建")
            self.downloading_dialog.raise_()
            self.downloading_dialog.activateWindow()
            return

        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel, QFrame, QSizePolicy

        # 创建对话框
        self.downloading_dialog = QDialog(self)
        self.downloading_dialog.setWindowTitle("正在下载")
        self.downloading_dialog.setModal(True)
        # 增大窗口尺寸：确保文本换行有空间，避免截断
        self.downloading_dialog.resize(560, 260)

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # 准备内容容器
        card = None
        if QFLUENT_AVAILABLE:
            try:
                from qfluentwidgets import CardWidget, SubtitleLabel, BodyLabel
                card = CardWidget()
                title_label = SubtitleLabel("资源仍在下载中 / The resource is still downloading")
                desc_label = BodyLabel("待资源文件下载完成后，安装将会开始 / The installation will begin once the resource files have finished downloading.")
            except ImportError:
                pass
        
        if card is None:
            card = QFrame()
            card.setFrameStyle(QFrame.Box)
            card.setStyleSheet("QFrame { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 10px; }")
            title_label = QLabel("资源仍在下载中 / The resource is still downloading")
            title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            desc_label = QLabel("待资源文件下载完成后，安装将会开始 / The installation will begin once the resource files have finished downloading.")
            desc_label.setStyleSheet("color: #666;")

        # 启用自动换行，防止文字挤在一起
        title_label.setWordWrap(True)
        desc_label.setWordWrap(True)

        # 容器布局
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        
        # 添加弹簧，把进度条推到底部
        card_layout.addStretch(1)

        # 使用标准 QProgressBar：确保即使在高频信号下也能可靠刷新
        self.download_progress_bar = QProgressBar()
        self.download_progress_bar.setRange(0, 100)
        self.download_progress_bar.setValue(0)
        # 隐藏进度条自带的、位于末尾且容易截断的百分比文字
        self.download_progress_bar.setTextVisible(False)
        # 稍微美化一下原生进度条颜色
        self.download_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #f0f0f0;
                height: 12px;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        
        card_layout.addWidget(self.download_progress_bar)

        # 进度文本标签（右对齐）
        self.download_progress_label = QLabel("0%")
        self.download_progress_label.setAlignment(Qt.AlignRight)
        if QFLUENT_AVAILABLE:
            font = self.download_progress_label.font()
            self.download_progress_label.setFont(font)
        
        card_layout.addWidget(self.download_progress_label)
        
        card.setLayout(card_layout)
        main_layout.addWidget(card)
        self.downloading_dialog.setLayout(main_layout)

        # 居中显示
        self.downloading_dialog.move(
            self.x() + (self.width() - self.downloading_dialog.width()) // 2,
            self.y() + (self.height() - self.downloading_dialog.height()) // 2
        )
        
        self.downloading_dialog.show()
        logger.info("下载进度窗口（稳定版）已显示")
    def update_download_progress(self, progress):
        """更新下载进度"""
        # logger.info(f"更新进度: {progress}%") # 减少日志频率，避免IO阻塞影响UI流畅度
        
        if self.downloading_dialog and self.downloading_dialog.isVisible():
            try:
                # 更新进度条
                if hasattr(self, 'download_progress_bar'):
                    self.download_progress_bar.setValue(progress)
                    # 某些情况下显式 update 可以确保 Fluent 组件及时重绘
                    self.download_progress_bar.update()
                
                # 更新标签文本
                if hasattr(self, 'download_progress_label'):
                    self.download_progress_label.setText(f"{progress}%")
                
                # 简单地处理事件循环即可，移除之前的过度刷新逻辑
                QApplication.processEvents()
            except Exception as e:
                logger.warning(f"更新进度UI失败: {e}")

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
        logger.info(f"显示错误信息: {error_msg}")
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
        # 逻辑已移至 Page3 内部处理，此处仅做日志记录
        logger.info("安装流程已全部完成")
        
    def show_error(self, message):
        """显示错误信息"""
        if QFLUENT_AVAILABLE:
            InfoBar.error(
                title='错误',
                content=message+"\n请重启 Bloret Launcher Setup 安装程序。",
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