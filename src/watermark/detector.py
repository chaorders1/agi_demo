#!/usr/bin/env python
"""
Watermark detection functionality
Handles detecting and verifying invisible watermarks in images
"""

import cv2
import numpy as np
from imwatermark import WatermarkDecoder


def calculate_similarity(str1, str2):
    """
    计算两个字符串的相似度
    使用编辑距离算法
    
    Returns:
        Float between 0-1, 1为完全相同
    """
    if not str1 or not str2:
        return 0.0
    
    # 计算编辑距离
    def edit_distance(s1, s2):
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
            
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
        
        return dp[m][n]
    
    distance = edit_distance(str1.lower(), str2.lower())
    max_len = max(len(str1), len(str2))
    
    if max_len == 0:
        return 1.0
    
    similarity = 1 - (distance / max_len)
    return max(0.0, similarity)


def fuzzy_watermark_match(expected, decoded, similarity_threshold=0.8):
    """
    模糊匹配水印内容
    
    Args:
        expected: 期望的水印内容
        decoded: 解码得到的内容
        similarity_threshold: 相似度阈值
        
    Returns:
        (is_match, similarity_score, match_reason)
    """
    if not decoded:
        return False, 0.0, "解码内容为空"
    
    # 1. 精确匹配
    if decoded == expected:
        return True, 1.0, "精确匹配"
    
    # 2. 相似度匹配
    similarity = calculate_similarity(expected, decoded)
    if similarity >= similarity_threshold:
        return True, similarity, f"高相似度匹配 ({similarity:.1%})"
    
    # 3. 包含关键词匹配
    # 提取主要关键词（长度 >= 4 的子串）
    keywords = []
    expected_lower = expected.lower()
    for i in range(len(expected_lower) - 3):
        keyword = expected_lower[i:i+4]
        if keyword.isalnum():
            keywords.append(keyword)
    
    decoded_lower = decoded.lower()
    matched_keywords = sum(1 for kw in keywords if kw in decoded_lower)
    keyword_ratio = matched_keywords / len(keywords) if keywords else 0
    
    if keyword_ratio >= 0.6:  # 60%的关键词匹配
        return True, keyword_ratio, f"关键词匹配 ({keyword_ratio:.1%})"
    
    # 4. 编辑距离匹配（允许1-2个字符差异）
    distance = abs(len(expected) - len(decoded))
    if distance <= 2 and similarity >= 0.6:
        return True, similarity, f"编辑距离匹配 (相似度: {similarity:.1%})"
    
    return False, similarity, f"不匹配 (相似度: {similarity:.1%})"


def detect_watermark(image_path, method='dwtDct', watermark=None, length=None):
    """
    检测图片是否包含指定水印内容。
    如果提供了水印内容，则解码后与输入内容比对，一致才算有水印。
    如果未提供水印内容，则只输出解码内容，不做自动判断。
    
    Args:
        image_path: Path to the image file
        method: Watermarking method ('dwtDct' or 'rivaGan')
        watermark: Expected watermark content (string)
        length: Watermark length in bits (optional, auto-calculated if watermark provided)
        
    Returns:
        Tuple of (has_watermark, confidence, decoded_content)
        - has_watermark: Boolean or None (if no expected watermark provided)
        - confidence: Float between 0-1 or None
        - decoded_content: Decoded watermark string or None
    """
    bgr = cv2.imread(image_path)
    if bgr is None:
        raise ValueError(f"Could not load image from {image_path}")

    # 自动推断长度
    if watermark is not None and length is None:
        length = len(watermark.encode('utf-8')) * 8

    if watermark is not None and length is not None:
        decoder = WatermarkDecoder('bytes', length)
        try:
            wm_decoded = decoder.decode(bgr, method)
            if wm_decoded is not None:
                try:
                    wm_decoded_str = wm_decoded.decode('utf-8')
                except Exception:
                    wm_decoded_str = str(wm_decoded)
                
                # 使用模糊匹配而不是精确匹配
                is_match, similarity, match_reason = fuzzy_watermark_match(watermark, wm_decoded_str)
                
                if is_match:
                    return True, similarity, wm_decoded_str
                else:
                    return False, similarity, wm_decoded_str
            else:
                return False, 0.0, None
        except Exception as e:
            return False, 0.0, None
    else:
        # 未输入水印内容，只做解码
        # 默认尝试32位长度
        try_lengths = [32, 64, 16, 8] if length is None else [length]
        for l in try_lengths:
            decoder = WatermarkDecoder('bytes', l)
            try:
                wm_decoded = decoder.decode(bgr, method)
                if wm_decoded is not None:
                    try:
                        wm_decoded_str = wm_decoded.decode('utf-8')
                    except Exception:
                        wm_decoded_str = str(wm_decoded)
                    return None, None, wm_decoded_str
            except Exception:
                continue
        return None, None, None


def verify_watermark(image_path, expected_watermark, method='dwtDct'):
    """
    Verify if an image contains the expected watermark
    
    Args:
        image_path: Path to the image file
        expected_watermark: Expected watermark text
        method: Watermarking method ('dwtDct' or 'rivaGan')
        
    Returns:
        Boolean indicating if the watermark matches
    """
    has_watermark, confidence, decoded = detect_watermark(
        image_path, method, expected_watermark
    )
    return has_watermark is True


def extract_any_watermark(image_path, method='dwtDct', max_length=512):
    """
    Try to extract any watermark from an image by testing different lengths
    
    Args:
        image_path: Path to the image file
        method: Watermarking method ('dwtDct' or 'rivaGan')
        max_length: Maximum length to try (in bits)
        
    Returns:
        List of possible watermark strings found
    """
    bgr = cv2.imread(image_path)
    if bgr is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    found_watermarks = []
    
    # Try common lengths
    test_lengths = [32, 64, 96, 128, 160, 192, 224, 256]
    test_lengths.extend(range(8, min(max_length, 256), 8))  # Try every 8 bits
    
    for length in sorted(set(test_lengths)):
        if length > max_length:
            break
            
        try:
            decoder = WatermarkDecoder('bytes', length)
            wm_decoded = decoder.decode(bgr, method)
            
            if wm_decoded is not None:
                try:
                    wm_decoded_str = wm_decoded.decode('utf-8')
                    # Filter out obviously invalid results
                    if (len(wm_decoded_str.strip()) > 0 and 
                        all(ord(c) < 128 for c in wm_decoded_str) and  # ASCII only
                        not all(c in '\x00\xff\x7f' for c in wm_decoded_str)):  # Not all control chars
                        found_watermarks.append({
                            'length': length,
                            'content': wm_decoded_str,
                            'raw_bytes': wm_decoded
                        })
                except UnicodeDecodeError:
                    # Try hex representation for non-UTF8 data
                    hex_str = wm_decoded.hex()
                    if len(hex_str) > 0 and hex_str != 'ff' * (length // 8):
                        found_watermarks.append({
                            'length': length,
                            'content': f"[HEX] {hex_str}",
                            'raw_bytes': wm_decoded
                        })
        except Exception:
            continue
    
    return found_watermarks 