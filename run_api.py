#!/usr/bin/env python
"""
FastAPI服务器启动脚本
运行水印API服务器
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 启动 Invisible Watermark API 服务器...")
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