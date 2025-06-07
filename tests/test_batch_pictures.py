#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
"""
批量图片水印兼容性自动化测试
遍历 tests/test_pictures/ 目录下所有图片，自动加水印并检测
"""
import glob
import cv2
from src.watermark.core import add_watermark
from src.watermark.detector import detect_watermark

WATERMARK_TEXT = "SocialNetwork0"
PICTURE_DIR = "tests/test_pictures"
TEMP_SUFFIX = "_watermarked_test"


def analyze_image(image_path):
    bgr = cv2.imread(image_path)
    if bgr is None:
        return None, None, None
    avg = bgr.mean()
    minv = bgr.min()
    maxv = bgr.max()
    return avg, minv, maxv


def test_image(image_path):
    print(f"\n🖼️ 测试图片: {image_path}")
    avg, minv, maxv = analyze_image(image_path)
    if avg is None:
        print(f"❌ 无法加载图片: {image_path}")
        return False
    print(f"   平均亮度: {avg:.1f}，最小: {minv}，最大: {maxv}")
    if avg > 200:
        print(f"⚠️  警告: 图片过亮，水印算法可能效果较差")
    if avg < 30:
        print(f"⚠️  警告: 图片过暗，水印算法可能效果较差")

    # 生成临时输出文件名
    ext = os.path.splitext(image_path)[-1]
    output_path = image_path.replace(ext, f"{TEMP_SUFFIX}{ext}")

    # 添加水印
    try:
        add_watermark(image_path, output_path, WATERMARK_TEXT)
    except Exception as e:
        print(f"❌ 添加水印失败: {e}")
        return False

    # 检测水印
    try:
        has_watermark, confidence, decoded = detect_watermark(
            image_path=output_path,
            watermark=WATERMARK_TEXT
        )
        
        # 获取匹配详情
        from src.watermark.detector import fuzzy_watermark_match
        is_match, similarity, match_reason = fuzzy_watermark_match(WATERMARK_TEXT, decoded)
        
        if has_watermark:
            print(f"✅ 检测成功！水印内容: '{decoded}' 置信度: {confidence:.2f}")
            print(f"   匹配原因: {match_reason}")
            os.remove(output_path)
            return True
        else:
            print(f"❌ 检测失败！解码内容: '{decoded}' 置信度: {confidence:.2f}")
            print(f"   匹配分析: {match_reason}")
            os.remove(output_path)
            return False
    except Exception as e:
        print(f"❌ 检测水印失败: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False


def main():
    print("\n===== 批量图片水印兼容性自动化测试 =====\n")
    image_files = []
    for ext in ('*.jpg', '*.jpeg', '*.png', '*.bmp'):
        image_files.extend(glob.glob(os.path.join(PICTURE_DIR, ext)))
    image_files.sort()
    
    total = len(image_files)
    success = 0
    for img in image_files:
        if test_image(img):
            success += 1
    print(f"\n===== 测试完成：共 {total} 张图片，成功 {success} 张，失败 {total-success} 张 =====\n")

if __name__ == "__main__":
    main() 