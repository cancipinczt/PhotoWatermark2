#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用程序启动诊断脚本
"""

import sys
import os
import traceback

# 全局导入
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PIL import Image

def test_imports():
    """测试所有必要的导入"""
    print("=== 测试导入 ===")
    
    try:
        print("1. 测试PyQt5导入...")
        # 已经在全局导入，这里只做验证
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        print("   ✓ PyQt5导入成功")
    except ImportError as e:
        print(f"   ✗ PyQt5导入失败: {e}")
        return False
    
    try:
        print("2. 测试PIL导入...")
        # 已经在全局导入，这里只做验证
        img = Image.new('RGB', (100, 100), 'white')
        print("   ✓ PIL导入成功")
    except ImportError as e:
        print(f"   ✗ PIL导入失败: {e}")
        return False
    
    try:
        print("3. 测试项目模块导入...")
        # 添加项目根目录到Python路径
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)
        
        from utils.logger import setup_logging
        from ui.main_window import MainWindow
        print("   ✓ 项目模块导入成功")
    except ImportError as e:
        print(f"   ✗ 项目模块导入失败: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_main_window_creation():
    """测试主窗口创建"""
    print("\n=== 测试主窗口创建 ===")
    
    try:
        # 创建QApplication实例（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        print("1. QApplication创建成功")
        
        # 测试主窗口创建
        print("2. 尝试创建MainWindow...")
        from ui.main_window import MainWindow
        window = MainWindow()
        print("   ✓ MainWindow创建成功")
        
        # 测试窗口显示
        print("3. 尝试显示窗口...")
        window.show()
        print("   ✓ 窗口显示成功")
        
        print("4. 应用程序启动成功！")
        
        # 不退出应用程序，让用户看到窗口
        print("5. 窗口已显示，按Ctrl+C退出测试")
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"   ✗ 主窗口创建失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主诊断函数"""
    print("开始诊断应用程序启动问题...\n")
    
    # 测试导入
    if not test_imports():
        print("\n❌ 导入测试失败，请检查依赖包安装")
        return
    
    # 测试主窗口创建
    if test_main_window_creation():
        print("\n✅ 诊断完成：应用程序可以正常启动")
    else:
        print("\n❌ 诊断完成：应用程序启动失败，请检查错误信息")

if __name__ == "__main__":
    main()