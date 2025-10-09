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
                            QFrame, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSlot, QMimeData
from PyQt5.QtGui import QPixmap, QFont, QIcon, QDragEnterEvent, QDropEvent, QDragMoveEvent  # 添加QDragMoveEvent导入

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