"""
Invisible Watermark Library
A Python library for adding and detecting invisible watermarks in images.
"""

from .core import add_watermark, extract_watermark
from .detector import detect_watermark

__version__ = "1.0.0"
__author__ = "AGI Demo Team"
__email__ = "team@agi-demo.com"

__all__ = [
    "add_watermark",
    "extract_watermark", 
    "detect_watermark",
] 