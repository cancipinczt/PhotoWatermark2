#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口界面
实现图片导入功能的用户界面
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QListWidget, QListWidgetItem, QLabel, 
                            QFileDialog, QMessageBox, QProgressBar, QSplitter,
                            QFrame, QScrollArea, QComboBox, QSpinBox, QSlider, 
                            QLineEdit, QGroupBox, QCheckBox, QColorDialog)  # 添加QColorDialog导入
from PyQt5.QtCore import Qt, pyqtSlot, QMimeData
from PyQt5.QtGui import QPixmap, QFont, QIcon, QDragEnterEvent, QDropEvent, QDragMoveEvent, QColor  # 添加QColor导入

from core.image_manager import ImageManager


class ImageListWidget(QListWidget):
    """自定义图片列表控件（支持拖拽）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QPixmap(200, 150).size())
        self.setResizeMode(QListWidget.Adjust)
        self.setViewMode(QListWidget.IconMode)
        self.setMovement(QListWidget.Static)
        self.setSpacing(10)
        
        # 启用拖拽支持
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DropOnly)
        
        # 设置拖拽时的样式
        self.normal_style = self.styleSheet()
        self.drag_over_style = """
            QListWidget {
                border: 2px dashed #0078d4;
                background-color: #f0f8ff;
            }
        """
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否有支持的图片文件
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if self.is_supported_image(file_path):
                    # 设置拖拽悬停样式
                    self.setStyleSheet(self.drag_over_style)
                    event.acceptProposedAction()
                    return
            
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        # 恢复正常样式
        self.setStyleSheet(self.normal_style)
        super().dragLeaveEvent(event)
    
    def dragMoveEvent(self, event: QDragMoveEvent):
        """拖拽移动事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """拖拽释放事件"""
        # 删除错误的样式设置代码 - MainWindow不需要恢复样式
        # self.setStyleSheet(self.normal_style)
        
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            image_files = []
            
            for url in urls:
                file_path = url.toLocalFile()
                if self.is_supported_image(file_path):
                    image_files.append(file_path)
            
            if image_files:
                # 直接调用MainWindow的handle_dropped_files方法
                self.handle_dropped_files(image_files)
                event.acceptProposedAction()
                return
        
        event.ignore()
    
    def is_supported_image(self, file_path):
        """检查文件是否为支持的图片格式"""
        if not os.path.isfile(file_path):
            return False
        
        supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
        _, ext = os.path.splitext(file_path)
        return ext.lower() in supported_extensions


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.image_manager = ImageManager()
        self.init_ui()
        self.connect_signals()
        
        # 设置窗口属性
        self.setWindowTitle("PhotoWatermark2 - 图片水印工具")
        self.resize(1200, 800)
        
        # 启用拖拽支持
        self.setAcceptDrops(True)
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 启用中央部件的拖拽支持
        central_widget.setAcceptDrops(True)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板 - 图片列表和控制按钮
        left_panel = self.create_left_panel()
        
        # 右侧面板 - 预览区域
        right_panel = self.create_right_panel()
        
        # 添加到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
    
    def create_left_panel(self):
        """创建左侧面板"""
        left_widget = QWidget()
        layout = QVBoxLayout(left_widget)
        
        # 标题
        title_label = QLabel("图片列表")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # 控制按钮区域
        control_layout = QHBoxLayout()
        
        # 导入按钮
        self.import_single_btn = QPushButton("导入单张")
        self.import_single_btn.setToolTip("导入单张图片")
        self.import_single_btn.clicked.connect(self.import_single_image)
        
        self.import_multiple_btn = QPushButton("导入多张")
        self.import_multiple_btn.setToolTip("导入多张图片")
        self.import_multiple_btn.clicked.connect(self.import_multiple_images)
        
        self.import_folder_btn = QPushButton("导入文件夹")
        self.import_folder_btn.setToolTip("导入整个文件夹的图片")
        self.import_folder_btn.clicked.connect(self.import_folder)
        
        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.setToolTip("清空所有图片")
        self.clear_btn.clicked.connect(self.clear_images)
        
        control_layout.addWidget(self.import_single_btn)
        control_layout.addWidget(self.import_multiple_btn)
        control_layout.addWidget(self.import_folder_btn)
        control_layout.addWidget(self.clear_btn)
        
        layout.addLayout(control_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)
        
        # 拖拽提示标签
        drag_label = QLabel("💡 提示：可以直接拖拽图片文件到此区域")
        drag_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        drag_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(drag_label)
        
        # 图片列表（支持拖拽）
        self.image_list = ImageListWidget(self)  # 传递self作为parent
        layout.addWidget(self.image_list)
        
        return left_widget
    
    def create_right_panel(self):
        """创建右侧预览面板"""
        right_widget = QWidget()
        layout = QVBoxLayout(right_widget)
        
        # 标题
        title_label = QLabel("图片预览")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # 预览区域
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.Box)
        preview_layout = QVBoxLayout(preview_frame)
        
        # 预览图片标签
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setText("请选择图片进行预览")
        self.preview_label.setMinimumSize(400, 300)
        
        # 添加到滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.preview_label)
        scroll_area.setWidgetResizable(True)
        
        preview_layout.addWidget(scroll_area)
        layout.addWidget(preview_frame)
        
        # 图片信息区域
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Box)
        info_layout = QVBoxLayout(info_frame)
        
        self.info_label = QLabel("图片信息将显示在这里")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        layout.addWidget(info_frame)
        
        # 添加文本水印设置面板（调整到上方）
        watermark_group = self.create_watermark_settings()
        layout.addWidget(watermark_group)
        
        # 导出设置区域（调整到下方）
        export_group = QGroupBox("导出设置")
        export_layout = QVBoxLayout(export_group)
        
        # 输出格式选择
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("输出格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JPEG", "PNG"])
        self.format_combo.setCurrentText("JPEG")
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        export_layout.addLayout(format_layout)
        
        # 文件命名规则
        naming_layout = QHBoxLayout()
        naming_layout.addWidget(QLabel("文件名前缀:"))
        self.prefix_edit = QLineEdit()
        self.prefix_edit.setPlaceholderText("例如: wm_")
        self.prefix_edit.setMaximumWidth(100)
        naming_layout.addWidget(self.prefix_edit)
        
        naming_layout.addWidget(QLabel("后缀:"))
        self.suffix_edit = QLineEdit()
        self.suffix_edit.setPlaceholderText("例如: _watermarked")
        self.suffix_edit.setMaximumWidth(100)
        naming_layout.addWidget(self.suffix_edit)
        naming_layout.addStretch()
        export_layout.addLayout(naming_layout)
        
        # JPEG质量设置
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("JPEG质量:"))
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(0, 100)
        self.quality_slider.setValue(95)
        self.quality_slider.setTickPosition(QSlider.TicksBelow)
        self.quality_slider.setTickInterval(10)
        quality_layout.addWidget(self.quality_slider)
        
        self.quality_label = QLabel("95")
        self.quality_label.setMinimumWidth(30)
        quality_layout.addWidget(self.quality_label)
        export_layout.addLayout(quality_layout)
        
        # 图片缩放选项
        resize_group = QGroupBox("图片缩放 (可选)")
        resize_layout = QVBoxLayout(resize_group)
        
        # 宽度缩放
        width_layout = QHBoxLayout()
        self.resize_width_check = QCheckBox("按宽度缩放:")
        self.resize_width_check.stateChanged.connect(self.on_resize_option_changed)
        width_layout.addWidget(self.resize_width_check)
        
        self.resize_width_spin = QSpinBox()
        self.resize_width_spin.setRange(1, 10000)
        self.resize_width_spin.setValue(800)
        self.resize_width_spin.setEnabled(False)
        width_layout.addWidget(self.resize_width_spin)
        width_layout.addWidget(QLabel("像素"))
        width_layout.addStretch()
        resize_layout.addLayout(width_layout)
        
        # 高度缩放
        height_layout = QHBoxLayout()
        self.resize_height_check = QCheckBox("按高度缩放:")
        self.resize_height_check.stateChanged.connect(self.on_resize_option_changed)
        height_layout.addWidget(self.resize_height_check)
        
        self.resize_height_spin = QSpinBox()
        self.resize_height_spin.setRange(1, 10000)
        self.resize_height_spin.setValue(600)
        self.resize_height_spin.setEnabled(False)
        height_layout.addWidget(self.resize_height_spin)
        height_layout.addWidget(QLabel("像素"))
        height_layout.addStretch()
        resize_layout.addLayout(height_layout)
        
        # 百分比缩放
        percent_layout = QHBoxLayout()
        self.resize_percent_check = QCheckBox("按百分比缩放:")
        self.resize_percent_check.stateChanged.connect(self.on_resize_option_changed)
        percent_layout.addWidget(self.resize_percent_check)
        
        self.resize_percent_spin = QSpinBox()
        self.resize_percent_spin.setRange(1, 500)
        self.resize_percent_spin.setValue(100)
        self.resize_percent_spin.setEnabled(False)
        self.resize_percent_spin.setSuffix("%")
        percent_layout.addWidget(self.resize_percent_spin)
        percent_layout.addStretch()
        resize_layout.addLayout(percent_layout)
        
        export_layout.addWidget(resize_group)
        
        # 导出按钮
        export_buttons_layout = QHBoxLayout()
        
        self.export_single_btn = QPushButton("导出当前图片")
        self.export_single_btn.setToolTip("导出当前选中的图片")
        self.export_single_btn.clicked.connect(self.export_single_image)
        self.export_single_btn.setEnabled(False)  # 初始禁用
        
        self.export_all_btn = QPushButton("导出所有图片")
        self.export_all_btn.setToolTip("导出列表中的所有图片")
        self.export_all_btn.clicked.connect(self.export_all_images)
        self.export_all_btn.setEnabled(False)  # 初始禁用
        
        export_buttons_layout.addWidget(self.export_single_btn)
        export_buttons_layout.addWidget(self.export_all_btn)
        export_layout.addLayout(export_buttons_layout)
        
        layout.addWidget(export_group)
        
        # 添加文本水印设置面板
        # watermark_group = self.create_watermark_settings()
        # layout.addWidget(watermark_group)
        
        # 连接信号
        self.quality_slider.valueChanged.connect(self.on_quality_changed)
        
        return right_widget
    
    def connect_signals(self):
        """连接信号和槽"""
        # 图片管理器信号
        self.image_manager.images_updated.connect(self.update_image_list)
        self.image_manager.progress_updated.connect(self.update_progress)
        
        # 列表选择信号
        self.image_list.currentItemChanged.connect(self.on_image_selected)
    
    @pyqtSlot(list)
    def update_image_list(self, images):
        """更新图片列表显示"""
        self.image_list.clear()
        
        for img_info in images:
            item = QListWidgetItem()
            # 使用QIcon设置图标
            item.setIcon(img_info['thumbnail'])
            item.setText(img_info['file_name'])
            item.setData(Qt.UserRole, img_info['file_path'])
            self.image_list.addItem(item)
        
        # 更新状态
        self.status_label.setText(f"已加载 {len(images)} 张图片")
        
        # 根据图片数量启用/禁用导出按钮
        has_images = len(images) > 0
        self.export_all_btn.setEnabled(has_images)
        
        # 如果当前没有选中图片，禁用单张导出按钮
        if not self.image_list.currentItem():
            self.export_single_btn.setEnabled(False)
    
    @pyqtSlot(int, str)
    def update_progress(self, progress, message):
        """更新进度显示"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
        
        if progress == 100:
            self.progress_bar.setVisible(False)
        elif not self.progress_bar.isVisible():
            self.progress_bar.setVisible(True)
    
    def import_single_image(self):
        """导入单张图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片文件",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.tif *.tiff);;所有文件 (*.*)"
        )
        
        if file_path:
            success = self.image_manager.import_single_image(file_path)
            if not success:
                QMessageBox.warning(self, "导入失败", f"无法导入图片: {file_path}")
    
    def import_multiple_images(self):
        """导入多张图片"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择多张图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.tif *.tiff);;所有文件 (*.*)"
        )
        
        if file_paths:
            success_count, fail_count = self.image_manager.import_multiple_images(file_paths)
            if fail_count > 0:
                QMessageBox.information(
                    self, 
                    "导入完成", 
                    f"成功导入 {success_count} 张图片，失败 {fail_count} 张"
                )
    
    def import_folder(self):
        """导入文件夹"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择包含图片的文件夹"
        )
        
        if folder_path:
            success_count, fail_count = self.image_manager.import_folder(folder_path)
            if success_count == 0 and fail_count > 0:
                QMessageBox.warning(self, "导入失败", "未找到支持的图片文件")
            elif fail_count > 0:
                QMessageBox.information(
                    self,
                    "导入完成",
                    f"成功导入 {success_count} 张图片，失败 {fail_count} 张"
                )
    
    def clear_images(self):
        """清空图片列表"""
        if self.image_manager.get_image_count() > 0:
            reply = QMessageBox.question(
                self,
                "确认清空",
                "确定要清空所有图片吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.image_manager.clear_all_images()
    
    def on_image_selected(self, current, previous):
        """当选择图片时更新预览"""
        if current is None:
            self.preview_label.setText("请选择图片进行预览")
            self.info_label.setText("图片信息将显示在这里")
            # 禁用单张导出按钮
            self.export_single_btn.setEnabled(False)
            return
        
        file_path = current.data(Qt.UserRole)
        img_info = self.image_manager.get_image_by_path(file_path)
        
        if img_info:
            # 显示原图预览（适当缩放）
            original_pixmap = QPixmap(file_path)
            if not original_pixmap.isNull():
                # 缩放以适应预览区域
                scaled_pixmap = original_pixmap.scaled(
                    self.preview_label.width(), 
                    self.preview_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
            
            # 显示图片信息
            info_text = f"""
文件名: {img_info['file_name']}
路径: {img_info['file_path']}
尺寸: {img_info['width']} × {img_info['height']} 像素
格式: {img_info['format']}
色彩模式: {img_info['mode']}
文件大小: {img_info['file_size'] / 1024:.1f} KB
            """.strip()
            
            self.info_label.setText(info_text)
            # 启用单张导出按钮
            self.export_single_btn.setEnabled(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """窗口级别的拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否有支持的图片文件
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if self.is_supported_image(file_path):
                    event.acceptProposedAction()
                    return
            
        event.ignore()
    
    def dragMoveEvent(self, event: QDragMoveEvent):
        """窗口级别的拖拽移动事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """拖拽释放事件"""
        # 删除错误的样式设置代码 - MainWindow不需要恢复样式
        # self.setStyleSheet(self.normal_style)
        
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            image_files = []
            
            for url in urls:
                file_path = url.toLocalFile()
                if self.is_supported_image(file_path):
                    image_files.append(file_path)
            
            if image_files:
                # 直接调用MainWindow的handle_dropped_files方法
                self.handle_dropped_files(image_files)
                event.acceptProposedAction()
                return
        
        event.ignore()
    
    def handle_dropped_files(self, file_paths):
        """处理拖拽的文件"""
        if not file_paths:
            return
        
        # 显示拖拽提示
        self.status_label.setText(f"正在处理 {len(file_paths)} 个拖拽文件...")
        
        # 导入图片
        success_count = 0
        fail_count = 0
        
        for file_path in file_paths:
            if self.image_manager.import_single_image(file_path):
                success_count += 1
            else:
                fail_count += 1
        # 显示结果
        if fail_count == 0:
            self.status_label.setText(f"成功导入 {success_count} 张图片")
        else:
            self.status_label.setText(f"导入完成：成功 {success_count} 张，失败 {fail_count} 张")
            QMessageBox.information(
                self,
                "拖拽导入结果",
                f"成功导入 {success_count} 张图片\n失败 {fail_count} 张图片"
            )
    
    def is_supported_image(self, file_path):
        """检查文件是否为支持的图片格式"""
        if not os.path.isfile(file_path):
            return False
        
        supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
        _, ext = os.path.splitext(file_path)
        return ext.lower() in supported_extensions

    def on_quality_changed(self, value):
        """JPEG质量滑块值改变"""
        self.quality_label.setText(str(value))

    def on_resize_option_changed(self):
        """缩放选项改变"""
        # 启用/禁用对应的输入框
        self.resize_width_spin.setEnabled(self.resize_width_check.isChecked())
        self.resize_height_spin.setEnabled(self.resize_height_check.isChecked())
        self.resize_percent_spin.setEnabled(self.resize_percent_check.isChecked())

        # 确保只有一个选项被选中
        if self.resize_width_check.isChecked():
            self.resize_height_check.setChecked(False)
            self.resize_percent_check.setChecked(False)
        elif self.resize_height_check.isChecked():
            self.resize_width_check.setChecked(False)
            self.resize_percent_check.setChecked(False)
        elif self.resize_percent_check.isChecked():
            self.resize_width_check.setChecked(False)
            self.resize_height_check.setChecked(False)

    def create_watermark_settings(self):        
        # 文本水印设置面板
        watermark_group = QGroupBox("文本水印设置")
        watermark_layout = QVBoxLayout(watermark_group)
        
        # 水印启用开关
        self.watermark_enabled = QCheckBox("启用文本水印")
        self.watermark_enabled.stateChanged.connect(self.on_watermark_enabled_changed)
        watermark_layout.addWidget(self.watermark_enabled)
        
        # 基础设置面板
        basic_settings_group = QGroupBox("基础设置")
        basic_layout = QVBoxLayout(basic_settings_group)
        
        # 文本内容
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("水印文本:"))
        self.watermark_text = QLineEdit()
        self.watermark_text.setPlaceholderText("请输入水印文本内容")
        self.watermark_text.textChanged.connect(self.on_watermark_text_changed)
        text_layout.addWidget(self.watermark_text)
        basic_layout.addLayout(text_layout)
        
        # 位置选择
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("水印位置:"))
        self.watermark_position = QComboBox()
        self.watermark_position.addItems([
            '左上角', '右上角', '左下角', '右下角', 
            '正中心', '顶部居中', '底部居中', '左侧居中', '右侧居中'
        ])
        self.watermark_position.setCurrentText('右下角')
        self.watermark_position.currentTextChanged.connect(self.on_watermark_position_changed)
        position_layout.addWidget(self.watermark_position)
        position_layout.addStretch()
        basic_layout.addLayout(position_layout)
        
        # 透明度调节
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("透明度:"))
        self.watermark_opacity = QSlider(Qt.Horizontal)
        self.watermark_opacity.setRange(0, 100)
        self.watermark_opacity.setValue(50)
        self.watermark_opacity.valueChanged.connect(self.on_watermark_opacity_changed)
        opacity_layout.addWidget(self.watermark_opacity)
        
        self.opacity_label = QLabel("50%")
        self.opacity_label.setMinimumWidth(30)
        opacity_layout.addWidget(self.opacity_label)
        basic_layout.addLayout(opacity_layout)
        
        watermark_layout.addWidget(basic_settings_group)
        
        # 高级设置面板（可折叠）
        self.advanced_settings_group = QGroupBox("高级设置")
        self.advanced_settings_group.setCheckable(True)
        self.advanced_settings_group.setChecked(False)
        advanced_layout = QVBoxLayout(self.advanced_settings_group)
        
        # 字体选择
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("字体:"))
        self.watermark_font = QComboBox()
        self.watermark_font.addItems(['Arial', 'Times New Roman', 'SimHei', 'Microsoft YaHei', 'SimSun'])
        self.watermark_font.setCurrentText('Arial')
        self.watermark_font.currentTextChanged.connect(self.on_watermark_font_changed)
        font_layout.addWidget(self.watermark_font)
        font_layout.addStretch()
        advanced_layout.addLayout(font_layout)
        
        # 字号设置
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("字号:"))
        self.watermark_font_size = QSpinBox()
        self.watermark_font_size.setRange(8, 72)
        self.watermark_font_size.setValue(24)
        self.watermark_font_size.valueChanged.connect(self.on_watermark_font_size_changed)
        font_size_layout.addWidget(self.watermark_font_size)
        font_size_layout.addWidget(QLabel("像素"))
        font_size_layout.addStretch()
        advanced_layout.addLayout(font_size_layout)
        
        # 字体样式
        style_layout = QHBoxLayout()
        self.watermark_bold = QCheckBox("粗体")
        self.watermark_bold.stateChanged.connect(self.on_watermark_style_changed)
        style_layout.addWidget(self.watermark_bold)
        
        self.watermark_italic = QCheckBox("斜体")
        self.watermark_italic.stateChanged.connect(self.on_watermark_style_changed)
        style_layout.addWidget(self.watermark_italic)
        style_layout.addStretch()
        advanced_layout.addLayout(style_layout)
        
        # 颜色选择 - 修改为调色板
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("颜色:"))
        
        # 颜色预览按钮
        self.watermark_color_button = QPushButton()
        self.watermark_color_button.setFixedSize(30, 30)
        self.watermark_color_button.setStyleSheet("background-color: white; border: 1px solid gray;")
        self.watermark_color_button.clicked.connect(self.on_color_button_clicked)
        
        # 颜色值显示
        self.watermark_color_label = QLabel("白色")
        self.watermark_color_label.setMinimumWidth(60)
        
        color_layout.addWidget(self.watermark_color_button)
        color_layout.addWidget(self.watermark_color_label)
        color_layout.addStretch()
        advanced_layout.addLayout(color_layout)
        
        # 效果设置
        effect_layout = QHBoxLayout()
        self.watermark_shadow = QCheckBox("阴影效果")
        self.watermark_shadow.stateChanged.connect(self.on_watermark_effect_changed)
        effect_layout.addWidget(self.watermark_shadow)
        
        self.watermark_stroke = QCheckBox("描边效果")
        self.watermark_stroke.stateChanged.connect(self.on_watermark_effect_changed)
        effect_layout.addWidget(self.watermark_stroke)
        effect_layout.addStretch()
        advanced_layout.addLayout(effect_layout)
        
        watermark_layout.addWidget(self.advanced_settings_group)
        
        # 删除错误的layout.addWidget(watermark_group)调用
        # layout.addWidget(watermark_group)
        
        # 连接信号
        # self.quality_slider.valueChanged.connect(self.on_quality_changed)
        
        return watermark_group

    def set_watermark_controls_enabled(self, enabled):
        """设置水印控件启用状态"""
        self.watermark_text.setEnabled(enabled)
        self.watermark_position.setEnabled(enabled)
        self.watermark_opacity.setEnabled(enabled)
        self.watermark_font.setEnabled(enabled)
        self.watermark_font_size.setEnabled(enabled)
        self.watermark_bold.setEnabled(enabled)
        self.watermark_italic.setEnabled(enabled)
        # 修复：将watermark_color改为watermark_color_button和watermark_color_label
        self.watermark_color_button.setEnabled(enabled)
        self.watermark_color_label.setEnabled(enabled)
        self.watermark_shadow.setEnabled(enabled)
        self.watermark_stroke.setEnabled(enabled)
        self.advanced_settings_group.setEnabled(enabled)

    def on_watermark_enabled_changed(self, state):
        """水印启用状态改变"""
        enabled = state == Qt.Checked
        self.set_watermark_controls_enabled(enabled)

    def on_watermark_text_changed(self, text):
        """水印文本改变"""
        pass

    def on_watermark_position_changed(self, position):
        """水印位置改变"""
        pass

    def on_watermark_opacity_changed(self, value):
        """水印透明度改变"""
        self.opacity_label.setText(f"{value}%")

    def on_watermark_font_changed(self, font):
        """水印字体改变"""
        pass

    def on_watermark_font_size_changed(self, size):
        """水印字号改变"""
        pass

    def on_watermark_style_changed(self):
        """水印样式改变"""
        pass

    def on_watermark_effect_changed(self):
        """水印效果改变"""
        pass

    def on_color_button_clicked(self):
        """颜色按钮点击事件 - 打开调色板"""
        # 获取当前颜色
        current_color_name = self.watermark_color_label.text()
        color_map = {
            '白色': QColor(255, 255, 255),
            '黑色': QColor(0, 0, 0),
            '红色': QColor(255, 0, 0),
            '蓝色': QColor(0, 0, 255),
            '绿色': QColor(0, 255, 0),
            '黄色': QColor(255, 255, 0)
        }
        
        # 设置默认颜色
        initial_color = color_map.get(current_color_name, QColor(255, 255, 255))
        
        # 打开调色板对话框
        color = QColorDialog.getColor(initial_color, self, "选择水印颜色")
        
        if color.isValid():
            # 更新颜色预览按钮
            self.watermark_color_button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid gray;")
            
            # 更新颜色标签
            color_name = self.get_color_name(color)
            self.watermark_color_label.setText(color_name)
            
            # 触发颜色改变事件
            self.on_watermark_color_changed(color_name)

    def get_color_name(self, color):
        """根据颜色值获取颜色名称"""
        color_map = {
            (255, 255, 255): '白色',
            (0, 0, 0): '黑色',
            (255, 0, 0): '红色',
            (0, 0, 255): '蓝色',
            (0, 255, 0): '绿色',
            (255, 255, 0): '黄色'
        }
        
        rgb = (color.red(), color.green(), color.blue())
        return color_map.get(rgb, f"RGB({rgb[0]},{rgb[1]},{rgb[2]})")

    def on_watermark_color_changed(self, color_name):
        """水印颜色改变"""
        # 直接从按钮样式表中提取颜色值，而不是依赖颜色名称映射
        button_style = self.watermark_color_button.styleSheet()
        import re
        match = re.search(r'background-color:\s*([^;]+);', button_style)
        
        if match:
            color_str = match.group(1)
            # 直接使用按钮的样式表颜色，确保颜色一致
            self.watermark_color_button.setStyleSheet(f"background-color: {color_str}; border: 1px solid gray;")
        else:
            # 如果无法提取颜色，使用默认白色
            self.watermark_color_button.setStyleSheet("background-color: white; border: 1px solid gray;")
        
        # 更新颜色标签显示
        self.watermark_color_label.setText(color_name)

    def get_watermark_settings(self):
        """获取水印设置"""
        # 直接从按钮样式表中提取颜色值，确保颜色准确
        button_style = self.watermark_color_button.styleSheet()
        import re
        match = re.search(r'background-color:\s*([^;]+);', button_style)
        
        if match:
            color_str = match.group(1)
            if color_str.startswith('#'):
                # 十六进制颜色
                color = QColor(color_str)
                color_rgb = (color.red(), color.green(), color.blue())
            elif color_str.startswith('rgb'):
                # RGB颜色
                rgb_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_str)
                if rgb_match:
                    color_rgb = (int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3)))
                else:
                    color_rgb = (255, 255, 255)
            else:
                # 颜色名称
                color_map = {
                    'white': (255, 255, 255),
                    'black': (0, 0, 0),
                    'red': (255, 0, 0),
                    'blue': (0, 0, 255),
                    'green': (0, 255, 0),
                    'yellow': (255, 255, 0)
                }
                color_rgb = color_map.get(color_str.lower(), (255, 255, 255))
        else:
            color_rgb = (255, 255, 255)
        
        return {
            'enabled': self.watermark_enabled.isChecked(),
            'text': self.watermark_text.text().strip(),
            'position': self.watermark_position.currentText(),
            'opacity': self.watermark_opacity.value(),
            'font': self.watermark_font.currentText(),
            'font_size': self.watermark_font_size.value(),
            'bold': self.watermark_bold.isChecked(),
            'italic': self.watermark_italic.isChecked(),
            'color': color_rgb,  # 返回RGB元组
            'shadow': self.watermark_shadow.isChecked(),
            'stroke': self.watermark_stroke.isChecked()
        }

    def extract_color_from_style(self, style_sheet):
        """从样式表中提取颜色值"""
        import re
        match = re.search(r'background-color:\s*([^;]+);', style_sheet)
        if match:
            color_str = match.group(1)
            if color_str.startswith('#'):
                # 十六进制颜色
                color = QColor(color_str)
                return (color.red(), color.green(), color.blue())
            elif color_str.startswith('rgb'):
                # RGB颜色
                rgb_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_str)
                if rgb_match:
                    return (int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3)))
        
        # 默认颜色
        return (255, 255, 255) if 'white' in style_sheet else (0, 0, 0)

    def export_single_image(self):
        """导出单张图片"""
        current_item = self.image_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "导出失败", "请先选择一张图片")
            return
        
        file_path = current_item.data(Qt.UserRole)
        
        # 选择输出目录
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "选择导出目录",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not output_dir:
            return
        
        # 获取导出设置
        output_format = self.format_combo.currentText()
        quality = self.quality_slider.value()
        prefix = self.prefix_edit.text().strip()
        suffix = self.suffix_edit.text().strip()
        
        # 获取缩放设置
        resize_width = None
        resize_height = None
        resize_percent = None
        
        if self.resize_width_check.isChecked():
            resize_width = self.resize_width_spin.value()
        elif self.resize_height_check.isChecked():
            resize_height = self.resize_height_spin.value()
        elif self.resize_percent_check.isChecked():
            resize_percent = self.resize_percent_spin.value()
        
        # 获取水印设置
        watermark_settings = self.get_watermark_settings()
        
        # 根据水印启用状态选择导出方法
        if watermark_settings['enabled']:
            # 导出带水印的图片
            success, result = self.image_manager.export_single_image_with_watermark(
                file_path, output_dir, output_format, quality, prefix, suffix,
                resize_width, resize_height, resize_percent,
                watermark_settings['text'], watermark_settings['position'],
                watermark_settings['opacity'], watermark_settings['font'],
                watermark_settings['font_size'], watermark_settings['bold'],
                watermark_settings['italic'], watermark_settings['color'],
                watermark_settings['shadow'], watermark_settings['stroke']
            )
        else:
            # 导出普通图片
            success, result = self.image_manager.export_single_image(
                file_path, output_dir, output_format, quality, prefix, suffix,
                resize_width, resize_height, resize_percent
            )
        
        if success:
            QMessageBox.information(self, "导出成功", f"图片已成功导出到:\n{result}")
            self.status_label.setText(f"成功导出图片: {os.path.basename(result)}")
        else:
            QMessageBox.critical(self, "导出失败", f"导出失败:\n{result}")
            self.status_label.setText(f"导出失败: {result}")

    def export_all_images(self):
        """导出所有图片"""
        if self.image_manager.get_image_count() == 0:
            QMessageBox.warning(self, "导出失败", "图片列表为空")
            return
        
        # 选择输出目录
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "选择导出目录",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not output_dir:
            return
        
        # 获取导出设置
        output_format = self.format_combo.currentText()
        quality = self.quality_slider.value()
        prefix = self.prefix_edit.text().strip()
        suffix = self.suffix_edit.text().strip()
        
        # 获取缩放设置
        resize_width = None
        resize_height = None
        resize_percent = None
        
        if self.resize_width_check.isChecked():
            resize_width = self.resize_width_spin.value()
        elif self.resize_height_check.isChecked():
            resize_height = self.resize_height_spin.value()
        elif self.resize_percent_check.isChecked():
            resize_percent = self.resize_percent_spin.value()
        
        # 获取水印设置
        watermark_settings = self.get_watermark_settings()
        
        # 获取所有图片路径
        file_paths = [img['file_path'] for img in self.image_manager.images]
        
        # 根据水印启用状态选择导出方法
        if watermark_settings['enabled']:
            # 批量导出带水印的图片
            success_count, fail_count, results = self.image_manager.export_multiple_images_with_watermark(
                file_paths, output_dir, output_format, quality, prefix, suffix,
                resize_width, resize_height, resize_percent,
                watermark_settings['text'], watermark_settings['position'],
                watermark_settings['opacity'], watermark_settings['font'],
                watermark_settings['font_size'], watermark_settings['bold'],
                watermark_settings['italic'], watermark_settings['color'],
                watermark_settings['shadow'], watermark_settings['stroke']
            )
        else:
            # 批量导出普通图片
            success_count, fail_count, results = self.image_manager.export_multiple_images(
                file_paths, output_dir, output_format, quality, prefix, suffix,
                resize_width, resize_height, resize_percent
            )
        
        # 显示结果
        if fail_count == 0:
            QMessageBox.information(self, "导出完成", f"成功导出 {success_count} 张图片")
            self.status_label.setText(f"批量导出完成: {success_count} 张图片")
        else:
            # 显示详细错误信息
            error_details = "\n".join([f"{os.path.basename(fp)}: {error}" 
                                     for fp, _, error in results if error != "成功"])
            
            QMessageBox.warning(
                self, 
                "导出结果", 
                f"成功导出 {success_count} 张图片\n失败 {fail_count} 张图片\n\n失败详情:\n{error_details}"
            )
            self.status_label.setText(f"批量导出: 成功 {success_count} 张，失败 {fail_count} 张")
    
    def handle_dropped_files(self, file_paths):
        """处理拖拽的文件"""
        if not file_paths:
            return
        
        # 显示拖拽提示
        self.status_label.setText(f"正在处理 {len(file_paths)} 个拖拽文件...")
        
        # 导入图片
        success_count = 0
        fail_count = 0
        
        for file_path in file_paths:
            if self.image_manager.import_single_image(file_path):
                success_count += 1
            else:
                fail_count += 1
        
        # 显示结果
        if fail_count == 0:
            self.status_label.setText(f"成功导入 {success_count} 张图片")
        else:
            self.status_label.setText(f"导入完成：成功 {success_count} 张，失败 {fail_count} 张")
            QMessageBox.information(
                self,
                "拖拽导入结果",
                f"成功导入 {success_count} 张图片\n失败 {fail_count} 张图片"
            )
    
    def is_supported_image(self, file_path):
        """检查文件是否为支持的图片格式"""
        if not os.path.isfile(file_path):
            return False
        
        supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
        _, ext = os.path.splitext(file_path)
        return ext.lower() in supported_extensions