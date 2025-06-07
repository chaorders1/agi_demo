# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Invisible Watermark Tool** that embeds and detects invisible watermarks in images using the `invisible-watermark` library. The project provides command-line interfaces for watermarking operations with robust testing and security validation.

## Commands

### Installation
```bash
# Install dependencies and invisible-watermark library
./install.sh

# Or manually:
pip install -r requirements.txt
pip install git+https://github.com/ShieldMnt/invisible-watermark.git@main
```

### Running Tests
```bash
# Run comprehensive test suite with colored output
python test_all.py

# Run final verification tests
python test_final.py

# Run security tests for watermark detection
python test_watermark_security.py
```

### Main Operations
```bash
# Add watermark to image
python watermark.py add -i input.png -w "Your watermark text" [-o output.png] [-m dwtDct|rivaGan]

# Extract watermark from image
python watermark.py extract -i watermarked.png -l <watermark_length>

# Detect watermark in image
python detect_watermark.py -i image.png -w "Expected watermark" [-c] [-d]
```

## Architecture Notes

### Core Components
- **watermark.py**: Main watermarking tool with add/extract commands. Uses DWT-DCT method by default (recommended over rivaGan which has 4-byte limit).
- **detect_watermark.py**: Watermark detection with exact content matching. Recently updated to handle watermark length in bits (multiply bytes by 8).
- **test_all.py**: Comprehensive test suite with organized test groups and color-coded output.

### Key Technical Details
- Watermarks are embedded in the frequency domain using DWT-DCT transform
- Detection requires knowing exact watermark length for extraction
- Watermarks are not robust to image resizing or significant cropping
- UTF-8 support including Unicode characters
- Auto-generates output filenames (e.g., `image.png` → `image_watermarked.png`)

### Testing Approach
- Use `test_all.py` for comprehensive testing including edge cases
- Security testing via `test_watermark_security.py` validates watermark integrity against various attack vectors
- Tests include special characters, Unicode, error handling, and boundary conditions