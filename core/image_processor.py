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
            # 创建图像的副本，避免修改原始图像
            thumbnail_image = image.copy()
            
            # 计算缩略图尺寸
            thumbnail_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 转换为QPixmap
            if thumbnail_image.mode == 'RGB':
                q_image = QImage(thumbnail_image.tobytes(), thumbnail_image.width, thumbnail_image.height, 
                                thumbnail_image.width * 3, QImage.Format_RGB888)
            elif thumbnail_image.mode == 'RGBA':
                q_image = QImage(thumbnail_image.tobytes(), thumbnail_image.width, thumbnail_image.height, 
                                thumbnail_image.width * 4, QImage.Format_RGBA8888)
            else:
                thumbnail_image = thumbnail_image.convert('RGB')
                q_image = QImage(thumbnail_image.tobytes(), thumbnail_image.width, thumbnail_image.height, 
                                thumbnail_image.width * 3, QImage.Format_RGB888)
            
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

    def export_image(self, image, output_path, output_format='JPEG', quality=95, 
                    resize_width=None, resize_height=None, resize_percent=None):
        """
        导出图片
        
        Args:
            image: PIL图片对象
            output_path: 输出文件路径
            output_format: 输出格式 ('JPEG', 'PNG')
            quality: JPEG质量 (0-100)
            resize_width: 按宽度缩放
            resize_height: 按高度缩放
            resize_percent: 按百分比缩放
            
        Returns:
            bool: 是否成功导出
        """
        try:
            # 检查输出路径是否与原路径相同
            if os.path.abspath(output_path) == os.path.abspath(getattr(image, 'filename', '')):
                raise ValueError("禁止导出到原文件路径")
            
            # 处理图片缩放
            processed_image = image.copy()
            
            if resize_width or resize_height or resize_percent:
                # 计算目标尺寸
                original_width, original_height = processed_image.size
                
                # 添加调试信息
                self.logger.info(f"原始尺寸: {original_width}x{original_height}")
                self.logger.info(f"缩放参数 - 宽度: {resize_width}, 高度: {resize_height}, 百分比: {resize_percent}")
                
                if resize_percent:
                    # 按百分比缩放 - 修复计算逻辑
                    scale_factor = resize_percent / 100.0
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)
                    
                    self.logger.info(f"百分比缩放: {resize_percent}% -> 缩放因子: {scale_factor}")
                    self.logger.info(f"目标尺寸: {new_width}x{new_height}")
                    
                elif resize_width and resize_height:
                    # 同时指定宽高
                    new_width = resize_width
                    new_height = resize_height
                elif resize_width:
                    # 按宽度缩放，保持宽高比
                    ratio = resize_width / original_width
                    new_width = resize_width
                    new_height = int(original_height * ratio)
                elif resize_height:
                    # 按高度缩放，保持宽高比
                    ratio = resize_height / original_height
                    new_width = int(original_width * ratio)
                    new_height = resize_height
                
                # 执行缩放
                processed_image = processed_image.resize(
                    (new_width, new_height), Image.Resampling.LANCZOS
                )
                
                self.logger.info(f"缩放后尺寸: {processed_image.size}")
            
            # 设置保存参数
            save_kwargs = {}
            if output_format.upper() == 'JPEG':
                save_kwargs['quality'] = max(0, min(100, quality))
                # JPEG不支持透明通道，转换为RGB
                if processed_image.mode in ('RGBA', 'LA', 'P'):
                    processed_image = processed_image.convert('RGB')
            elif output_format.upper() == 'PNG':
                # PNG保持透明通道
                if processed_image.mode == 'RGB':
                    processed_image = processed_image.convert('RGBA')
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存图片
            processed_image.save(output_path, format=output_format, **save_kwargs)
            self.logger.info(f"成功导出图片: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出图片失败 {output_path}: {str(e)}")
            return False

    def generate_output_filename(self, original_filename, prefix='', suffix='_watermarked', 
                               output_format='JPEG'):
        """
        生成输出文件名
        
        Args:
            original_filename: 原文件名
            prefix: 文件名前缀
            suffix: 文件名后缀
            output_format: 输出格式
            
        Returns:
            str: 生成的输出文件名
        """
        # 分离文件名和扩展名
        name, ext = os.path.splitext(original_filename)
        
        # 根据输出格式确定新扩展名
        if output_format.upper() == 'JPEG':
            new_ext = '.jpg'
        elif output_format.upper() == 'PNG':
            new_ext = '.png'
        else:
            new_ext = ext  # 保持原扩展名
        
        # 组合新文件名
        new_filename = f"{prefix}{name}{suffix}{new_ext}"
        return new_filename