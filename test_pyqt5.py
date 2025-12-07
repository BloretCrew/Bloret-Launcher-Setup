#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 测试PyQt5导入
    from PyQt5.QtWidgets import QApplication, QLabel
    from PyQt5.QtCore import Qt
    print("✓ PyQt5导入成功")
    
    # 测试基本功能
    app = QApplication(sys.argv)
    label = QLabel("PyQt5测试成功！")
    label.setAlignment(Qt.AlignCenter)
    label.resize(200, 100)
    label.show()
    
    # 自动关闭
    from PyQt5.QtCore import QTimer
    QTimer.singleShot(1000, app.quit)
    
    app.exec_()
    print("✓ PyQt5基本功能测试通过")
    
except ImportError as e:
    print(f"✗ PyQt5导入失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ PyQt5测试失败: {e}")
    sys.exit(1)

print("所有测试通过！")