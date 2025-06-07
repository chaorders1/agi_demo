# 水印工具最简用法说明

**1. 给图片添加水印（推荐用法）：**
```bash
python watermark.py add people.png --text "SocialNetwork0"
```
（自动生成 people_watermarked.png）

**2. 检测图片中的水印：**
```bash
python detect_watermark.py people_watermarked.png --watermark "SocialNetwork0"

python detect_watermark.py people_watermarked.png --watermark "SocialNet"
```
（检测是否包含指定水印，返回 yes/no）

**3. 运行安全测试（检测hack尝试）：**
```bash
python test_watermark_security.py people_watermarked.png "SocialNetwork0"
```
（自动测试各种hack变种，确保水印安全性）

---

**高级用法：**
- 手动指定输出文件名：`python watermark.py add people.png custom_name.png --text "SocialNetwork0"`
- 使用不同算法：`python watermark.py add people.png --text "SocialNetwork0" --method rivaGan`
- 显示检测置信度：`python detect_watermark.py people_watermarked.png --watermark "SocialNetwork0" --confidence`