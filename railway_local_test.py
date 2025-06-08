#!/usr/bin/env python
"""
Railway本地测试脚本
模拟Railway环境进行本地测试
"""

import os
import sys
import subprocess
import json
import logging
import socket
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RailwayLocalTester:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.railway_config = self.load_railway_config()
    
    def find_available_port(self, start_port=8000):
        """查找可用端口"""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise RuntimeError("无法找到可用端口")
    
    def is_port_in_use(self, port):
        """检查端口是否被占用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return False
        except OSError:
            return True
        
    def load_railway_config(self):
        """加载Railway配置"""
        config_file = self.project_root / "railway.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def setup_environment(self):
        """设置模拟Railway环境变量"""
        logger.info("🔧 设置Railway模拟环境...")
        
        # 检查端口并选择可用端口
        default_port = 8000
        if self.is_port_in_use(default_port):
            available_port = self.find_available_port(default_port)
            logger.warning(f"⚠️ 端口 {default_port} 已被占用，使用端口 {available_port}")
        else:
            available_port = default_port
        
        # 基础环境变量
        env_vars = {
            'ENVIRONMENT': 'development',
            'PYTHONPATH': str(self.project_root / 'src'),
            'PORT': str(available_port),
            'RAILWAY_ENVIRONMENT': 'development',
            'RAILWAY_PROJECT_NAME': 'agi_demo_backend',
            'RAILWAY_SERVICE_NAME': 'web',
        }
        
        # 从railway.json加载环境变量，但覆盖PYTHONPATH为本地路径
        if 'environments' in self.railway_config:
            production_vars = self.railway_config['environments'].get('production', {}).get('variables', {})
            env_vars.update(production_vars)
            # 强制使用本地路径，不使用生产环境的/app/src
            env_vars['PYTHONPATH'] = str(self.project_root / 'src')
        
        # OpenCV headless模式
        env_vars.update({
            'OPENCV_IO_ENABLE_OPENEXR': '0',
            'OPENCV_IO_ENABLE_JASPER': '0',
            'QT_QPA_PLATFORM': 'offscreen'
        })
        
        # 设置环境变量
        for key, value in env_vars.items():
            os.environ[key] = value
            logger.info(f"  {key}={value}")
        
        # 添加src到Python路径
        src_path = str(self.project_root / 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
            logger.info(f"  添加到Python路径: {src_path}")
    
    def check_dependencies(self):
        """检查依赖是否安装"""
        logger.info("📦 检查依赖...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            logger.error("❌ requirements.txt 不存在")
            return False
        
        try:
            # 检查pip freeze输出
            result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], 
                                  capture_output=True, text=True)
            installed_packages = result.stdout.lower()
            
            # 读取requirements.txt
            with open(requirements_file, 'r') as f:
                requirements = f.read().strip().split('\n')
            
            missing_packages = []
            for req in requirements:
                if req.strip() and not req.startswith('#'):
                    package_name = req.split('==')[0].split('>=')[0].split('<=')[0].strip().lower()
                    if package_name not in installed_packages:
                        missing_packages.append(req.strip())
            
            if missing_packages:
                logger.warning("⚠️ 发现缺失的依赖包:")
                for pkg in missing_packages:
                    logger.warning(f"  - {pkg}")
                
                install = input("是否现在安装缺失的依赖? (y/n): ").lower().strip()
                if install == 'y':
                    self.install_dependencies()
                else:
                    logger.warning("跳过依赖安装，可能会导致运行错误")
            else:
                logger.info("✅ 所有依赖已安装")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 依赖检查失败: {e}")
            return False
    
    def install_dependencies(self):
        """安装依赖"""
        logger.info("📦 安装依赖...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                         check=True)
            logger.info("✅ 依赖安装完成")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 依赖安装失败: {e}")
    
    def run_build_command(self):
        """运行构建命令"""
        if 'build' in self.railway_config and 'buildCommand' in self.railway_config['build']:
            build_cmd = self.railway_config['build']['buildCommand']
            logger.info(f"🔨 运行构建命令: {build_cmd}")
            try:
                subprocess.run(build_cmd, shell=True, check=True)
                logger.info("✅ 构建完成")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ 构建失败: {e}")
                return False
        return True
    
    def start_service(self, script_name=None):
        """启动服务"""
        # 确定启动脚本
        if script_name:
            start_script = script_name
        elif 'deploy' in self.railway_config and 'startCommand' in self.railway_config['deploy']:
            start_script = self.railway_config['deploy']['startCommand']
        else:
            # 检查可用的启动脚本
            possible_scripts = ['minimal_start.py', 'railway_start.py', 'start.py']
            start_script = None
            for script in possible_scripts:
                if (self.project_root / script).exists():
                    start_script = f"python {script}"
                    break
            
            if not start_script:
                logger.error("❌ 找不到启动脚本")
                return False
        
        logger.info(f"🚀 启动服务: {start_script}")
        logger.info(f"📍 端口: {os.environ.get('PORT', '8000')}")
        logger.info(f"📍 环境: {os.environ.get('ENVIRONMENT', 'development')}")
        logger.info("📍 按 Ctrl+C 停止服务")
        
        try:
            # 运行启动命令
            subprocess.run(start_script, shell=True, check=True)
        except KeyboardInterrupt:
            logger.info("🛑 服务已停止")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 服务启动失败: {e}")
            return False
        
        return True
    
    def run_test(self, script_name=None):
        """运行完整测试"""
        logger.info("🧪 Railway本地测试开始")
        logger.info(f"📍 项目目录: {self.project_root}")
        
        # 设置环境
        self.setup_environment()
        
        # 检查依赖
        if not self.check_dependencies():
            logger.error("依赖检查失败")
            return False
        
        # 运行构建
        if not self.run_build_command():
            logger.error("构建失败")
            return False
        
        # 启动服务
        return self.start_service(script_name)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Railway本地测试工具')
    parser.add_argument('--script', '-s', help='指定启动脚本')
    parser.add_argument('--no-deps', action='store_true', help='跳过依赖检查')
    parser.add_argument('--env-only', action='store_true', help='只设置环境变量')
    
    args = parser.parse_args()
    
    tester = RailwayLocalTester()
    
    if args.env_only:
        tester.setup_environment()
        logger.info("✅ 环境变量已设置，你可以手动运行应用")
        return
    
    if args.no_deps:
        tester.setup_environment()
        tester.start_service(args.script)
    else:
        tester.run_test(args.script)

if __name__ == "__main__":
    main() 