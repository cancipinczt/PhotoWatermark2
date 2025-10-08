#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志配置模块
"""

import logging
import os


def setup_logging():
    """设置日志配置"""
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'photowatermark2.log')),
            logging.StreamHandler()
        ]
    )