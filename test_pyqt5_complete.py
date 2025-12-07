#!/usr/bin/env python3
"""
PyQt5 完整功能测试脚本
用于验证PyQt5迁移是否完全成功
"""

import sys
import traceback

def test_pyqt5_imports():
    """测试PyQt5导入"""
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox, QFileDialog, QProgressBar, QLabel
        from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
        from PyQt5.QtGui import QIcon, QPixmap
        print("✓ PyQt5 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ PyQt5 导入失败: {e}")
        return False

def test_pyqt5_basic_functionality():
    """测试PyQt5基本功能"""
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox, QProgressBar, QLabel
        from PyQt5.QtCore import Qt, QTimer
        # 创建应用
        app = QApplication(sys.argv)
        
        # 创建主窗口
        window = QMainWindow()
        window.setWindowTitle("PyQt5 测试窗口")
        window.setGeometry(100, 100, 400, 300)
        
        # 创建中央部件
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建标签
        label = QLabel("PyQt5 测试标签")
        label.setAlignment(Qt.AlignCenter)  # 测试Qt.AlignCenter
        layout.addWidget(label)
        
        # 创建进度条
        progress_bar = QProgressBar()
        progress_bar.setValue(50)
        layout.addWidget(progress_bar)
        
        # 创建按钮
        button = QPushButton("测试按钮")
        layout.addWidget(button)
        
        # 测试信号连接
        def on_button_clicked():
            QMessageBox.information(window, "信息", "按钮被点击了！")
        
        button.clicked.connect(on_button_clicked)
        
        # 测试QTimer
        def timer_timeout():
            print("✓ QTimer 正常工作")
        
        timer = QTimer()
        timer.timeout.connect(timer_timeout)
        timer.start(1000)  # 1秒触发一次
        
        # 显示窗口（不阻塞）
        window.show()
        
        # 运行事件循环一小段时间
        QTimer.singleShot(2000, app.quit)  # 2秒后退出
        app.exec_()
        
        print("✓ PyQt5 基本功能测试通过")
        return True
        
    except Exception as e:
        print(f"✗ PyQt5 功能测试失败: {e}")
        traceback.print_exc()
        return False

def test_pyqt5_enums():
    """测试PyQt5枚举类型"""
    try:
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QApplication, QFileDialog
        
        # 测试Qt枚举
        align_center = Qt.AlignCenter
        horizontal = Qt.Horizontal
        
        # 测试QFileDialog枚举
        show_dirs_only = QFileDialog.ShowDirsOnly
        
        print("✓ PyQt5 枚举类型测试通过")
        return True
        
    except Exception as e:
        print(f"✗ PyQt5 枚举类型测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始 PyQt5 完整功能测试...")
    print("=" * 50)
    
    # 测试1: 导入测试
    if not test_pyqt5_imports():
        print("导入测试失败，停止后续测试")
        return False
    
    # 测试2: 枚举类型测试
    if not test_pyqt5_enums():
        print("枚举类型测试失败")
        return False
    
    # 测试3: 基本功能测试
    if not test_pyqt5_basic_functionality():
        print("基本功能测试失败")
        return False
    
    print("=" * 50)
    print("🎉 所有 PyQt5 测试通过！")
    print("PyQt5 迁移验证成功")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)