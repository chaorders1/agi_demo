#!/usr/bin/env python
"""
Watermark detection functionality
Handles detecting and verifying invisible watermarks in images
"""

import cv2
import numpy as np
from imwatermark import WatermarkDecoder


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
                if wm_decoded_str == watermark:
                    return True, 1.0, wm_decoded_str
                else:
                    return False, 0.0, wm_decoded_str
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