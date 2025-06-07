#!/usr/bin/env python3
"""
Final verification test for watermark tools
"""

import subprocess
import tempfile
import os


def run_test(name, command, expected_success=True):
    """Run a test and report result"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    success = (result.returncode == 0) == expected_success
    
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"{name}: {status}")
    
    if not success:
        print(f"  Command: {command}")
        print(f"  Exit code: {result.returncode}")
        print(f"  Output: {result.stdout}")
        print(f"  Error: {result.stderr}")
    
    return success


def main():
    print("Final Verification Tests")
    print("=" * 50)
    
    all_passed = True
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test 1: Add watermark with dwtDct
        test_file = f"{tmpdir}/test1.png"
        cmd = f"python3 watermark.py add asset/AGI_vide_coding.png {test_file} --text 'Final Test'"
        all_passed &= run_test("Add watermark (dwtDct)", cmd)
        
        # Test 2: Extract watermark
        cmd = f"python3 watermark.py extract {test_file} --length 10"
        all_passed &= run_test("Extract watermark", cmd)
        
        # Test 3: Detect watermark
        cmd = f"python3 detect_watermark.py {test_file} --confidence"
        all_passed &= run_test("Detect watermark", cmd)
        
        # Test 4: Test on original (should detect due to DCT sensitivity)
        cmd = "python3 detect_watermark.py asset/AGI_vide_coding.png"
        all_passed &= run_test("Detect on original", cmd)
        
        # Test 5: Error handling - rivaGan
        test_file2 = f"{tmpdir}/test2.png"
        cmd = f"python3 watermark.py add asset/AGI_vide_coding.png {test_file2} --text 'Test' --method rivaGan"
        all_passed &= run_test("rivaGan error handling", cmd, expected_success=False)
        
        # Test 6: Unicode watermark
        test_file3 = f"{tmpdir}/test3.png"
        cmd = f"python3 watermark.py add asset/AGI_vide_coding.png {test_file3} --text '你好世界'"
        all_passed &= run_test("Unicode watermark", cmd)
        
        # Test 7: Empty watermark (should fail)
        test_file4 = f"{tmpdir}/test4.png"
        cmd = f"python3 watermark.py add asset/AGI_vide_coding.png {test_file4} --text ''"
        all_passed &= run_test("Empty watermark error handling", cmd, expected_success=False)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("All tests PASSED! ✓")
        return 0
    else:
        print("Some tests FAILED! ✗")
        return 1


if __name__ == "__main__":
    exit(main())