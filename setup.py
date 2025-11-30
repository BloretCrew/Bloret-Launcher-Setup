#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import os

def install_requirements():
    """安装依赖包"""
    print("正在检查并安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖安装完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False

def check_python_version():
    """检查 Python 版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要 Python 3.8 或更高版本")
        return False
    return True

def main():
    """主函数"""
    print("Bloret Launcher 安装向导设置程序")
    print("=" * 40)
    
    # 检查 Python 版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装依赖
    if not install_requirements():
        print("请手动安装依赖后重试")
        sys.exit(1)
    
    print("\n设置完成！现在可以运行安装向导了。")
    print("运行命令: python installer.py")
    print("或者双击 run_installer.bat")
    
    # 询问是否立即运行
    response = input("\n是否立即运行安装向导? (y/n): ").lower()
    if response == 'y':
        subprocess.run([sys.executable, "installer.py"])

if __name__ == "__main__":
    main()