#!/usr/bin/env python
"""
Command Line Interface for the watermark library
Provides unified access to all watermark functionality
"""

import argparse
import os
import sys
from .core import add_watermark, extract_watermark, auto_generate_output_path
from .detector import detect_watermark, verify_watermark, extract_any_watermark


def cmd_add(args):
    """Handle the 'add' command"""
    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        return 1
    
    # Auto-generate output filename if not provided
    if args.output is None:
        args.output = auto_generate_output_path(args.input)
        print(f"Auto-generated output path: {args.output}")
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        add_watermark(args.input, args.output, args.text, args.method)
        return 0
    except Exception as e:
        print(f"Error adding watermark: {e}")
        return 1


def cmd_extract(args):
    """Handle the 'extract' command"""
    if not os.path.exists(args.image):
        print(f"Error: Image file '{args.image}' not found")
        return 1
    
    try:
        watermark = extract_watermark(args.image, args.length, args.method)
        print(f"Extracted watermark: {watermark}")
        return 0
    except Exception as e:
        print(f"Error extracting watermark: {e}")
        return 1


def cmd_detect(args):
    """Handle the 'detect' command"""
    if not os.path.exists(args.image):
        print(f"Error: Image file '{args.image}' not found")
        return 1
    
    try:
        from .detector import detect_watermark_robust
        
        has_watermark, confidence, decoded, debug_info = detect_watermark_robust(
            image_path=args.image, 
            method=args.method, 
            watermark=args.watermark, 
            length=args.length
        )
        
        if args.watermark is not None:
            if has_watermark:
                if args.confidence:
                    print(f"yes (confidence: {confidence:.0%})")
                    if args.verbose:
                        print(f"📊 检测详情:")
                        print(f"   使用长度: {debug_info.get('used_length', 'unknown')} 位")
                        print(f"   解码文本: '{decoded}'")
                        if debug_info.get('best_matches'):
                            best_match = debug_info['best_matches'][-1]
                            print(f"   匹配原因: {best_match['reason']}")
                else:
                    print("yes")
                return 0
            else:
                if args.confidence:
                    print(f"no (decoded: {decoded})")
                    if args.verbose and debug_info.get('decoding_attempts'):
                        print(f"📊 尝试了 {len(debug_info['tried_lengths'])} 种长度")
                        successful_attempts = [a for a in debug_info['decoding_attempts'] if a['success']]
                        if successful_attempts:
                            print(f"   成功解码 {len(successful_attempts)} 次，但无匹配")
                            for attempt in successful_attempts[:3]:  # 显示前3个
                                print(f"   - 长度{attempt['length']}: '{attempt['decoded_text']}'")
                else:
                    print("no")
                return 1
        else:
            print(f"[未输入水印内容，无法自动判断] 解码内容: {decoded}")
            return 0
    except Exception as e:
        print(f"Error: {e}")
        return 2


def cmd_scan(args):
    """Handle the 'scan' command - try to find any watermarks"""
    if not os.path.exists(args.image):
        print(f"Error: Image file '{args.image}' not found")
        return 1
    
    try:
        found_watermarks = extract_any_watermark(args.image, args.method, args.max_length)
        
        if found_watermarks:
            print(f"Found {len(found_watermarks)} possible watermark(s):")
            for i, wm in enumerate(found_watermarks, 1):
                print(f"{i}. Length: {wm['length']} bits")
                print(f"   Content: {wm['content']}")
                if args.verbose:
                    print(f"   Raw bytes: {wm['raw_bytes']}")
                print()
        else:
            print("No watermarks found")
            return 1
        
        return 0
    except Exception as e:
        print(f"Error scanning for watermarks: {e}")
        return 2


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Invisible Watermark Tool - Add, extract, and detect watermarks in images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add watermark (auto-generate output filename)
  watermark add image.png --text "My Watermark"
  
  # Add watermark with custom output
  watermark add image.png output.png --text "My Watermark"
  
  # Detect specific watermark
  watermark detect image.png --watermark "My Watermark"
  
  # Extract watermark with known length
  watermark extract image.png --length 88
  
  # Scan for any watermarks
  watermark scan image.png
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add watermark command
    add_parser = subparsers.add_parser('add', help='Add watermark to image')
    add_parser.add_argument('input', help='Input image path')
    add_parser.add_argument('output', nargs='?', help='Output image path (optional, auto-generated if not provided)')
    add_parser.add_argument('--text', '-t', required=True, help='Watermark text')
    add_parser.add_argument('--method', '-m', default='dwtDct', 
                          choices=['dwtDct', 'rivaGan'],
                          help='Watermarking method (default: dwtDct)')
    
    # Extract watermark command
    extract_parser = subparsers.add_parser('extract', help='Extract watermark from image')
    extract_parser.add_argument('image', help='Watermarked image path')
    extract_parser.add_argument('--length', '-l', type=int, required=True,
                              help='Length of watermark in bits')
    extract_parser.add_argument('--method', '-m', default='dwtDct',
                              choices=['dwtDct', 'rivaGan'],
                              help='Watermarking method (default: dwtDct)')
    
    # Detect watermark command
    detect_parser = subparsers.add_parser('detect', help='Detect specific watermark in image')
    detect_parser.add_argument('image', help='Image file to check')
    detect_parser.add_argument('--watermark', '-w', type=str, required=True,
                             help='Expected watermark content')
    detect_parser.add_argument('--method', '-m', default='dwtDct',
                             choices=['dwtDct', 'rivaGan'],
                             help='Watermarking method (default: dwtDct)')
    detect_parser.add_argument('--confidence', '-c', action='store_true',
                             help='Show confidence level')
    detect_parser.add_argument('--length', '-l', type=int, default=None,
                             help='Watermark length in bits (auto-calculated if not provided)')
    detect_parser.add_argument('--verbose', '-v', action='store_true',
                             help='Show detailed detection information')
    
    # Scan for watermarks command
    scan_parser = subparsers.add_parser('scan', help='Scan image for any watermarks')
    scan_parser.add_argument('image', help='Image file to scan')
    scan_parser.add_argument('--method', '-m', default='dwtDct',
                           choices=['dwtDct', 'rivaGan'],
                           help='Watermarking method (default: dwtDct)')
    scan_parser.add_argument('--max-length', type=int, default=512,
                           help='Maximum watermark length to try (default: 512)')
    scan_parser.add_argument('--verbose', '-v', action='store_true',
                           help='Show detailed information')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        return cmd_add(args)
    elif args.command == 'extract':
        return cmd_extract(args)
    elif args.command == 'detect':
        return cmd_detect(args)
    elif args.command == 'scan':
        return cmd_scan(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main()) 