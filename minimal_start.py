#!/usr/bin/env python
"""
最小化启动脚本 - 跳过依赖检查直接启动
用于Railway部署的最后备选方案
"""

import os
import sys

# 设置环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ.setdefault('ENVIRONMENT', 'production')

# 设置OpenCV环境变量
os.environ.setdefault('OPENCV_IO_ENABLE_OPENEXR', '0')
os.environ.setdefault('OPENCV_IO_ENABLE_JASPER', '0')
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 最小化启动脚本 - 端口 {port}")
    print(f"📍 工作目录: {os.getcwd()}")
    print(f"📍 Python路径: {sys.path[0]}")
    
    try:
        import uvicorn
        uvicorn.run(
            "watermark.api:app",
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 