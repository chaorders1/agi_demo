Here are the CLI commands you can use to test the watermark tools:

  1. Adding Watermarks

  # Basic usage - add watermark to an image
  python3 watermark.py add asset/AGI_vide_coding.png output.png --text "Hello World"

  # Add watermark with specific method (dwtDct is default and recommended)
  python3 watermark.py add asset/AGI_vide_coding.png output.png --text "Copyright 2025" --method dwtDct

  # Try rivaGan method (will fail - requires models)
  python3 watermark.py add asset/AGI_vide_coding.png output.png --text "Test" --method rivaGan

  2. Extracting Watermarks

  # Extract watermark (you need to know the exact length)
  python3 watermark.py extract output.png --length 11

  # Extract with specific method
  python3 watermark.py extract output.png --length 11 --method dwtDct

  3. Detecting Watermarks

  # Basic detection (outputs: yes or no)
  python3 detect_watermark.py output.png

  # Detection with confidence level
  python3 detect_watermark.py output.png --confidence

  # Check original image (may show false positive due to DCT sensitivity)
  python3 detect_watermark.py asset/AGI_vide_coding.png --confidence

  # Try different detection method
  python3 detect_watermark.py output.png --method rivaGan --confidence

  4. Help Commands

  # Get help for main commands
  python3 watermark.py --help
  python3 watermark.py add --help
  python3 watermark.py extract --help
  python3 detect_watermark.py --help

  5. Quick Test Sequence

  # 1. Add a watermark
  python3 watermark.py add asset/AGI_vide_coding.png test_image.png --text "Secret123"

  # 2. Detect if watermark exists
  python3 detect_watermark.py test_image.png --confidence

  # 3. Extract the watermark (length = 9 for "Secret123")
  python3 watermark.py extract test_image.png --length 9

  # 4. Clean up
  rm test_image.png

  6. Run Test Suites

  # Run comprehensive test suite
  python3 test_all.py

  # Run quick verification tests
  python3 test_final.py

  Note: The extraction may not return the exact text due to library limitations, but the detection tool will indicate
  if a watermark is present.