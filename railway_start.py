#!/usr/bin/env python
"""
Railway专用启动脚本
处理Railway环境的特殊需求
"""

import os
import sys
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """设置环境变量和Python路径"""
    # 添加src到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, 'src')
    
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
        logger.info(f"添加到Python路径: {src_dir}")
    
    # 设置环境变量
    os.environ.setdefault('ENVIRONMENT', 'production')
    os.environ.setdefault('PYTHONPATH', src_dir)
    
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"工作目录: {os.getcwd()}")
    logger.info(f"Python路径: {sys.path[:3]}")

def check_dependencies():
    """检查关键依赖是否可用"""
    try:
        logger.info("检查依赖模块...")
        
        import fastapi
        logger.info(f"✅ FastAPI: {fastapi.__version__}")
        
        import uvicorn
        logger.info("✅ Uvicorn: 已导入")
        
        import numpy as np
        logger.info(f"✅ NumPy: {np.__version__}")
        
        import cv2
        logger.info(f"✅ OpenCV: {cv2.__version__}")
        
        from imwatermark import WatermarkEncoder
        logger.info("✅ invisible-watermark: 已导入")
        
        # 尝试导入API模块
        from watermark.api import app
        logger.info("✅ 水印API模块: 导入成功")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ 依赖导入失败: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 依赖检查失败: {e}")
        return False

def start_server():
    """启动服务器"""
    port = int(os.environ.get('PORT', 8000))
    
    logger.info(f"🚀 启动Railway生产服务器")
    logger.info(f"📍 端口: {port}")
    logger.info(f"📍 健康检查: /api/health")
    
    try:
        import uvicorn
        
        # Railway环境优化配置
        uvicorn.run(
            "watermark.api:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            reload=False,
            workers=1,  # Railway单容器，使用单worker
            timeout_keep_alive=30,
            timeout_graceful_shutdown=30
        )
    except Exception as e:
        logger.error(f"❌ 服务器启动失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    logger.info("🔧 Railway启动脚本开始执行")
    
    # 设置环境
    setup_environment()
    
    # 检查依赖
    if not check_dependencies():
        logger.error("依赖检查失败，退出")
        sys.exit(1)
    
    # 短暂延迟，确保所有模块加载完成
    time.sleep(2)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 