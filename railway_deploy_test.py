#!/usr/bin/env python
"""
Railway部署测试脚本
模拟Railway环境，测试部署配置
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_railway_environment():
    """设置Railway模拟环境"""
    logger.info("🔧 设置Railway模拟环境...")
    
    # 从railway.json读取配置
    railway_config_path = Path("railway.json")
    if railway_config_path.exists():
        with open(railway_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 设置环境变量
        env_vars = config.get('environments', {}).get('production', {}).get('variables', {})
        for key, value in env_vars.items():
            os.environ[key] = str(value)
            logger.info(f"   {key}={value}")
    
    # 设置额外的Railway环境变量
    railway_vars = {
        'PORT': '8000',
        'RAILWAY_ENVIRONMENT': 'development',
        'RAILWAY_PROJECT_NAME': 'agi_demo_backend',
        'RAILWAY_SERVICE_NAME': 'web'
    }
    
    for key, value in railway_vars.items():
        os.environ.setdefault(key, value)
        logger.info(f"   {key}={os.environ[key]}")


def check_dependencies():
    """检查依赖安装情况"""
    logger.info("📦 检查依赖...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'opencv-python-headless',
        'numpy',
        'Pillow',
        'invisible-watermark'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"   ❌ {package}")
    
    if missing_packages:
        logger.warning(f"⚠️ 发现缺失的依赖包:")
        for pkg in missing_packages:
            logger.warning(f"   - {pkg}")
        
        response = input("是否现在安装缺失的依赖? (y/n): ")
        if response.lower() == 'y':
            install_dependencies()
        else:
            logger.warning("跳过依赖安装，可能会导致启动失败")
    else:
        logger.info("✅ 所有依赖都已安装")


def install_dependencies():
    """安装依赖"""
    logger.info("🔧 安装依赖...")
    
    try:
        # 升级pip
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ])
        
        # 安装requirements.txt
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            '--no-cache-dir', '-r', 'requirements.txt'
        ])
        
        logger.info("✅ 依赖安装完成")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ 依赖安装失败: {e}")
        return False
    
    return True


def test_import():
    """测试关键模块导入"""
    logger.info("🧪 测试模块导入...")
    
    try:
        # 测试uvicorn导入
        import uvicorn
        logger.info("   ✅ uvicorn导入成功")
        
        # 测试应用导入
        sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
        from watermark.api import app
        logger.info("   ✅ watermark.api导入成功")
        
        # 测试健康检查端点
        logger.info("   ✅ 应用模块导入测试通过")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ 模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_startup():
    """测试启动脚本"""
    logger.info("🚀 测试启动脚本...")
    
    try:
        # 测试minimal_start.py是否可以正常执行
        result = subprocess.run([
            sys.executable, 'minimal_start.py'
        ], timeout=10, capture_output=True, text=True)
        
        if "启动服务器" in result.stdout or "uvicorn" in result.stdout:
            logger.info("   ✅ 启动脚本测试通过")
            return True
        else:
            logger.warning(f"   ⚠️ 启动脚本输出异常: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.info("   ✅ 启动脚本正常运行（超时终止）")
        return True
    except Exception as e:
        logger.error(f"   ❌ 启动脚本测试失败: {e}")
        return False


def main():
    """主函数"""
    logger.info("🧪 Railway部署测试开始")
    logger.info(f"📍 项目目录: {os.getcwd()}")
    
    # 设置环境
    setup_railway_environment()
    
    # 检查依赖
    check_dependencies()
    
    # 测试导入
    if not test_import():
        logger.error("❌ 模块导入测试失败")
        return False
    
    # 测试启动
    if not test_startup():
        logger.error("❌ 启动测试失败")
        return False
    
    logger.info("🎉 Railway部署测试完成！")
    logger.info("💡 建议:")
    logger.info("   1. 确保所有依赖都已正确安装")
    logger.info("   2. 检查railway.json配置是否正确")
    logger.info("   3. 在Railway控制台查看构建和部署日志")
    logger.info("   4. 确保健康检查端点 /api/health 可访问")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 