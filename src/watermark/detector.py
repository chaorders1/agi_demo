#!/usr/bin/env python
"""
Watermark detection functionality
Handles detecting and verifying invisible watermarks in images
"""

import cv2
import numpy as np
from imwatermark import WatermarkDecoder
import hashlib
import re


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


def bytes_to_text_smart(data_bytes):
    """
    智能地将字节数据转换为文本
    尝试多种编码和修复策略
    
    Args:
        data_bytes: 原始字节数据
        
    Returns:
        (decoded_text, encoding_used, confidence)
    """
    if not data_bytes:
        return None, None, 0.0
    
    # 尝试的编码列表
    encodings = ['utf-8', 'ascii', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            decoded = data_bytes.decode(encoding)
            # 检查是否包含可打印字符
            printable_ratio = sum(1 for c in decoded if c.isprintable()) / len(decoded) if decoded else 0
            if printable_ratio > 0.7:  # 70%以上是可打印字符
                return decoded, encoding, printable_ratio
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    # 如果所有编码都失败，尝试忽略错误
    for encoding in encodings:
        try:
            decoded = data_bytes.decode(encoding, errors='ignore')
            if decoded and len(decoded) > 0:
                printable_ratio = sum(1 for c in decoded if c.isprintable()) / len(decoded)
                return decoded, f"{encoding}(ignore)", printable_ratio * 0.5  # 降低置信度
        except:
            continue
    
    # 最后尝试替换错误字符
    try:
        decoded = data_bytes.decode('utf-8', errors='replace')
        return decoded, "utf-8(replace)", 0.3
    except:
        return data_bytes.hex(), "hex", 0.1


def fuzzy_watermark_match(expected, decoded, similarity_threshold=0.6):
    """
    模糊匹配水印内容 - 优化版本
    
    Args:
        expected: 期望的水印内容
        decoded: 解码得到的内容
        similarity_threshold: 相似度阈值 (降低到0.6)
        
    Returns:
        (is_match, similarity_score, match_reason)
    """
    if not decoded:
        return False, 0.0, "解码内容为空"
    
    # 预处理：移除不可打印字符和空白
    def clean_text(text):
        if not text:
            return ""
        # 移除不可打印字符，保留字母数字和基本符号
        cleaned = re.sub(r'[^\w\s\-_.]', '', text)
        return cleaned.strip()
    
    expected_clean = clean_text(expected)
    decoded_clean = clean_text(decoded)
    
    # 1. 精确匹配
    if decoded == expected:
        return True, 1.0, "精确匹配"
    
    # 2. 清理后精确匹配
    if decoded_clean == expected_clean and expected_clean:
        return True, 0.95, "清理后精确匹配"
    
    # 3. 相似度匹配
    similarity = calculate_similarity(expected, decoded)
    if similarity >= similarity_threshold:
        return True, similarity, f"高相似度匹配 ({similarity:.1%})"
    
    # 4. 清理后相似度匹配
    if expected_clean and decoded_clean:
        clean_similarity = calculate_similarity(expected_clean, decoded_clean)
        if clean_similarity >= similarity_threshold:
            return True, clean_similarity, f"清理后相似度匹配 ({clean_similarity:.1%})"
    
    # 5. 包含关键词匹配
    if len(expected) >= 4:
        keywords = []
        expected_lower = expected.lower()
        # 提取长度>=3的子串作为关键词
        for i in range(len(expected_lower) - 2):
            keyword = expected_lower[i:i+3]
            if keyword.isalnum():
                keywords.append(keyword)
        
        if keywords:
            decoded_lower = decoded.lower()
            matched_keywords = sum(1 for kw in keywords if kw in decoded_lower)
            keyword_ratio = matched_keywords / len(keywords)
            
            if keyword_ratio >= 0.5:  # 50%的关键词匹配
                return True, keyword_ratio * 0.8, f"关键词匹配 ({keyword_ratio:.1%})"
    
    # 6. 字符频率匹配
    def char_frequency(text):
        freq = {}
        for char in text.lower():
            if char.isalnum():
                freq[char] = freq.get(char, 0) + 1
        return freq
    
    expected_freq = char_frequency(expected)
    decoded_freq = char_frequency(decoded)
    
    if expected_freq and decoded_freq:
        common_chars = set(expected_freq.keys()) & set(decoded_freq.keys())
        if common_chars:
            freq_similarity = len(common_chars) / max(len(expected_freq), len(decoded_freq))
            if freq_similarity >= 0.6:
                return True, freq_similarity * 0.7, f"字符频率匹配 ({freq_similarity:.1%})"
    
    # 7. 长度相似性检查
    if abs(len(expected) - len(decoded)) <= 2 and similarity >= 0.4:
        return True, similarity * 0.8, f"长度相似匹配 (相似度: {similarity:.1%})"
    
    return False, similarity, f"不匹配 (相似度: {similarity:.1%})"


def create_watermark_signature(text):
    """
    为水印文本创建特征签名
    用于在数据损坏时进行模糊匹配
    
    Args:
        text: 原始水印文本
        
    Returns:
        dict: 包含多种特征的签名
    """
    signature = {
        'text': text,
        'length': len(text),
        'byte_length': len(text.encode('utf-8')),
        'bit_length': len(text.encode('utf-8')) * 8,
        'hash_md5': hashlib.md5(text.encode('utf-8')).hexdigest(),
        'hash_sha1': hashlib.sha1(text.encode('utf-8')).hexdigest()[:16],  # 前16位
        'char_set': set(text.lower()),
        'char_freq': {},
        'patterns': []
    }
    
    # 字符频率
    for char in text.lower():
        signature['char_freq'][char] = signature['char_freq'].get(char, 0) + 1
    
    # 提取模式（连续的字母/数字序列）
    patterns = re.findall(r'[a-zA-Z]+|\d+', text)
    signature['patterns'] = [p.lower() for p in patterns if len(p) >= 2]
    
    return signature


def match_by_signature(expected_signature, decoded_bytes, decoded_text):
    """
    基于签名进行模糊匹配
    
    Args:
        expected_signature: 期望的水印签名
        decoded_bytes: 解码的字节数据
        decoded_text: 解码的文本（可能损坏）
        
    Returns:
        (is_match, confidence, reason)
    """
    if not decoded_text:
        return False, 0.0, "无解码文本"
    
    scores = []
    reasons = []
    
    # 1. 长度匹配
    if abs(len(decoded_text) - expected_signature['length']) <= 2:
        length_score = 1.0 - abs(len(decoded_text) - expected_signature['length']) / max(len(decoded_text), expected_signature['length'])
        scores.append(length_score * 0.2)
        reasons.append(f"长度相似 ({length_score:.1%})")
    
    # 2. 字符集重叠
    decoded_char_set = set(decoded_text.lower())
    char_overlap = len(expected_signature['char_set'] & decoded_char_set)
    if char_overlap > 0:
        char_score = char_overlap / len(expected_signature['char_set'])
        scores.append(char_score * 0.3)
        reasons.append(f"字符集重叠 ({char_score:.1%})")
    
    # 3. 模式匹配
    if expected_signature['patterns']:
        decoded_patterns = re.findall(r'[a-zA-Z]+|\d+', decoded_text)
        decoded_patterns = [p.lower() for p in decoded_patterns if len(p) >= 2]
        
        pattern_matches = 0
        for expected_pattern in expected_signature['patterns']:
            for decoded_pattern in decoded_patterns:
                if expected_pattern in decoded_pattern or decoded_pattern in expected_pattern:
                    pattern_matches += 1
                    break
        
        if pattern_matches > 0:
            pattern_score = pattern_matches / len(expected_signature['patterns'])
            scores.append(pattern_score * 0.4)
            reasons.append(f"模式匹配 ({pattern_score:.1%})")
    
    # 4. 字节级相似性
    if decoded_bytes:
        expected_bytes = expected_signature['text'].encode('utf-8')
        byte_similarity = 0
        min_len = min(len(decoded_bytes), len(expected_bytes))
        if min_len > 0:
            matching_bytes = sum(1 for i in range(min_len) if decoded_bytes[i] == expected_bytes[i])
            byte_similarity = matching_bytes / min_len
            if byte_similarity > 0.3:
                scores.append(byte_similarity * 0.1)
                reasons.append(f"字节相似 ({byte_similarity:.1%})")
    
    # 综合评分
    total_score = sum(scores) if scores else 0.0
    is_match = total_score >= 0.4  # 降低阈值到40%
    
    return is_match, total_score, "; ".join(reasons) if reasons else "无匹配特征"


def detect_watermark_robust(image_path, method='dwtDct', watermark=None, length=None):
    """
    鲁棒性水印检测 - 能够处理数据损坏的情况
    
    Args:
        image_path: Path to the image file
        method: Watermarking method ('dwtDct' or 'rivaGan')
        watermark: Expected watermark content (string)
        length: Watermark length in bits (optional)
        
    Returns:
        Tuple of (has_watermark, confidence, decoded_content, debug_info)
    """
    bgr = cv2.imread(image_path)
    if bgr is None:
        raise ValueError(f"Could not load image from {image_path}")

    debug_info = {
        'tried_lengths': [],
        'decoding_attempts': [],
        'signature_matches': [],
        'best_matches': []
    }

    # 创建期望水印的签名
    expected_signature = None
    if watermark:
        expected_signature = create_watermark_signature(watermark)
        debug_info['expected_signature'] = expected_signature

    # 计算测试长度
    test_lengths = []
    if watermark:
        base_length = len(watermark.encode('utf-8')) * 8
        # 扩大搜索范围
        for offset in range(-32, 33, 8):  # -32到+32，每8位一个步长
            new_length = base_length + offset
            if 8 <= new_length <= 512:
                test_lengths.append(new_length)
    
    if length:
        test_lengths.insert(0, length)
    
    # 添加常见长度
    common_lengths = [32, 64, 96, 112, 128, 160, 192, 224, 256]
    for cl in common_lengths:
        if cl not in test_lengths:
            test_lengths.append(cl)
    
    test_lengths = sorted(list(set(test_lengths)))
    debug_info['tried_lengths'] = test_lengths
    
    best_result = None
    best_confidence = 0.0
    
    for test_length in test_lengths:
        try:
            decoder = WatermarkDecoder('bytes', test_length)
            decoded_bytes = decoder.decode(bgr, method)
            
            attempt_info = {
                'length': test_length,
                'success': False,
                'raw_bytes': None,
                'decoded_text': None,
                'encoding': None,
                'fuzzy_match': None,
                'signature_match': None
            }
            
            if decoded_bytes is not None:
                attempt_info['success'] = True
                attempt_info['raw_bytes'] = decoded_bytes.hex()
                
                # 智能文本转换
                decoded_text, encoding_used, text_confidence = bytes_to_text_smart(decoded_bytes)
                attempt_info['decoded_text'] = decoded_text
                attempt_info['encoding'] = encoding_used
                
                if watermark and decoded_text:
                    # 传统模糊匹配
                    is_fuzzy_match, fuzzy_similarity, fuzzy_reason = fuzzy_watermark_match(watermark, decoded_text)
                    attempt_info['fuzzy_match'] = {
                        'is_match': is_fuzzy_match,
                        'similarity': fuzzy_similarity,
                        'reason': fuzzy_reason
                    }
                    
                    # 签名匹配
                    is_sig_match, sig_similarity, sig_reason = match_by_signature(
                        expected_signature, decoded_bytes, decoded_text
                    )
                    attempt_info['signature_match'] = {
                        'is_match': is_sig_match,
                        'similarity': sig_similarity,
                        'reason': sig_reason
                    }
                    
                    # 综合判断：任一方法匹配即认为找到
                    is_match = is_fuzzy_match or is_sig_match
                    # 综合置信度：取较高者，但给签名匹配更高权重
                    combined_confidence = max(
                        fuzzy_similarity * text_confidence,
                        sig_similarity * text_confidence * 1.2  # 签名匹配权重更高
                    )
                    
                    if is_match and (best_result is None or combined_confidence > best_confidence):
                        match_method = "模糊匹配" if is_fuzzy_match else "签名匹配"
                        match_reason = fuzzy_reason if is_fuzzy_match else sig_reason
                        
                        best_result = (True, combined_confidence, decoded_text, test_length, match_method, match_reason)
                        best_confidence = combined_confidence
                        
                        debug_info['best_matches'].append({
                            'length': test_length,
                            'confidence': combined_confidence,
                            'text': decoded_text,
                            'method': match_method,
                            'reason': match_reason
                        })
                
            debug_info['decoding_attempts'].append(attempt_info)
            
        except Exception as e:
            debug_info['decoding_attempts'].append({
                'length': test_length,
                'success': False,
                'error': str(e)
            })
    
    # 返回最佳结果
    if best_result:
        has_watermark, confidence, decoded_text, used_length, match_method, match_reason = best_result
        debug_info['used_length'] = used_length
        debug_info['match_method'] = match_method
        debug_info['match_reason'] = match_reason
        return has_watermark, confidence, decoded_text, debug_info
    
    # 如果没有找到匹配，返回最有希望的解码结果
    for attempt in debug_info['decoding_attempts']:
        if attempt['success'] and attempt['decoded_text']:
            return False, 0.0, attempt['decoded_text'], debug_info
    
    return False, 0.0, None, debug_info


def detect_watermark(image_path, method='dwtDct', watermark=None, length=None):
    """
    检测图片是否包含指定水印内容 - 兼容原接口
    """
    has_watermark, confidence, decoded_content, debug_info = detect_watermark_robust(
        image_path, method, watermark, length
    )
    return has_watermark, confidence, decoded_content


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