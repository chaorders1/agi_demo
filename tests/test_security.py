#!/usr/bin/env python
"""
水印安全性自动化测试
测试各种hack尝试和变种，确保只有正确的水印才能被检测到
"""

import subprocess
import sys
import os
from typing import List, Tuple


def run_watermark_detection(image_path: str, watermark_text: str) -> str:
    """
    运行水印检测命令并返回结果
    
    Args:
        image_path: 图片路径
        watermark_text: 要检测的水印文字
        
    Returns:
        检测结果 ('yes' 或 'no')
    """
    try:
        result = subprocess.run([
            'python', '-m', 'src.watermark.cli', 'detect',
            image_path, 
            '--watermark', watermark_text
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return result.stdout.strip()
        elif result.returncode == 1:
            # 返回码1表示没有找到水印，这是正常的
            return "no"
        else:
            # 其他错误
            error_msg = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
            return f"ERROR: {error_msg}"
    except subprocess.TimeoutExpired:
        return "ERROR: Timeout"
    except Exception as e:
        return f"ERROR: {str(e)}"


def generate_hack_variants(original_watermark: str) -> List[Tuple[str, str]]:
    """
    生成各种可能的hack变种
    
    Args:
        original_watermark: 原始水印文字
        
    Returns:
        (变种文字, 描述) 的列表
    """
    variants = []
    
    # 1. 大小写变化
    variants.extend([
        (original_watermark.upper(), "全大写"),
        (original_watermark.lower(), "全小写"),
        (original_watermark.capitalize(), "首字母大写"),
        (original_watermark.swapcase(), "大小写互换"),
    ])
    
    # 2. 部分匹配尝试
    if len(original_watermark) > 1:
        variants.extend([
            (original_watermark[:-1], "去掉最后一个字符"),
            (original_watermark[1:], "去掉第一个字符"),
            (original_watermark[:len(original_watermark)//2], "前半部分"),
            (original_watermark[len(original_watermark)//2:], "后半部分"),
        ])
    
    # 3. 添加字符
    variants.extend([
        (original_watermark + "1", "末尾加数字"),
        (original_watermark + "x", "末尾加字母"),
        ("x" + original_watermark, "开头加字母"),
        (original_watermark + " ", "末尾加空格"),
        (" " + original_watermark, "开头加空格"),
    ])
    
    # 4. 替换字符
    if len(original_watermark) > 0:
        replacements = [
            ('0', 'O', "数字0替换为字母O"),
            ('1', 'l', "数字1替换为小写L"),
            ('S', '5', "字母S替换为数字5"),
            ('o', '0', "小写o替换为数字0"),
        ]
        
        for old_char, new_char, description in replacements:
            if old_char in original_watermark:
                replaced = original_watermark.replace(old_char, new_char)
                if replaced != original_watermark:  # 确保确实发生了替换
                    variants.append((replaced, description))
    
    # 5. 特殊字符和编码
    variants.extend([
        (original_watermark + "\n", "末尾加换行符"),
        (original_watermark + "\t", "末尾加制表符"),
        ("*" + original_watermark + "*", "前后加星号"),
        (f'"{original_watermark}"', "加双引号"),
        (f"'{original_watermark}'", "加单引号"),
    ])
    
    # 6. 常见hack尝试
    variants.extend([
        ("", "空字符串"),
        ("*", "通配符"),
        (".*", "正则表达式通配符"),
        ("admin", "常见hack词汇"),
        ("password", "常见hack词汇"),
        ("123456", "常见数字序列"),
        ("test", "测试词汇"),
        ("null", "空值词汇"),
        ("undefined", "未定义词汇"),
    ])
    
    # 7. Unicode和特殊编码
    variants.extend([
        ("SocialNetwork０", "全角数字0"),
        ("ＳocialNetwork0", "全角字母S"),
        ("Social​Network0", "零宽字符"),
        ("SocialNetwork0\u200b", "零宽空格"),
    ])
    
    return variants


def run_security_test(image_path: str, correct_watermark: str):
    """
    运行完整的安全性测试
    
    Args:
        image_path: 测试图片路径
        correct_watermark: 正确的水印文字
    """
    print("🔒 水印安全性自动化测试")
    print("=" * 50)
    print(f"测试图片: {image_path}")
    print(f"正确水印: '{correct_watermark}'")
    print()
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"❌ 错误: 图片文件 '{image_path}' 不存在")
        return
    
    # 1. 测试正确的水印
    print("✅ 测试正确水印:")
    correct_result = run_watermark_detection(image_path, correct_watermark)
    print(f"   '{correct_watermark}' -> {correct_result}")
    
    if correct_result != "yes":
        print("❌ 警告: 正确的水印检测失败!")
        return
    
    print()
    
    # 2. 生成并测试各种变种
    variants = generate_hack_variants(correct_watermark)
    
    print("🔍 测试各种hack尝试和变种:")
    print("-" * 30)
    
    failed_tests = []
    passed_tests = []
    error_tests = []
    
    for i, (variant, description) in enumerate(variants, 1):
        result = run_watermark_detection(image_path, variant)
        
        status_icon = ""
        if result == "no":
            status_icon = "✅"
            passed_tests.append((variant, description))
        elif result == "yes":
            status_icon = "❌"
            failed_tests.append((variant, description))
        else:
            status_icon = "⚠️"
            error_tests.append((variant, description, result))
        
        print(f"{status_icon} {i:2d}. {description:<20} '{variant}' -> {result}")
    
    # 3. 总结报告
    print()
    print("📊 测试总结:")
    print("=" * 30)
    print(f"总测试数量: {len(variants)}")
    print(f"✅ 安全通过: {len(passed_tests)} (正确返回no)")
    print(f"❌ 安全失败: {len(failed_tests)} (错误返回yes)")
    print(f"⚠️  测试错误: {len(error_tests)}")
    
    if failed_tests:
        print()
        print("🚨 安全风险警告:")
        print("以下变种被错误识别为有效水印:")
        for variant, description in failed_tests:
            print(f"   - {description}: '{variant}'")
    
    if error_tests:
        print()
        print("⚠️  测试错误详情:")
        for variant, description, error in error_tests:
            print(f"   - {description}: '{variant}' -> {error}")
    
    # 4. 安全评分
    if len(variants) > 0:
        security_score = (len(passed_tests) / len(variants)) * 100
        print()
        print(f"🛡️  安全评分: {security_score:.1f}%")
        
        if security_score >= 95:
            print("   评级: 优秀 🌟")
        elif security_score >= 85:
            print("   评级: 良好 👍")
        elif security_score >= 70:
            print("   评级: 一般 ⚠️")
        else:
            print("   评级: 需要改进 🚨")


def main():
    """主函数"""
    # 默认测试参数
    default_image = "people_watermarked.png"
    default_watermark = "SocialNetwork0"
    
    # 解析命令行参数
    if len(sys.argv) >= 2:
        image_path = sys.argv[1]
    else:
        image_path = default_image
    
    if len(sys.argv) >= 3:
        watermark_text = sys.argv[2]
    else:
        watermark_text = default_watermark
    
    # 运行测试
    run_security_test(image_path, watermark_text)


if __name__ == "__main__":
    main() 