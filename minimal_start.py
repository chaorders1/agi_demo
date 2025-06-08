#!/usr/bin/env python
"""
最小化启动脚本 - 跳过依赖检查直接启动
用于Railway部署的最后备选方案
"""

import os
import sys
import subprocess
import importlib.util

# 设置环境
project_root = os.path.dirname(__file__)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

# 设置环境变量
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('PYTHONPATH', src_path)

# 设置OpenCV环境变量
os.environ.setdefault('OPENCV_IO_ENABLE_OPENEXR', '0')
os.environ.setdefault('OPENCV_IO_ENABLE_JASPER', '0')
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ.setdefault('PYTHONUNBUFFERED', '1')


def check_dependency(package_name):
    """检查依赖是否已安装"""
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except ImportError:
        return False


def install_missing_dependencies():
    """尝试安装缺失的依赖"""
    missing_deps = []
    
    # 检查关键依赖
    critical_deps = ['uvicorn', 'fastapi', 'opencv', 'numpy', 'PIL']
    
    for dep in critical_deps:
        if not check_dependency(dep):
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"⚠️ 发现缺失依赖: {missing_deps}")
        print("🔧 尝试安装缺失依赖...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                '--upgrade', '--no-cache-dir', '-r', 'requirements.txt'
            ])
            print("✅ 依赖安装完成")
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False
    
    return True


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 最小化启动脚本 - 端口 {port}")
    print(f"📍 项目目录: {project_root}")
    print(f"📍 源码目录: {src_path}")
    print(f"📍 Python路径: {sys.path[:3]}")
    print(f"🌍 环境变量:")
    for key in ['ENVIRONMENT', 'PYTHONPATH', 'PORT']:
        print(f"   {key}={os.environ.get(key, 'Not Set')}")
    
    # 检查并安装依赖
    if not install_missing_dependencies():
        print("⚠️ 依赖检查失败，但继续尝试启动...")
    
    try:
        print("📦 导入uvicorn...")
        import uvicorn
        print("✅ uvicorn导入成功")
        
        print("📦 导入应用...")
        from watermark.api import app
        print("✅ 应用导入成功")
        
        print(f"🌐 启动服务器 - http://0.0.0.0:{port}")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("🔄 尝试使用字符串方式启动...")
        try:
            import uvicorn
            uvicorn.run(
                "watermark.api:app",
                host="0.0.0.0",
                port=port,
                log_level="info",
                access_log=True
            )
        except Exception as e2:
            print(f"❌ 字符串方式启动也失败: {e2}")
            raise
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 尝试备用启动方案
        print("🔄 尝试备用启动方案...")
        try:
            os.system(f"python -m uvicorn watermark.api:app --host 0.0.0.0 --port {port}")
        except Exception as e3:
            print(f"❌ 备用方案也失败: {e3}")
            sys.exit(1) 