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
    
    # 设置OpenCV环境变量，强制使用headless模式
    os.environ.setdefault('OPENCV_IO_ENABLE_OPENEXR', '0')
    os.environ.setdefault('OPENCV_IO_ENABLE_JASPER', '0')
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"工作目录: {os.getcwd()}")
    logger.info(f"Python路径: {sys.path[:3]}")

def check_dependencies():
    """检查关键依赖是否可用"""
    critical_errors = []
    warnings = []
    
    try:
        logger.info("检查依赖模块...")
        
        # 检查FastAPI (关键)
        try:
            import fastapi
            logger.info(f"✅ FastAPI: {fastapi.__version__}")
        except ImportError as e:
            critical_errors.append(f"FastAPI导入失败: {e}")
        
        # 检查Uvicorn (关键)
        try:
            import uvicorn
            logger.info("✅ Uvicorn: 已导入")
        except ImportError as e:
            critical_errors.append(f"Uvicorn导入失败: {e}")
        
        # 检查NumPy (关键)
        try:
            import numpy as np
            logger.info(f"✅ NumPy: {np.__version__}")
        except ImportError as e:
            critical_errors.append(f"NumPy导入失败: {e}")
        
        # 检查OpenCV (非关键，可以降级处理)
        try:
            import cv2
            logger.info(f"✅ OpenCV: {cv2.__version__}")
        except ImportError as e:
            warnings.append(f"OpenCV导入失败: {e}")
            logger.warning(f"⚠️ OpenCV导入失败，但将尝试继续: {e}")
        except Exception as e:
            warnings.append(f"OpenCV运行时错误: {e}")
            logger.warning(f"⚠️ OpenCV运行时错误，但将尝试继续: {e}")
        
        # 检查invisible-watermark (关键)
        try:
            from imwatermark import WatermarkEncoder
            logger.info("✅ invisible-watermark: 已导入")
        except ImportError as e:
            critical_errors.append(f"invisible-watermark导入失败: {e}")
        except Exception as e:
            warnings.append(f"invisible-watermark运行时错误: {e}")
            logger.warning(f"⚠️ invisible-watermark运行时错误: {e}")
        
        # 检查API模块 (关键)
        try:
            from watermark.api import app
            logger.info("✅ 水印API模块: 导入成功")
        except ImportError as e:
            critical_errors.append(f"水印API模块导入失败: {e}")
        except Exception as e:
            critical_errors.append(f"水印API模块运行时错误: {e}")
        
        # 报告结果
        if critical_errors:
            logger.error("❌ 关键依赖检查失败:")
            for error in critical_errors:
                logger.error(f"  - {error}")
            return False
        
        if warnings:
            logger.warning("⚠️ 发现警告，但将尝试继续运行:")
            for warning in warnings:
                logger.warning(f"  - {warning}")
        
        logger.info("✅ 依赖检查完成，可以启动服务器")
        return True
        
    except Exception as e:
        logger.error(f"❌ 依赖检查过程中发生未预期错误: {e}")
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
        logger.error("关键依赖检查失败，退出")
        sys.exit(1)
    
    # 短暂延迟，确保所有模块加载完成
    time.sleep(2)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 