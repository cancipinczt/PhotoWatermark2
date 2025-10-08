#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用程序启动脚本
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from utils.logger import setup_logging


if __name__ == "__main__":
    # 设置日志
    setup_logging()
    
    # 导入并运行主程序
    from main import main
    main()