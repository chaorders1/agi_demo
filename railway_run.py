#!/usr/bin/env python
"""
模拟 railway run 命令的简化脚本
用于在本地测试Railway环境
"""

import os
import sys
import subprocess
import json
import socket
from pathlib import Path

def load_railway_config():
    """加载Railway配置"""
    config_file = Path("railway.json")
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def find_available_port(start_port=8000):
    """查找可用端口"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError("无法找到可用端口")

def is_port_in_use(port):
    """检查端口是否被占用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return False
    except OSError:
        return True

def setup_railway_env():
    """设置Railway环境变量"""
    config = load_railway_config()
    
    # 检查端口并选择可用端口
    default_port = 8000
    if is_port_in_use(default_port):
        available_port = find_available_port(default_port)
        print(f"⚠️ 端口 {default_port} 已被占用，使用端口 {available_port}")
    else:
        available_port = default_port
    
    # 基础环境变量
    env_vars = {
        'ENVIRONMENT': 'development',
        'PYTHONPATH': str(Path.cwd() / 'src'),
        'PORT': str(available_port),
        'RAILWAY_ENVIRONMENT': 'development',
        'RAILWAY_PROJECT_NAME': 'agi_demo_backend',
        'RAILWAY_SERVICE_NAME': 'web',
    }
    
    # 从railway.json加载环境变量，但覆盖PYTHONPATH为本地路径
    if 'environments' in config:
        production_vars = config['environments'].get('production', {}).get('variables', {})
        env_vars.update(production_vars)
        # 强制使用本地路径，不使用生产环境的/app/src
        env_vars['PYTHONPATH'] = str(Path.cwd() / 'src')
    
    # OpenCV headless模式
    env_vars.update({
        'OPENCV_IO_ENABLE_OPENEXR': '0',
        'OPENCV_IO_ENABLE_JASPER': '0',
        'QT_QPA_PLATFORM': 'offscreen'
    })
    
    # 设置环境变量
    for key, value in env_vars.items():
        os.environ[key] = value
    
    return env_vars

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python railway_run.py <command>")
        print("例如: python railway_run.py python start.py")
        sys.exit(1)
    
    # 设置环境变量
    env_vars = setup_railway_env()
    
    print("🔧 Railway环境变量已设置:")
    for key, value in env_vars.items():
        print(f"  {key}={value}")
    
    # 运行命令
    command = ' '.join(sys.argv[1:])
    print(f"\n🚀 运行命令: {command}")
    
    try:
        subprocess.run(command, shell=True, check=True)
    except KeyboardInterrupt:
        print("\n🛑 命令已中断")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 命令执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 