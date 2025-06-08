#!/usr/bin/env python
"""
FastAPI服务器启动脚本
运行水印API服务器
"""

import uvicorn
import os

if __name__ == "__main__":
    # 检测环境
    environment = os.getenv("ENVIRONMENT", "development")
    port = int(os.getenv("PORT", 8000))
    
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
            log_level="info"
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