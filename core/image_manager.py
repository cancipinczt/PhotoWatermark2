#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图片管理器
管理已导入的图片列表，处理批量导入等功能
"""

import os
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon  # 添加QIcon导入
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
            
            # 创建缩略图并转换为QIcon
            thumbnail_pixmap = self.image_processor.create_thumbnail(image)
            thumbnail_icon = QIcon(thumbnail_pixmap)
            
            # 添加到图片列表
            image_info['thumbnail'] = thumbnail_icon  # 存储QIcon对象
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

    def export_single_image(self, file_path, output_dir, output_format='JPEG', 
                          quality=95, prefix='', suffix='_watermarked',
                          resize_width=None, resize_height=None, resize_percent=None):
        """
        导出单张图片
        
        Args:
            file_path: 原图片文件路径
            output_dir: 输出目录
            output_format: 输出格式
            quality: JPEG质量
            prefix: 文件名前缀
            suffix: 文件名后缀
            resize_width: 缩放宽度
            resize_height: 缩放高度
            resize_percent: 缩放百分比
            
        Returns:
            tuple: (是否成功, 输出文件路径或错误信息)
        """
        try:
            # 获取图片信息
            img_info = self.get_image_by_path(file_path)
            if not img_info:
                return False, "图片不在列表中"
            
            # 检查输出目录是否与原目录相同
            if os.path.abspath(output_dir) == os.path.abspath(os.path.dirname(file_path)):
                return False, "禁止导出到原文件夹"
            
            # 生成输出文件名
            output_filename = self.image_processor.generate_output_filename(
                img_info['file_name'], prefix, suffix, output_format
            )
            output_path = os.path.join(output_dir, output_filename)
            
            # 导出图片
            if 'image_object' in img_info:
                success = self.image_processor.export_image(
                    img_info['image_object'], output_path, output_format, quality,
                    resize_width, resize_height, resize_percent
                )
            else:
                # 如果图像对象不存在，重新加载图片
                success, image = self.image_processor.load_image(file_path)
                if success:
                    success = self.image_processor.export_image(
                        image, output_path, output_format, quality,
                        resize_width, resize_height, resize_percent
                    )
                    image.close()
                else:
                    return False, "无法加载图片"
            
            return success, output_path if success else "导出失败"
            
        except Exception as e:
            self.logger.error(f"导出单张图片失败 {file_path}: {str(e)}")
            return False, str(e)

    def export_multiple_images(self, file_paths, output_dir, output_format='JPEG', 
                             quality=95, prefix='', suffix='_watermarked',
                             resize_width=None, resize_height=None, resize_percent=None):
        """
        批量导出图片
        
        Args:
            file_paths: 图片文件路径列表
            output_dir: 输出目录
            output_format: 输出格式
            quality: JPEG质量
            prefix: 文件名前缀
            suffix: 文件名后缀
            resize_width: 缩放宽度
            resize_height: 缩放高度
            resize_percent: 缩放百分比
            
        Returns:
            tuple: (成功数量, 失败数量, 详细结果列表)
        """
        success_count = 0
        fail_count = 0
        results = []
        
        total = len(file_paths)
        for i, file_path in enumerate(file_paths):
            # 更新进度
            progress = int((i / total) * 100)
            self.progress_updated.emit(progress, f"正在导出图片 {i+1}/{total}")
            
            # 导出单张图片
            success, result = self.export_single_image(
                file_path, output_dir, output_format, quality, prefix, suffix,
                resize_width, resize_height, resize_percent
            )
            
            if success:
                success_count += 1
                results.append((file_path, result, "成功"))
            else:
                fail_count += 1
                results.append((file_path, None, result))
        
        # 完成进度
        self.progress_updated.emit(100, f"导出完成: 成功 {success_count} 张，失败 {fail_count} 张")
        
        return success_count, fail_count, results

    def export_single_image_with_watermark(self, file_path, output_dir, output_format='JPEG', 
                                        quality=95, prefix='', suffix='_watermarked',
                                        resize_width=None, resize_height=None, resize_percent=None,
                                        text='', position='右下角', opacity=50, font='Arial', 
                                        font_size=24, bold=False, italic=False, color='白色',
                                        shadow=False, stroke=False):
        """
        导出带文本水印的单张图片
        
        Args:
            file_path: 原图片文件路径
            output_dir: 输出目录
            output_format: 输出格式
            quality: JPEG质量
            prefix: 文件名前缀
            suffix: 文件名后缀
            resize_width: 缩放宽度
            resize_height: 缩放高度
            resize_percent: 缩放百分比
            text: 水印文本内容
            position: 水印位置
            opacity: 透明度
            font: 字体名称
            font_size: 字号
            bold: 是否粗体
            italic: 是否斜体
            color: 颜色名称
            shadow: 是否启用阴影
            stroke: 是否启用描边
            
        Returns:
            tuple: (是否成功, 输出文件路径或错误信息)
        """
        try:
            # 获取图片信息
            img_info = self.get_image_by_path(file_path)
            if not img_info:
                return False, "图片不在列表中"
            
            # 检查输出目录是否与原目录相同
            if os.path.abspath(output_dir) == os.path.abspath(os.path.dirname(file_path)):
                return False, "禁止导出到原文件夹"
            
            # 生成输出文件名
            output_filename = self.image_processor.generate_output_filename(
                img_info['file_name'], prefix, suffix, output_format
            )
            output_path = os.path.join(output_dir, output_filename)
            
            # 导出带水印的图片
            if 'image_object' in img_info:
                success = self.image_processor.export_image_with_watermark(
                    img_info['image_object'], output_path, output_format, quality,
                    resize_width, resize_height, resize_percent,
                    text, position, opacity, font, font_size, bold, italic, color,
                    shadow, stroke
                )
            else:
                # 如果图像对象不存在，重新加载图片
                success, image = self.image_processor.load_image(file_path)
                if success:
                    success = self.image_processor.export_image_with_watermark(
                        image, output_path, output_format, quality,
                        resize_width, resize_height, resize_percent,
                        text, position, opacity, font, font_size, bold, italic, color,
                        shadow, stroke
                    )
                    image.close()
                else:
                    return False, "无法加载图片"
            
            return success, output_path if success else "导出失败"
            
        except Exception as e:
            self.logger.error(f"导出带水印单张图片失败 {file_path}: {str(e)}")
            return False, str(e)

    def export_multiple_images_with_watermark(self, file_paths, output_dir, output_format='JPEG', 
                                            quality=95, prefix='', suffix='_watermarked',
                                            resize_width=None, resize_height=None, resize_percent=None,
                                            text='', position='右下角', opacity=50, font='Arial', 
                                            font_size=24, bold=False, italic=False, color='白色',
                                            shadow=False, stroke=False):
        """
        批量导出带文本水印的图片
        
        Args:
            file_paths: 图片文件路径列表
            output_dir: 输出目录
            output_format: 输出格式
            quality: JPEG质量
            prefix: 文件名前缀
            suffix: 文件名后缀
            resize_width: 缩放宽度
            resize_height: 缩放高度
            resize_percent: 缩放百分比
            text: 水印文本内容
            position: 水印位置
            opacity: 透明度
            font: 字体名称
            font_size: 字号
            bold: 是否粗体
            italic: 是否斜体
            color: 颜色名称
            shadow: 是否启用阴影
            stroke: 是否启用描边
            
        Returns:
            tuple: (成功数量, 失败数量, 详细结果列表)
        """
        success_count = 0
        fail_count = 0
        results = []
        
        total = len(file_paths)
        for i, file_path in enumerate(file_paths):
            # 更新进度
            progress = int((i / total) * 100)
            self.progress_updated.emit(progress, f"正在导出带水印图片 {i+1}/{total}")
            
            # 导出带水印的单张图片
            success, result = self.export_single_image_with_watermark(
                file_path, output_dir, output_format, quality, prefix, suffix,
                resize_width, resize_height, resize_percent,
                text, position, opacity, font, font_size, bold, italic, color,
                shadow, stroke
            )
            
            if success:
                success_count += 1
                results.append((file_path, result, "成功"))
            else:
                fail_count += 1
                results.append((file_path, None, result))
        
        # 完成进度
        self.progress_updated.emit(100, f"带水印导出完成: 成功 {success_count} 张，失败 {fail_count} 张")
        
        return success_count, fail_count, results