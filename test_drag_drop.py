#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试拖拽功能
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def test_drag_drop():
    """测试拖拽功能"""
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 检查拖拽支持
    print(f"MainWindow accepts drops: {window.acceptDrops()}")
    print(f"Central widget accepts drops: {window.centralWidget().acceptDrops()}")
    print(f"Image list widget accepts drops: {window.image_list.acceptDrops()}")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_drag_drop()