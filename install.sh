#!/bin/bash
# Installation script for Invisible Watermark Tools

echo "Installing Invisible Watermark Tools..."
echo "======================================"

# Install basic requirements
echo "Installing basic dependencies..."
pip install -r requirements.txt

# Install invisible-watermark from GitHub
echo ""
echo "Installing invisible-watermark library from GitHub..."
pip install git+https://github.com/ShieldMnt/invisible-watermark.git

echo ""
echo "Installation complete!"
echo ""
echo "You can now use:"
echo "  - python3 watermark.py --help"
echo "  - python3 detect_watermark.py --help"
echo ""
echo "Quick test:"
echo "  python3 watermark.py add asset/AGI_vide_coding.png test.png --text 'Hello'"