#!/usr/bin/env python3
"""
Invisible Watermark Detection Tool with Confidence Levels
Works with the actual behavior of the invisible-watermark library
"""

import argparse
import cv2
import numpy as np
from imwatermark import WatermarkEncoder, WatermarkDecoder


def detect_watermark(image_path, method='dwtDct', watermark=None, length=None):
    """
    检测图片是否包含指定水印内容。
    如果提供了水印内容，则解码后与输入内容比对，一致才算有水印。
    如果未提供水印内容，则只输出解码内容，不做自动判断。
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


def main():
    parser = argparse.ArgumentParser(description='Detect invisible watermarks with confidence')
    parser.add_argument('image', help='Image file to check')
    parser.add_argument('--method', '-m', default='dwtDct',
                        choices=['dwtDct', 'rivaGan'],
                        help='Watermarking method (default: dwtDct)')
    parser.add_argument('--confidence', '-c', action='store_true',
                        help='Show confidence level')
    parser.add_argument('--watermark', '-w', type=str, default=None,
                        help='Known watermark content (string)')
    parser.add_argument('--length', '-l', type=int, default=None,
                        help='Watermark length in bits (optional, auto if not set)')
    args = parser.parse_args()

    try:
        has_watermark, confidence, decoded = detect_watermark(
            args.image, args.method, args.watermark, args.length)
        if args.watermark is not None:
            if has_watermark:
                if args.confidence:
                    print(f"yes (confidence: {confidence:.0%})")
                else:
                    print("yes")
            else:
                if args.confidence:
                    print(f"no (decoded: {decoded})")
                else:
                    print("no")
        else:
            print(f"[未输入水印内容，无法自动判断] 解码内容: {decoded}")
        return 0 if has_watermark else 1
    except Exception as e:
        print(f"Error: {e}")
        return 2


if __name__ == '__main__':
    exit(main())