#!/usr/bin/env python3
"""
Invisible Watermark Detection Tool with Confidence Levels
Works with the actual behavior of the invisible-watermark library
"""

import argparse
import cv2
import numpy as np
from imwatermark import WatermarkEncoder, WatermarkDecoder


def detect_watermark(image_path, method='dwtDct'):
    """
    Detect if an image has been processed by invisible-watermark library
    
    Since the library doesn't always preserve the exact watermark content,
    we detect based on the presence of watermark patterns in the image.
    """
    # Load the image
    bgr = cv2.imread(image_path)
    if bgr is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Create a reference image without watermark (solid color)
    reference = np.ones_like(bgr) * 128
    
    # Try to decode watermarks from both images
    has_watermark = False
    confidence = 0.0
    
    # Test multiple lengths
    test_lengths = [8, 16, 32, 64]
    
    for length in test_lengths:
        try:
            decoder = WatermarkDecoder('bytes', length)
            
            # Decode from target image
            wm_target = decoder.decode(bgr, method)
            
            # Decode from reference (should be noise/nothing meaningful)
            wm_ref = decoder.decode(reference, method)
            
            if wm_target is not None and wm_ref is not None:
                # Compare the statistical properties
                target_variance = np.var(list(wm_target))
                ref_variance = np.var(list(wm_ref))
                
                # If target has significantly different variance, likely has watermark
                if target_variance > 0 and abs(target_variance - ref_variance) > 10:
                    has_watermark = True
                    confidence = max(confidence, 0.7)
                    
                # Check for non-random patterns
                unique_target = len(set(wm_target))
                unique_ref = len(set(wm_ref))
                
                if unique_target < unique_ref * 0.8 and unique_target > 1:
                    has_watermark = True
                    confidence = max(confidence, 0.8)
                    
        except:
            continue
    
    # Additional check: Compare image statistics
    # Watermarked images often have subtle statistical differences
    original_mean = np.mean(bgr)
    original_std = np.std(bgr)
    
    # Check DCT coefficients for watermark artifacts
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Ensure the image dimensions are suitable for DCT (must be even)
    h, w = gray.shape
    if h % 2 != 0:
        gray = gray[:-1, :]
    if w % 2 != 0:
        gray = gray[:, :-1]
    
    # Resize to a standard size for DCT if needed
    if gray.shape[0] < 8 or gray.shape[1] < 8:
        gray = cv2.resize(gray, (max(8, gray.shape[1]), max(8, gray.shape[0])))
    
    try:
        dct = cv2.dct(np.float32(gray))
        dct_std = np.std(dct)
    except:
        # If DCT fails, use a default value
        dct_std = original_std
    
    # Heuristic: watermarked images tend to have slightly different DCT statistics
    if dct_std > original_std * 1.01:
        confidence = max(confidence, 0.6)
        has_watermark = True
    
    return has_watermark, confidence


def main():
    parser = argparse.ArgumentParser(description='Detect invisible watermarks with confidence')
    parser.add_argument('image', help='Image file to check')
    parser.add_argument('--method', '-m', default='dwtDct',
                        choices=['dwtDct', 'rivaGan'],
                        help='Watermarking method (default: dwtDct)')
    parser.add_argument('--confidence', '-c', action='store_true',
                        help='Show confidence level')
    
    args = parser.parse_args()
    
    try:
        has_watermark, confidence = detect_watermark(args.image, args.method)
        
        if args.confidence:
            if has_watermark:
                print(f"yes (confidence: {confidence:.1%})")
            else:
                print("no")
        else:
            print("yes" if has_watermark else "no")
        
        return 0 if has_watermark else 1
        
    except Exception as e:
        print(f"Error: {e}")
        return 2


if __name__ == '__main__':
    exit(main())