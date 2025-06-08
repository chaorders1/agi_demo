# Railway部署指南

## 🚀 快速部署步骤

### 1. 本地测试
```bash
# 运行新的部署测试脚本
python railway_deploy_test.py

# 或者运行原有的测试脚本
python railway_local_test.py --script minimal_start.py
```

### 2. Railway部署配置

#### 关键文件说明：
- `railway.json` - Railway部署配置（主要）
- `Procfile` - 启动命令配置  
- `nixpacks.toml` - 构建环境配置（备用）
- `Dockerfile.backup` - Docker构建配置（备用）
- `minimal_start.py` - 优化的启动脚本
- `requirements.txt` - 依赖包列表
- `.railwayignore` - 部署时忽略的文件

#### 环境变量设置：
```
PYTHONPATH=/app/src
ENVIRONMENT=production
OPENCV_IO_ENABLE_OPENEXR=0
OPENCV_IO_ENABLE_JASPER=0
QT_QPA_PLATFORM=offscreen
PYTHONUNBUFFERED=1
PIP_NO_CACHE_DIR=1
```

### 3. 部署到Railway

#### 方案1: 使用railway.json（推荐）
1. **连接GitHub仓库**
   - 在Railway控制台选择"Deploy from GitHub repo"
   - 选择你的项目仓库

2. **自动检测配置**
   - Railway会自动检测到`railway.json`配置
   - 使用Railway的默认Python构建器
   - 构建命令：`pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt`
   - 启动命令：`python minimal_start.py`

#### 方案2: 使用Dockerfile（备用）
如果自动构建有问题：
1. 将 `Dockerfile.backup` 重命名为 `Dockerfile`
2. 重新部署项目

#### 方案3: 使用Nixpacks（高级）
如果需要特定的系统依赖：
1. 确保 `nixpacks.toml` 配置正确
2. 在Railway设置中指定构建器为 "nixpacks"

## 🔧 故障排除

### 常见问题及解决方案

#### 1. Nix构建错误
**症状**：`undefined variable 'pip'` 或其他Nix相关错误
**解决方案**：
- ✅ 已修复：移除了nixpacks中的无效pip配置
- 使用默认的Python构建器（railway.json已更新）
- 如果仍有问题，使用Dockerfile.backup作为备用方案

#### 2. 依赖安装失败
**症状**：构建时提示缺少uvicorn或其他依赖
**解决方案**：
```bash
# 本地测试依赖安装
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# 检查requirements.txt是否包含所有必要依赖
```

#### 3. 模块导入失败
**症状**：启动时提示"ModuleNotFoundError"
**解决方案**：
- 检查`PYTHONPATH`环境变量是否正确设置为`/app/src`
- 确认`src/watermark/`目录结构正确

#### 4. OpenCV相关错误
**症状**：OpenCV初始化失败或GUI相关错误
**解决方案**：
- 确保使用`opencv-python-headless`而不是`opencv-python`
- 设置环境变量：
  ```
  OPENCV_IO_ENABLE_OPENEXR=0
  OPENCV_IO_ENABLE_JASPER=0
  QT_QPA_PLATFORM=offscreen
  ```

#### 5. 端口绑定问题
**症状**：服务无法启动或无法访问
**解决方案**：
- 确保使用`0.0.0.0`而不是`localhost`或`127.0.0.1`
- 使用Railway提供的`PORT`环境变量

#### 6. 健康检查失败
**症状**：部署成功但健康检查超时
**解决方案**：
- 检查`/api/health`端点是否正常响应
- 增加健康检查超时时间（已设置为600秒）
- 查看应用启动日志

#### 7. 构建器相关问题
**症状**：构建过程失败或超时
**解决方案**：
1. **默认构建器**（推荐）：使用railway.json，不指定构建器
2. **Nixpacks构建器**：确保nixpacks.toml配置正确
3. **Docker构建器**：使用Dockerfile.backup

## 📊 监控和调试

### 查看日志
```bash
# Railway CLI查看日志
railway logs

# 或在Railway控制台查看实时日志
```

### 测试API端点
```bash
# 健康检查
curl https://your-app.railway.app/api/health

# API根端点
curl https://your-app.railway.app/

# 测试水印功能
curl -X POST https://your-app.railway.app/api/watermark/add \
  -F "image=@test.jpg" \
  -F "text=test watermark"
```

## 🎯 性能优化建议

1. **依赖优化**
   - 使用固定版本号避免构建时的版本冲突
   - 使用`--no-cache-dir`减少构建时间

2. **启动优化**
   - 使用`minimal_start.py`跳过不必要的检查
   - 设置`PYTHONUNBUFFERED=1`确保日志实时输出

3. **资源配置**
   - Railway免费计划有资源限制，注意内存使用
   - 考虑升级到付费计划获得更好性能

4. **构建优化**
   - 使用`.railwayignore`排除不必要的文件
   - 选择合适的构建器（默认Python > Dockerfile > Nixpacks）

## 📝 部署检查清单

- [ ] 本地测试通过（`python railway_deploy_test.py`）
- [ ] 所有依赖都在`requirements.txt`中
- [ ] `railway.json`配置正确
- [ ] 环境变量设置完整
- [ ] 健康检查端点可访问
- [ ] API端点正常响应
- [ ] 日志输出正常
- [ ] 选择合适的构建方案

## 🔄 多重部署方案

### 方案优先级
1. **railway.json** （推荐）- 简单稳定
2. **Dockerfile** （备用）- 完全控制
3. **nixpacks.toml** （高级）- 系统依赖定制

### 快速切换方案
```bash
# 切换到Dockerfile方案
mv Dockerfile.backup Dockerfile
git add . && git commit -m "Switch to Dockerfile" && git push

# 切换回默认方案  
mv Dockerfile Dockerfile.backup
git add . && git commit -m "Switch back to default" && git push
```

## 🆘 获取帮助

如果遇到问题：
1. 查看Railway控制台的构建和部署日志
2. 运行本地测试脚本诊断问题
3. 尝试不同的构建方案
4. 检查GitHub仓库的Actions（如果配置了CI/CD）
5. 参考Railway官方文档：https://docs.railway.app/

## 🎉 最新修复

- ✅ 修复了Nix构建中的`undefined variable 'pip'`错误
- ✅ 优化了railway.json配置，使用默认Python构建器
- ✅ 添加了.railwayignore文件，提高构建速度
- ✅ 提供了多种备用部署方案
- ✅ 改进了错误诊断和故障排除指南 