#!/usr/bin/env python
"""
FastAPI服务器启动脚本
运行水印API服务器
"""

import uvicorn
import os
import sys

# 确保src目录在Python路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def main():
    # 检测环境
    environment = os.getenv("ENVIRONMENT", "development")
    port = int(os.getenv("PORT", 8000))
    
    print(f"🔧 Python版本: {sys.version}")
    print(f"🔧 当前工作目录: {os.getcwd()}")
    print(f"🔧 Python路径: {sys.path[:3]}...")  # 只显示前3个路径
    print(f"🔧 环境变量 ENVIRONMENT: {environment}")
    print(f"🔧 环境变量 PORT: {port}")
    
    # 尝试导入关键模块进行预检查
    try:
        print("🔍 检查依赖模块...")
        import fastapi
        print(f"✅ FastAPI版本: {fastapi.__version__}")
        
        import uvicorn
        print(f"✅ Uvicorn已导入")
        
        # 检查水印模块
        from src.watermark.api import app
        print("✅ 水印API模块导入成功")
        
        # 检查核心依赖
        import cv2
        print(f"✅ OpenCV版本: {cv2.__version__}")
        
        import numpy as np
        print(f"✅ NumPy版本: {np.__version__}")
        
        from imwatermark import WatermarkEncoder
        print("✅ invisible-watermark库导入成功")
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("🔧 尝试安装缺失的依赖...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 预检查失败: {e}")
        sys.exit(1)
    
    if environment == "production":
        print("🚀 启动 Invisible Watermark API 服务器 (生产环境)...")
        print(f"📍 服务运行在端口: {port}")
        print("📍 API文档: /docs")
        print("📍 健康检查: /api/health")
        
        uvicorn.run(
            "src.watermark.api:app",
            host="0.0.0.0",
            port=port,
            reload=False,  # 生产环境关闭自动重载
            log_level="info",
            access_log=True
        )
    else:
        print("🚀 启动 Invisible Watermark API 服务器 (开发环境)...")
        print("📍 API文档: http://localhost:8000/docs")
        print("📍 健康检查: http://localhost:8000/api/health")
        print("📍 根端点: http://localhost:8000/")
        print("")
        
        uvicorn.run(
            "src.watermark.api:app",  # 使用import字符串而不是直接导入app对象
            host="0.0.0.0",
            port=8000,
            reload=True,  # 开发模式自动重载
            log_level="info"
        )

if __name__ == "__main__":
    main() 