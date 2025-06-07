#!/usr/bin/env python
"""
Core watermark functionality
Handles adding and extracting invisible watermarks from images
"""

import cv2
import os
from imwatermark import WatermarkEncoder, WatermarkDecoder


def add_watermark(input_path, output_path, watermark_text, method='dwtDct'):
    """
    Add invisible watermark to an image
    
    Args:
        input_path: Path to input image
        output_path: Path to save watermarked image
        watermark_text: Text to embed as watermark
        method: Watermarking method ('dwtDct' or 'rivaGan')
    """
    # Load the image
    bgr = cv2.imread(input_path)
    if bgr is None:
        raise ValueError(f"Could not load image from {input_path}")
    
    # Encode watermark text
    wm_bytes = watermark_text.encode('utf-8')
    
    # Handle empty watermark
    if len(wm_bytes) == 0:
        print("Error: Watermark text cannot be empty")
        raise ValueError("Empty watermark text")
    
    # rivaGan only supports 32-bit (4 bytes) watermarks
    if method == 'rivaGan':
        if len(wm_bytes) > 4:
            print(f"Warning: rivaGan only supports 4 bytes. Truncating '{watermark_text}' to '{watermark_text[:4]}'")
            wm_bytes = wm_bytes[:4]
        elif len(wm_bytes) < 4:
            # Pad with zeros to make it exactly 4 bytes
            wm_bytes = wm_bytes.ljust(4, b'\x00')
    
    encoder = WatermarkEncoder()
    encoder.set_watermark('bytes', wm_bytes)
    
    # Add watermark to the image
    try:
        bgr_encoded = encoder.encode(bgr, method)
    except RuntimeError as e:
        if "loadModel" in str(e) and method == 'rivaGan':
            print("Error: rivaGan method requires pre-trained models that are not included.")
            print("Please use 'dwtDct' method instead (default).")
            raise ValueError("rivaGan method not available")
        else:
            raise
    
    # Save the watermarked image
    cv2.imwrite(output_path, bgr_encoded)
    print(f"✓ Watermarked image saved to: {output_path}")


def extract_watermark(image_path, watermark_length, method='dwtDct'):
    """
    Extract invisible watermark from an image
    
    Args:
        image_path: Path to watermarked image
        watermark_length: Length of the watermark text
        method: Watermarking method used ('dwtDct' or 'rivaGan')
    
    Returns:
        Extracted watermark text
    """
    # Load the image
    bgr = cv2.imread(image_path)
    if bgr is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    decoder = WatermarkDecoder('bytes', watermark_length)
    watermark = decoder.decode(bgr, method)
    try:
        return watermark.decode('utf-8')
    except UnicodeDecodeError:
        # If UTF-8 decoding fails, return hex representation
        return watermark.hex()


def auto_generate_output_path(input_path, suffix="_watermarked"):
    """
    Auto-generate output path based on input path
    
    Args:
        input_path: Input file path
        suffix: Suffix to add to filename
        
    Returns:
        Generated output path
    """
    input_dir = os.path.dirname(input_path)
    input_name = os.path.basename(input_path)
    name_without_ext, ext = os.path.splitext(input_name)
    
    output_filename = f"{name_without_ext}{suffix}{ext}"
    return os.path.join(input_dir, output_filename) 