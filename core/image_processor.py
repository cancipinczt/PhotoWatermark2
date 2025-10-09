#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像处理核心模块
处理图片的加载、格式验证、缩略图生成等功能
"""

import os
from PIL import Image, ImageOps, ImageDraw, ImageFont
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

    def add_text_watermark(self, image, text, position='右下角', opacity=50, font='Arial', 
                          font_size=24, bold=False, italic=False, color='白色',
                          shadow=False, stroke=False):
        """
        为图片添加文本水印
        
        Args:
            image: PIL图片对象
            text: 水印文本内容
            position: 水印位置 ('左上角', '右上角', '左下角', '右下角', '正中心', 
                     '顶部居中', '底部居中', '左侧居中', '右侧居中')
            opacity: 透明度 (0-100)
            font: 字体名称
            font_size: 字号
            bold: 是否粗体
            italic: 是否斜体
            color: 颜色名称 ('白色', '黑色', '红色', '蓝色', '绿色', '黄色', '自定义')
            shadow: 是否启用阴影效果
            stroke: 是否启用描边效果
            
        Returns:
            PIL.Image: 添加水印后的图片
        """
        try:
            if not text:
                return image
            
            # 创建图片副本
            watermarked_image = image.copy()
            
            # 创建绘图对象
            draw = ImageDraw.Draw(watermarked_image)
            
            # 获取图片尺寸
            img_width, img_height = watermarked_image.size
            
            # 获取字体
            font_obj = self._get_font(font, font_size, bold, italic)
            if not font_obj:
                self.logger.warning(f"无法加载字体: {font}，使用默认字体")
                font_obj = ImageFont.load_default()
            
            # 获取文本尺寸
            bbox = draw.textbbox((0, 0), text, font=font_obj)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 计算水印位置
            x, y = self._calculate_text_position(position, img_width, img_height, text_width, text_height)
            
            # 设置颜色
            fill_color = self._get_color_value(color)
            
            # 设置透明度
            alpha = int(opacity * 2.55)  # 转换为0-255范围
            
            # 中文斜体模拟：只在文本水印上应用倾斜，而不是整个图片
            if italic and font in ['SimHei', 'Microsoft YaHei', 'SimSun']:
                # 创建只包含文本的临时图像用于倾斜变换
                text_image = Image.new('RGBA', (text_width + 50, text_height + 50), (0, 0, 0, 0))
                text_draw = ImageDraw.Draw(text_image)
                
                # 绘制文本到临时图像
                text_draw.text((25, 25), text, font=font_obj, fill=fill_color + (alpha,))
                
                # 使用PIL的transform方法进行更平滑的倾斜变换
                shear_factor = 0.25  # 倾斜程度
                width, height = text_image.size
                
                # 计算变换后的宽度（考虑倾斜）
                new_width = int(width + height * abs(shear_factor))
                
                # 修正倾斜方向：使用正的shear_factor实现上半部分偏右，下半部分偏左
                # 变换矩阵：[1, shear_factor, 0, 0, 1, 0]
                # 正的shear_factor表示向右倾斜（上半部分偏右，下半部分偏左）
                transform_matrix = (1, shear_factor, 0, 0, 1, 0)
                
                # 应用仿射变换，使用高质量的重采样
                sheared_text_image = text_image.transform(
                    (new_width, height),
                    Image.Transform.AFFINE,
                    transform_matrix,
                    resample=Image.Resampling.BICUBIC  # 使用双三次插值获得更平滑效果
                )
                
                # 裁剪掉多余的透明区域
                bbox = sheared_text_image.getbbox()
                if bbox:
                    sheared_text_image = sheared_text_image.crop(bbox)
                    
                    # 将倾斜后的文本图像合并到原图
                    text_width_new = bbox[2] - bbox[0]
                    text_height_new = bbox[3] - bbox[1]
                    
                    # 重新计算位置（考虑倾斜后的尺寸）
                    x_new, y_new = self._calculate_text_position(position, img_width, img_height, text_width_new, text_height_new)
                    
                    # 合并倾斜文本到原图
                    watermarked_image.paste(sheared_text_image, (x_new, y_new), sheared_text_image)
                    
                    self.logger.info(f"对中文字体 {font} 应用平滑模拟斜体效果")
                
                return watermarked_image
            
            # 创建临时图像用于绘制文本（非中文斜体情况）
            temp_image = Image.new('RGBA', watermarked_image.size, (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_image)
            
            # 进一步优化粗体效果：使用更小的偏移量避免粘连
            if bold:
                # 使用更小的偏移量和更少的次数
                offsets = [(0, 0), (0.5, 0), (0, 0.5)]  # 减少偏移量和次数
            else:
                offsets = [(0, 0)]
            
            # 绘制文本（带效果）
            if stroke:
                # 描边效果
                stroke_width = 1  # 减小描边宽度
                for dx in [-stroke_width, 0, stroke_width]:
                    for dy in [-stroke_width, 0, stroke_width]:
                        if dx == 0 and dy == 0:
                            continue
                        for offset_x, offset_y in offsets:
                            temp_draw.text((x + dx + offset_x, y + dy + offset_y), text, 
                                         font=font_obj, fill=(0, 0, 0, alpha))
            
            if shadow:
                # 阴影效果
                shadow_offset = 2
                for offset_x, offset_y in offsets:
                    temp_draw.text((x + shadow_offset + offset_x, y + shadow_offset + offset_y), 
                                 text, font=font_obj, fill=(0, 0, 0, alpha // 2))
            
            # 主文本 - 优化粗体效果
            for offset_x, offset_y in offsets:
                temp_draw.text((x + offset_x, y + offset_y), text, 
                             font=font_obj, fill=fill_color + (alpha,))
            
            # 合并图像
            watermarked_image = Image.alpha_composite(
                watermarked_image.convert('RGBA'), temp_image
            )
            
            return watermarked_image
            
        except Exception as e:
            self.logger.error(f"添加文本水印失败: {str(e)}")
            return image

    def export_image_with_watermark(self, image, output_path, output_format='JPEG', quality=95,
                                  resize_width=None, resize_height=None, resize_percent=None,
                                  text='', position='右下角', opacity=50, font='Arial', 
                                  font_size=24, bold=False, italic=False, color='白色',
                                  shadow=False, stroke=False):
        """
        导出带文本水印的图片
        
        Args:
            image: PIL图片对象
            output_path: 输出文件路径
            output_format: 输出格式
            quality: JPEG质量
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
            bool: 是否成功导出
        """
        try:
            # 处理图片缩放
            processed_image = image.copy()
            
            if resize_width or resize_height or resize_percent:
                # 计算目标尺寸
                original_width, original_height = processed_image.size
                
                if resize_percent:
                    # 按百分比缩放
                    scale_factor = resize_percent / 100.0
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)
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
            
            # 添加文本水印
            if text:
                processed_image = self.add_text_watermark(
                    processed_image, text, position, opacity, font, font_size, 
                    bold, italic, color, shadow, stroke
                )
            
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
            self.logger.info(f"成功导出带水印图片: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出带水印图片失败 {output_path}: {str(e)}")
            return False

    def _calculate_text_position(self, position, img_width, img_height, text_width, text_height):
        """
        计算文本位置
        
        Args:
            position: 位置名称
            img_width: 图片宽度
            img_height: 图片高度
            text_width: 文本宽度
            text_height: 文本高度
            
        Returns:
            tuple: (x, y) 坐标
        """
        margin = 20  # 边距
        
        if position == '左上角':
            return margin, margin
        elif position == '右上角':
            return img_width - text_width - margin, margin
        elif position == '左下角':
            return margin, img_height - text_height - margin
        elif position == '右下角':
            return img_width - text_width - margin, img_height - text_height - margin
        elif position == '正中心':
            return (img_width - text_width) // 2, (img_height - text_height) // 2
        elif position == '顶部居中':
            return (img_width - text_width) // 2, margin
        elif position == '底部居中':
            return (img_width - text_width) // 2, img_height - text_height - margin
        elif position == '左侧居中':
            return margin, (img_height - text_height) // 2
        elif position == '右侧居中':
            return img_width - text_width - margin, (img_height - text_height) // 2
        else:
            # 默认右下角
            return img_width - text_width - margin, img_height - text_height - margin

    def _get_font(self, font_name, font_size, bold=False, italic=False):
        """
        获取字体对象
        
        Args:
            font_name: 字体名称
            font_size: 字号
            bold: 是否粗体
            italic: 是否斜体
            
        Returns:
            ImageFont: 字体对象
        """
        try:
            # 改进的字体映射，包含更多字体变体和备用选项
            font_mapping = {
                'Arial': {
                    'normal': ['arial.ttf', 'ariali.ttf'],
                    'bold': ['arialbd.ttf', 'arialbi.ttf'],
                    'italic': ['ariali.ttf', 'arial.ttf'],
                    'bold_italic': ['arialbi.ttf', 'arialbd.ttf']
                },
                'Times New Roman': {
                    'normal': ['times.ttf', 'timesi.ttf'],
                    'bold': ['timesbd.ttf', 'timesbi.ttf'],
                    'italic': ['timesi.ttf', 'times.ttf'],
                    'bold_italic': ['timesbi.ttf', 'timesbd.ttf']
                },
                'SimHei': {
                    'normal': ['simhei.ttf'],
                    'bold': ['simhei.ttf'],  # 黑体本身就是粗体
                    'italic': ['simhei.ttf'],  # 中文字体不支持斜体，在add_text_watermark中模拟
                    'bold_italic': ['simhei.ttf']
                },
                'Microsoft YaHei': {
                    'normal': ['msyh.ttc', 'msyh.ttf'],
                    'bold': ['msyhbd.ttc', 'msyhbd.ttf'],
                    'italic': ['msyh.ttc', 'msyh.ttf'],  # 中文字体不支持斜体，在add_text_watermark中模拟
                    'bold_italic': ['msyhbd.ttc', 'msyhbd.ttf']
                },
                'SimSun': {
                    'normal': ['simsun.ttc', 'simsun.ttf'],
                    'bold': ['simsunb.ttf', 'simsun.ttc'],
                    'italic': ['simsun.ttc', 'simsun.ttf'],  # 中文字体不支持斜体，在add_text_watermark中模拟
                    'bold_italic': ['simsunb.ttf', 'simsun.ttc']
                }
            }
            
            # 确定字体样式
            if bold and italic:
                style_key = 'bold_italic'
            elif bold:
                style_key = 'bold'
            elif italic:
                style_key = 'italic'
            else:
                style_key = 'normal'
            
            # 改进的字体文件查找逻辑
            font_path = None
            if font_name in font_mapping:
                # 获取该样式的所有可能字体文件
                font_files = font_mapping[font_name].get(style_key, font_mapping[font_name]['normal'])
                
                # 在系统字体目录中查找
                system_font_dirs = [
                    'C:/Windows/Fonts',
                    'C:/Windows/Fonts/truetype',
                    '/usr/share/fonts',
                    '/Library/Fonts'
                ]
                
                # 遍历所有可能的字体文件
                for font_file in font_files:
                    for font_dir in system_font_dirs:
                        if os.path.exists(font_dir):
                            font_path = os.path.join(font_dir, font_file)
                            if os.path.exists(font_path):
                                self.logger.info(f"成功加载字体: {font_path}")
                                break
                            else:
                                font_path = None
                    if font_path:
                        break
                
                # 如果特定样式字体不存在，尝试使用普通字体
                if not font_path:
                    normal_files = font_mapping[font_name]['normal']
                    for font_file in normal_files:
                        for font_dir in system_font_dirs:
                            if os.path.exists(font_dir):
                                font_path = os.path.join(font_dir, font_file)
                                if os.path.exists(font_path):
                                    self.logger.warning(f"字体样式 {style_key} 不可用，使用普通字体")
                                    break
                                else:
                                    font_path = None
                        if font_path:
                            break
            
            if font_path and os.path.exists(font_path):
                # 加载字体文件
                font = ImageFont.truetype(font_path, font_size, encoding='utf-8')
                # 对于中文字体，记录需要模拟斜体
                if italic and font_name in ['SimHei', 'Microsoft YaHei', 'SimSun']:
                    self.logger.info(f"中文字体 {font_name} 将应用模拟斜体效果")
                return font
            else:
                # 使用默认字体（不支持样式）
                self.logger.warning(f"无法加载字体 {font_name}，使用默认字体")
                return ImageFont.load_default()
                
        except Exception as e:
            self.logger.warning(f"无法加载字体 {font_name}: {str(e)}")
            return ImageFont.load_default()
    def _get_color_value(self, color_name):
        """
        获取颜色值
        
        Args:
            color_name: 颜色名称或RGB元组
            
        Returns:
            tuple: (R, G, B) 颜色值
        """
        # 如果传入的是RGB元组，直接返回
        if isinstance(color_name, tuple) and len(color_name) == 3:
            return color_name
        
        color_map = {
            '白色': (255, 255, 255),
            '黑色': (0, 0, 0),
            '红色': (255, 0, 0),
            '蓝色': (0, 0, 255),
            '绿色': (0, 255, 0),
            '黄色': (255, 255, 0)
        }
        
        return color_map.get(color_name, (255, 255, 255))  # 默认白色