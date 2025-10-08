#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像处理核心模块
处理图片的加载、格式验证、缩略图生成等功能
"""

import os
from PIL import Image, ImageOps
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import logging

# 支持的图片格式
SUPPORTED_FORMATS = {
    'JPEG': ['.jpg', '.jpeg', '.jpe', '.jfif'],
    'PNG': ['.png'],
    'BMP': ['.bmp', '.dib'],
    'TIFF': ['.tif', '.tiff']
}

# 所有支持的扩展名
ALL_SUPPORTED_EXTENSIONS = []
for extensions in SUPPORTED_FORMATS.values():
    ALL_SUPPORTED_EXTENSIONS.extend(extensions)


class ImageProcessor(QObject):
    """图像处理器类"""
    
    # 信号：图片处理进度
    progress_updated = pyqtSignal(int, str)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def is_supported_format(self, file_path):
        """
        检查文件格式是否支持
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否支持该格式
        """
        if not os.path.isfile(file_path):
            return False
        
        _, ext = os.path.splitext(file_path)
        return ext.lower() in ALL_SUPPORTED_EXTENSIONS
    
    def load_image(self, file_path):
        """
        加载图片
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            tuple: (成功状态, 图片对象或错误信息)
        """
        try:
            if not self.is_supported_format(file_path):
                return False, f"不支持的图片格式: {os.path.splitext(file_path)[1]}"
            
            # 使用PIL加载图片
            image = Image.open(file_path)
            # 转换为RGB模式（如果需要）
            if image.mode in ('RGBA', 'LA'):
                # 保持透明通道
                pass
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            return True, image
            
        except Exception as e:
            self.logger.error(f"加载图片失败 {file_path}: {str(e)}")
            return False, f"加载图片失败: {str(e)}"
    
    def create_thumbnail(self, image, max_size=(200, 150)):
        """
        创建缩略图
        
        Args:
            image: PIL图片对象
            max_size: 最大尺寸 (宽, 高)
            
        Returns:
            QPixmap: 缩略图
        """
        try:
            # 计算缩略图尺寸
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 转换为QPixmap
            if image.mode == 'RGB':
                q_image = QImage(image.tobytes(), image.width, image.height, 
                                image.width * 3, QImage.Format_RGB888)
            elif image.mode == 'RGBA':
                q_image = QImage(image.tobytes(), image.width, image.height, 
                                image.width * 4, QImage.Format_RGBA8888)
            else:
                image = image.convert('RGB')
                q_image = QImage(image.tobytes(), image.width, image.height, 
                                image.width * 3, QImage.Format_RGB888)
            
            return QPixmap.fromImage(q_image)
            
        except Exception as e:
            self.logger.error(f"创建缩略图失败: {str(e)}")
            # 返回一个默认的错误缩略图
            return QPixmap(max_size[0], max_size[1])
    
    def get_image_info(self, file_path):
        """
        获取图片信息
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            dict: 图片信息
        """
        try:
            with Image.open(file_path) as img:
                info = {
                    'file_name': os.path.basename(file_path),
                    'file_path': file_path,
                    'file_size': os.path.getsize(file_path),
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode
                }
                return info
        except Exception as e:
            self.logger.error(f"获取图片信息失败 {file_path}: {str(e)}")
            return None