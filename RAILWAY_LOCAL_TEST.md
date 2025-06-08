# Railway本地测试工具

这个工具集帮助你在本地模拟Railway环境进行测试，解决 `railway run` 命令无法正常工作的问题。

## 问题背景

当你运行 `railway run python start.py` 时遇到 "Project has no services" 错误，这是因为Railway项目没有正确配置服务。这个工具集提供了本地测试的替代方案。

## 工具说明

### 1. `railway_local_test.py` - 完整测试工具
功能最全面的测试脚本，包含：
- 环境变量设置
- 依赖检查和安装
- 构建命令执行
- 服务启动

### 2. `railway_run.py` - 简化运行工具
模拟 `railway run` 命令的简化版本，只设置环境变量并运行指定命令。

### 3. `railway_test.sh` - 便捷脚本
Shell脚本包装器，提供友好的命令行界面。

## 使用方法

### 方法1：使用便捷脚本（推荐）

```bash
# 显示帮助信息
./railway_test.sh --help

# 运行完整测试（自动选择启动脚本）
./railway_test.sh --test

# 使用指定脚本运行测试
./railway_test.sh --script minimal_start.py

# 模拟railway run命令
./railway_test.sh --run python start.py
./railway_test.sh --run python minimal_start.py
```

### 方法2：直接使用Python脚本

```bash
# 完整测试
python railway_local_test.py

# 使用指定脚本
python railway_local_test.py --script minimal_start.py

# 跳过依赖检查
python railway_local_test.py --no-deps

# 只设置环境变量
python railway_local_test.py --env-only

# 模拟railway run
python railway_run.py python start.py
```

## 环境变量设置

工具会自动设置以下环境变量：

```bash
ENVIRONMENT=development
PYTHONPATH=/path/to/your/project/src
PORT=8000
RAILWAY_ENVIRONMENT=development
RAILWAY_PROJECT_NAME=agi_demo_backend
RAILWAY_SERVICE_NAME=web
OPENCV_IO_ENABLE_OPENEXR=0
OPENCV_IO_ENABLE_JASPER=0
QT_QPA_PLATFORM=offscreen
```

还会从 `railway.json` 中加载生产环境的环境变量。

## 功能特性

### ✅ 自动环境配置
- 读取 `railway.json` 配置
- 设置Railway兼容的环境变量
- 配置Python路径

### ✅ 依赖管理
- 检查 `requirements.txt` 中的依赖
- 自动提示安装缺失的包
- 支持跳过依赖检查

### ✅ 多启动脚本支持
- 自动检测可用的启动脚本
- 支持指定特定脚本
- 按优先级选择：`minimal_start.py` > `railway_start.py` > `start.py`

### ✅ 构建命令执行
- 自动执行 `railway.json` 中的构建命令
- 支持pip安装依赖

### ✅ 错误处理
- 友好的错误提示
- 支持Ctrl+C中断
- 详细的日志输出

## 故障排除

### 问题1：Python模块导入失败
```bash
# 确保依赖已安装
pip install -r requirements.txt

# 或使用工具自动安装
python railway_local_test.py  # 会提示安装缺失依赖
```

### 问题2：找不到启动脚本
```bash
# 检查可用的启动脚本
ls *.py | grep -E "(start|minimal)"

# 手动指定脚本
./railway_test.sh --script your_script.py
```

### 问题3：端口冲突
```bash
# 修改端口（在脚本中或环境变量）
export PORT=8001
./railway_test.sh --test
```

### 问题4：OpenCV相关错误
工具已自动设置headless模式环境变量，如果仍有问题：
```bash
# 手动设置
export QT_QPA_PLATFORM=offscreen
export OPENCV_IO_ENABLE_OPENEXR=0
```

## 与Railway部署的区别

| 特性 | 本地测试 | Railway部署 |
|------|----------|-------------|
| 环境 | development | production |
| 端口 | 8000 | Railway分配 |
| 依赖安装 | 手动/提示 | 自动 |
| 构建过程 | 可选 | 自动 |
| 日志级别 | INFO | 根据配置 |

## 下一步

1. **修复Railway服务配置**：
   ```bash
   # 等待当前部署完成，然后检查
   railway status
   ```

2. **本地开发**：
   使用这些工具进行本地开发和测试

3. **生产部署**：
   确认本地测试通过后，推送到Railway

## 文件说明

- `railway_local_test.py` - 主要测试脚本（200+行）
- `railway_run.py` - 简化运行脚本（60+行）
- `railway_test.sh` - Shell包装脚本（100+行）
- `railway.json` - Railway配置文件
- `nixpacks.toml` - 构建配置
- `Procfile` - 进程配置

这些工具完全模拟Railway环境，让你可以在本地进行完整的测试！ 