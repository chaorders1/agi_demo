#!/usr/bin/env python
"""
Invisible Watermark Tool
Add invisible watermarks to images using the invisible-watermark library
"""

import argparse
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
    import cv2
    
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
    import cv2
    
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


def main():
    parser = argparse.ArgumentParser(description='Add or extract invisible watermarks from images')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add watermark command
    add_parser = subparsers.add_parser('add', help='Add watermark to image')
    add_parser.add_argument('input', help='Input image path')
    add_parser.add_argument('output', nargs='?', help='Output image path (optional, defaults to input_watermarked.ext)')
    add_parser.add_argument('--text', '-t', required=True, help='Watermark text')
    add_parser.add_argument('--method', '-m', default='dwtDct', 
                          choices=['dwtDct', 'rivaGan'],
                          help='Watermarking method (default: dwtDct)')
    
    # Extract watermark command
    extract_parser = subparsers.add_parser('extract', help='Extract watermark from image')
    extract_parser.add_argument('image', help='Watermarked image path')
    extract_parser.add_argument('--length', '-l', type=int, required=True,
                              help='Length of watermark text')
    extract_parser.add_argument('--method', '-m', default='dwtDct',
                              choices=['dwtDct', 'rivaGan'],
                              help='Watermarking method (default: dwtDct)')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        # Validate input file exists
        if not os.path.exists(args.input):
            print(f"Error: Input file '{args.input}' not found")
            return 1
        
        # Auto-generate output filename if not provided
        if args.output is None:
            # Split the input path into name and extension
            input_dir = os.path.dirname(args.input)
            input_name = os.path.basename(args.input)
            name_without_ext, ext = os.path.splitext(input_name)
            
            # Generate output filename: input_watermarked.ext
            output_filename = f"{name_without_ext}_watermarked{ext}"
            args.output = os.path.join(input_dir, output_filename)
            print(f"Auto-generated output path: {args.output}")
            
        # Create output directory if needed
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        add_watermark(args.input, args.output, args.text, args.method)
        
    elif args.command == 'extract':
        # Validate input file exists
        if not os.path.exists(args.image):
            print(f"Error: Image file '{args.image}' not found")
            return 1
            
        watermark = extract_watermark(args.image, args.length, args.method)
        print(f"Extracted watermark: {watermark}")
        
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())