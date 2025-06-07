# Invisible Watermark Tool

A Python script that adds invisible watermarks to images using the invisible-watermark library from https://github.com/ShieldMnt/invisible-watermark

## Installation

### Option 1: Using install script
```bash
chmod +x install.sh
./install.sh
```

### Option 2: Manual installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install invisible-watermark from GitHub
pip install git+https://github.com/ShieldMnt/invisible-watermark.git
```

## Scripts

### 1. watermark.py - Add/Extract Watermarks

#### Adding a watermark

```bash
python3 watermark.py add <input_image> <output_image> --text "Your watermark text"
```

Example:
```bash
python3 watermark.py add photo.jpg watermarked_photo.jpg --text "Copyright 2025"
```

#### Extracting a watermark

```bash
python3 watermark.py extract <watermarked_image> --length <text_length>
```

Example:
```bash
python3 watermark.py extract watermarked_photo.jpg --length 14
```

### 2. detect_watermark.py - Detect Watermarks

```bash
python3 detect_watermark.py <image_file>
```

With confidence level:
```bash
python3 detect_watermark.py <image_file> --confidence
```

Output: "yes" or "no" (with optional confidence percentage)

### Options

- `--method`: Choose watermarking method ('dwtDct' or 'rivaGan'). Default is 'dwtDct'
  - Note: 'rivaGan' requires pre-trained models and is not available by default
- `--confidence`: Show confidence level for detection

## Important Notes

- The watermark is invisible and doesn't affect the visual appearance of the image
- You need to know the exact length of the watermark text to extract it
- The 'dwtDct' method is fastest and most robust (recommended)
- **rivaGan limitations**: 
  - Only supports 4-byte watermarks
  - Requires pre-trained models that are not included
- **Detection Limitations**: The library may not preserve watermark content perfectly, making detection challenging. The detection tool uses statistical analysis but may have false positives/negatives.
- The watermarks are not robust to image resizing or significant cropping