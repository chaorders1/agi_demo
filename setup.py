#!/usr/bin/env python
"""
Setup script for the invisible watermark library
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="invisible-watermark-agi",
    version="1.0.0",
    author="AGI Demo Team",
    author_email="team@agi-demo.com",
    description="A powerful Python library for adding and detecting invisible watermarks in images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agi-demo/invisible-watermark",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "watermark=watermark.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="watermark, image processing, security, steganography, invisible watermark",
    project_urls={
        "Bug Reports": "https://github.com/agi-demo/invisible-watermark/issues",
        "Source": "https://github.com/agi-demo/invisible-watermark",
        "Documentation": "https://github.com/agi-demo/invisible-watermark/blob/main/docs/",
    },
) 