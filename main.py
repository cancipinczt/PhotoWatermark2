#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PhotoWatermark2 主程序入口
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from ui.main_window import MainWindow


def main():
    """应用程序主函数"""
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("PhotoWatermark2")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AI4SE")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()