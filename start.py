#!/usr/bin/env python
"""
简化的启动脚本 - 用于Railway部署
"""

import os
import sys

# 添加src到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 设置环境变量
os.environ.setdefault('ENVIRONMENT', 'production')

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 启动服务器在端口 {port}")
    
    uvicorn.run(
        "watermark.api:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 