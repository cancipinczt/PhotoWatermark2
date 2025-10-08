# PhotoWatermark2

AI4SE homework2 - 图片水印工具

## 功能特性

### 已实现功能
- ✅ 单张图片导入（拖拽或文件选择器）
- ✅ 批量图片导入（多选或文件夹导入）
- ✅ 图片格式支持：JPEG, PNG, BMP, TIFF
- ✅ 图片列表显示（缩略图和文件名）
- ✅ 实时预览功能
- ✅ 图片信息显示

### 待实现功能
- 水印添加功能
- 图片导出功能
- 配置管理
- 更多高级功能

## 安装和运行

### 环境要求
- Python 3.8+
- Windows 10/11

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行程序
```bash
python run.py
```

## 项目结构

```
PhotoWatermark2/
 ├── main.py # 主程序入口
 ├── run.py # 启动脚本
 ├── requirements.txt # 依赖列表
 ├── requirements.md # 需求规格说明
 ├── core/ # 核心功能模块 
 │ ├── image_processor.py # 图像处理 
 │ └── image_manager.py # 图片管理 
 ├── ui/ # 用户界面 
 │ └── main_window.py # 主窗口 
 └── utils/ # 工具函数 
 └── logger.py # 日志配置
```


## 开发进度
- [x] 项目结构和需求分析
- [x] 图片导入功能实现
- [ ] 水印功能开发
- [ ] 导出功能开发
- [ ] 测试和优化