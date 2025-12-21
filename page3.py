#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import threading
import logging
import subprocess
import tempfile
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap
import traceback

from qfluentwidgets import (SmoothScrollArea, TitleLabel, ProgressBar, StrongBodyLabel, 
                            CardWidget, SubtitleLabel, PrimaryPushButton, InfoBar, InfoBarPosition)

# 获取logger
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
            
            # 遍历解压目录
            logger.debug(f"遍历解压目录: {extract_dir}")
            for root, dirs, files in os.walk(extract_dir):
                logger.debug(f"检查目录: {root}")
                logger.debug(f"文件列表: {files}")
                for file in files:
                    file_lower = file.lower()
                    logger.debug(f"检查文件: {file} (小写: {file_lower})")
                    # 检查是否是exe文件且名称匹配常见的安装程序名称
                    if file_lower.endswith('.exe') and any(name in file_lower for name in [n.lower() for n in installer_names]):
                        full_path = os.path.join(root, file)
                        logger.info(f"找到匹配的安装程序: {full_path}")
                        return full_path
                    # 如果是exe文件但不是特定的安装程序名称，也返回第一个exe
                    elif file_lower.endswith('.exe'):
                        full_path = os.path.join(root, file)
                        logger.debug(f"找到exe文件: {full_path}")
                        return full_path
            
            # 如果没找到特定名称的exe，返回第一个exe文件
            logger.debug(f"未找到特定安装程序，返回第一个exe文件")
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.lower().endswith('.exe'):
                        full_path = os.path.join(root, file)
                        logger.info(f"找到第一个exe文件: {full_path}")
                        return full_path
            
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
                
            # 查找可执行文件
            exe_path = self.find_executable_in_install_path(install_path)
            if not exe_path:
                logger.error(f"在安装路径 {install_path} 中未找到可执行文件")
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
    
    def find_executable_in_install_path(self, install_path):
        """在安装路径中查找可执行文件"""
        try:
            logger.debug(f"在安装路径中查找可执行文件: {install_path}")
            
            # 常见的可执行文件名称
            common_exe_names = ['Bloret-Launcher.exe', 'Bloret Launcher.exe', 'BloretLauncher.exe', 
                              'launcher.exe', 'Bloret.exe', 'main.exe']
            
            # 首先检查安装路径本身
            if os.path.isfile(install_path) and install_path.lower().endswith('.exe'):
                logger.debug(f"安装路径本身就是可执行文件: {install_path}")
                return install_path
            
            # 如果是目录，在其中查找
            if os.path.isdir(install_path):
                logger.debug(f"安装路径是目录，在其中查找可执行文件")
                
                # 优先查找常见的可执行文件名称
                for exe_name in common_exe_names:
                    exe_path = os.path.join(install_path, exe_name)
                    if os.path.exists(exe_path):
                        logger.debug(f"找到匹配的可执行文件: {exe_path}")
                        return exe_path
                
                # 如果没找到特定名称的，返回第一个exe文件
                for root, dirs, files in os.walk(install_path):
                    for file in files:
                        if file.lower().endswith('.exe'):
                            exe_path = os.path.join(root, file)
                            logger.debug(f"找到可执行文件: {exe_path}")
                            return exe_path
            
            logger.warning(f"在安装路径 {install_path} 中未找到可执行文件")
            return None
            
        except Exception as e:
            logger.error(f"查找可执行文件失败: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def get_app_name_from_path(self, exe_path):
        """从可执行文件路径获取应用名称"""
        try:
            # 从文件名获取名称（不含扩展名）
            base_name = os.path.splitext(os.path.basename(exe_path))[0]
            
            # 如果是Bloret相关的，返回Bloret Launcher
            if 'bloret' in base_name.lower():
                return "Bloret Launcher"
            
            # 否则返回格式化后的名称
            return base_name.replace('-', ' ').replace('_', ' ').title()
            
        except Exception as e:
            logger.error(f"获取应用名称失败: {e}")
            return "Application"
    
    def get_desktop_path(self):
        """获取桌面路径"""
        try:
            import winreg
            
            # 通过注册表获取桌面路径
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
            winreg.CloseKey(key)
            
            logger.debug(f"桌面路径: {desktop_path}")
            return desktop_path
            
        except Exception as e:
            logger.error(f"获取桌面路径失败: {e}")
            #  fallback到常见路径
            try:
                desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
                if os.path.exists(desktop_path):
                    return desktop_path
                else:
                    # 尝试中文桌面路径
                    desktop_path = os.path.join(os.environ['USERPROFILE'], '桌面')
                    if os.path.exists(desktop_path):
                        return desktop_path
            except Exception as e2:
                logger.error(f"fallback获取桌面路径失败: {e2}")
            return None
    
    def get_start_menu_path(self):
        """获取开始菜单路径"""
        try:
            import winreg
            
            # 通过注册表获取开始菜单路径
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            start_menu_path = winreg.QueryValueEx(key, "Programs")[0]
            winreg.CloseKey(key)
            
            logger.debug(f"开始菜单路径: {start_menu_path}")
            return start_menu_path
            
        except Exception as e:
            logger.error(f"获取开始菜单路径失败: {e}")
            # fallback到常见路径
            try:
                start_menu_path = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
                if os.path.exists(start_menu_path):
                    return start_menu_path
            except Exception as e2:
                logger.error(f"fallback获取开始菜单路径失败: {e2}")
            return None
    
    def create_windows_shortcut(self, target_path, shortcut_path, description=""):
        """创建Windows快捷方式"""
        try:
            logger.debug(f"创建快捷方式: 目标={target_path}, 路径={shortcut_path}, 描述={description}")
            
            # 使用Windows Script Host创建快捷方式
            import win32com.client
            
            shell = win32com.client.Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target_path
            shortcut.WorkingDirectory = os.path.dirname(target_path)
            shortcut.IconLocation = target_path
            if description:
                shortcut.Description = description
            shortcut.save()
            
            logger.debug(f"快捷方式创建成功: {shortcut_path}")
            return True
            
        except Exception as e:
            logger.error(f"创建快捷方式失败: {e}")
            
            # 如果win32com不可用，尝试使用简单的批处理文件方法
            try:
                logger.debug("尝试使用批处理方法创建快捷方式")
                return self.create_shortcut_with_bat(target_path, shortcut_path, description)
            except Exception as e2:
                logger.error(f"批处理方法也失败: {e2}")
                return False
    
    def create_shortcut_with_bat(self, target_path, shortcut_path, description=""):
        """使用批处理文件方法创建快捷方式（备用方案）"""
        try:
            # 创建临时批处理文件来创建快捷方式
            bat_content = f"""
@echo off
setlocal enabledelayedexpansion
set "target={target_path}"
set "shortcut={shortcut_path}"
set "desc={description}"

if not exist "%target%" (
    echo 目标文件不存在: %target%
    exit /b 1
)

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%shortcut%'); $s.TargetPath = '%target%'; $s.WorkingDirectory = Split-Path -Parent '%target%'; $s.IconLocation = '%target%'; $s.Description = '%desc%'; $s.Save()"

if %errorlevel% equ 0 (
    echo 快捷方式创建成功
    exit /b 0
) else (
    echo 快捷方式创建失败
    exit /b 1
)
"""
            
            # 创建临时批处理文件
            import tempfile
            bat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False)
            bat_file.write(bat_content)
            bat_file.close()
            
            try:
                # 执行批处理文件
                result = subprocess.run([bat_file.name], capture_output=True, text=True, timeout=30)
                success = result.returncode == 0
                
                if success:
                    logger.debug(f"批处理方法创建快捷方式成功: {shortcut_path}")
                else:
                    logger.error(f"批处理方法创建快捷方式失败: {result.stderr}")
                
                return success
                
            finally:
                # 清理临时批处理文件
                try:
                    os.unlink(bat_file.name)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"批处理方法创建快捷方式失败: {e}")
            return False
            
    def update_progress(self, value):
        """更新进度条"""
        logger.debug(f"更新进度条: {value}%")
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
        logger.info("显示安装成功")
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
        logger.error(f"显示安装错误: {error_msg}")
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

    def apply_theme(self, is_dark=None):
        """应用主题到页面"""
        if is_dark is None:
            from installer import is_dark_theme
            is_dark = is_dark_theme()

        # 页面已经使用QFluentWidgets组件，它们会自动跟随主题
        # 这里可以添加额外的主题特定样式调整
        if is_dark:
            self.setStyleSheet("""
                Page3 {
                    background-color: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                Page3 {
                    background-color: transparent;
                }
            """)