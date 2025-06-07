# 🔒 Invisible Watermark Library

一个强大的Python库，用于在图片中添加和检测不可见水印。

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/security-tested-brightgreen.svg)](tests/test_security.py)

## ✨ 特性

- 🎯 **简单易用**: 一行命令即可添加水印
- 🔍 **智能检测**: 自动检测和验证水印
- 🛡️ **安全可靠**: 通过34种hack测试，安全评分100%
- 🚀 **高性能**: 基于DWT-DCT算法，处理速度快
- 📦 **模块化设计**: 可作为库使用或命令行工具

## 🚀 快速开始

### 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 或使用安装脚本
bash scripts/install.sh
```

### 基础用法

```bash
# 1. 添加水印（自动生成输出文件名）
python -m src.watermark.cli add image.png --text "SocialNetwork0"

# 2. 检测水印
python -m src.watermark.cli detect image_watermarked.png --watermark "SocialNetwork0"

# 3. 扫描未知水印
python -m src.watermark.cli scan image.png
```

## 📖 详细文档

- [使用说明](docs/usage.md) - 详细的使用指南
- [API文档](docs/detailed_readme.md) - 完整的API参考
- [安全测试](tests/test_security.py) - 安全性验证

## 🏗️ 项目结构

```
agi_demo/
├── src/watermark/          # 核心库代码
│   ├── core.py            # 水印添加/提取
│   ├── detector.py        # 水印检测
│   └── cli.py             # 命令行接口
├── tests/                 # 测试套件
├── docs/                  # 文档
├── examples/              # 使用示例
└── scripts/               # 工具脚本
```

## 🔧 作为Python库使用

```python
from src.watermark import add_watermark, detect_watermark

# 添加水印
add_watermark('input.png', 'output.png', 'My Watermark')

# 检测水印
has_watermark, confidence, decoded = detect_watermark(
    'output.png', watermark='My Watermark'
)
print(f"Has watermark: {has_watermark}")
```

## 🛡️ 安全性

本库经过严格的安全测试，包括：
- ✅ 大小写变化测试
- ✅ 字符替换测试  
- ✅ 部分匹配测试
- ✅ 特殊字符注入测试
- ✅ Unicode攻击测试

运行安全测试：
```bash
python tests/test_security.py image_watermarked.png "YourWatermark"
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

基于 [invisible-watermark](https://github.com/ShieldMnt/invisible-watermark) 库开发