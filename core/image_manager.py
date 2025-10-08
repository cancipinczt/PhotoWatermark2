#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图片管理器
管理已导入的图片列表，处理批量导入等功能
"""

import os
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap
import logging

from .image_processor import ImageProcessor


class ImageManager(QObject):
    """图片管理器类"""
    
    # 信号：图片列表更新
    images_updated = pyqtSignal(list)
    # 信号：处理进度
    progress_updated = pyqtSignal(int, str)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.image_processor = ImageProcessor()
        self.images = []  # 存储图片信息列表
        
        # 连接信号
        self.image_processor.progress_updated.connect(self.progress_updated)
    
    def import_single_image(self, file_path):
        """
        导入单张图片
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            bool: 是否成功导入
        """
        try:
            # 检查文件是否存在
            if not os.path.isfile(file_path):
                self.logger.error(f"文件不存在: {file_path}")
                return False
            
            # 检查是否已存在
            if any(img['file_path'] == file_path for img in self.images):
                self.logger.warning(f"图片已存在: {file_path}")
                return True  # 视为成功，但不重复添加
            
            # 获取图片信息
            image_info = self.image_processor.get_image_info(file_path)
            if not image_info:
                return False
            
            # 加载图片并创建缩略图
            success, image = self.image_processor.load_image(file_path)
            if not success:
                return False
            
            # 创建缩略图
            thumbnail = self.image_processor.create_thumbnail(image)
            
            # 添加到图片列表
            image_info['thumbnail'] = thumbnail
            image_info['image_object'] = image  # 保存PIL图像对象
            self.images.append(image_info)
            
            # 发出更新信号
            self.images_updated.emit(self.images)
            
            self.logger.info(f"成功导入图片: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"导入单张图片失败 {file_path}: {str(e)}")
            return False
    
    def import_multiple_images(self, file_paths):
        """
        导入多张图片
        
        Args:
            file_paths: 图片文件路径列表
            
        Returns:
            tuple: (成功数量, 失败数量)
        """
        success_count = 0
        fail_count = 0
        
        total = len(file_paths)
        for i, file_path in enumerate(file_paths):
            # 更新进度
            progress = int((i / total) * 100)
            self.progress_updated.emit(progress, f"正在导入图片 {i+1}/{total}")
            
            if self.import_single_image(file_path):
                success_count += 1
            else:
                fail_count += 1
                self.logger.error(f"导入失败: {file_path}")
        
        # 完成进度
        self.progress_updated.emit(100, f"导入完成: 成功 {success_count} 张，失败 {fail_count} 张")
        
        return success_count, fail_count
    
    def import_folder(self, folder_path):
        """
        导入文件夹中的所有图片
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            tuple: (成功数量, 失败数量)
        """
        try:
            if not os.path.isdir(folder_path):
                self.logger.error(f"文件夹不存在: {folder_path}")
                return 0, 0
            
            # 获取文件夹中所有支持的图片文件
            image_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.image_processor.is_supported_format(file_path):
                        image_files.append(file_path)
            
            self.logger.info(f"在文件夹 {folder_path} 中找到 {len(image_files)} 张图片")
            
            # 导入所有图片
            return self.import_multiple_images(image_files)
            
        except Exception as e:
            self.logger.error(f"导入文件夹失败 {folder_path}: {str(e)}")
            return 0, 0
    
    def remove_image(self, file_path):
        """
        从列表中移除图片
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            bool: 是否成功移除
        """
        try:
            # 查找并移除图片
            for i, img_info in enumerate(self.images):
                if img_info['file_path'] == file_path:
                    # 释放图像资源
                    if 'image_object' in img_info:
                        img_info['image_object'].close()
                    
                    self.images.pop(i)
                    self.images_updated.emit(self.images)
                    self.logger.info(f"已移除图片: {file_path}")
                    return True
            
            self.logger.warning(f"图片不在列表中: {file_path}")
            return False
            
        except Exception as e:
            self.logger.error(f"移除图片失败 {file_path}: {str(e)}")
            return False
    
    def clear_all_images(self):
        """清空所有图片"""
        try:
            # 释放所有图像资源
            for img_info in self.images:
                if 'image_object' in img_info:
                    img_info['image_object'].close()
            
            self.images.clear()
            self.images_updated.emit(self.images)
            self.logger.info("已清空所有图片")
            
        except Exception as e:
            self.logger.error(f"清空图片失败: {str(e)}")
    
    def get_image_count(self):
        """获取图片数量"""
        return len(self.images)
    
    def get_image_by_path(self, file_path):
        """
        根据文件路径获取图片信息
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            dict: 图片信息，如果不存在返回None
        """
        for img_info in self.images:
            if img_info['file_path'] == file_path:
                return img_info
        return None