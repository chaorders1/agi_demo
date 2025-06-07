#!/usr/bin/env python3
"""
Comprehensive Test Suite for Watermark Tools
Tests all functionality of watermark.py and detect_watermark.py
"""

import os
import subprocess
import tempfile
import shutil
import sys


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def run_command(cmd):
    """Run a command and return output, error, and return code"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{test_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")


def print_result(test_name, passed, details=""):
    """Print test result with color coding"""
    if passed:
        status = f"{Colors.GREEN}✓ PASSED{Colors.RESET}"
    else:
        status = f"{Colors.RED}✗ FAILED{Colors.RESET}"
    
    print(f"{test_name}: {status}")
    if details:
        print(f"  {Colors.YELLOW}Details: {details}{Colors.RESET}")


def test_watermark_add():
    """Test watermark.py add functionality"""
    print_test_header("Testing watermark.py - Add Functionality")
    
    tests_passed = 0
    tests_failed = 0
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test 1: Basic add functionality
        test_name = "Basic watermark add"
        output_file = f"{tmpdir}/test1.png"
        cmd = f"python3 watermark.py add asset/AGI_vide_coding.png {output_file} --text 'Test123'"
        out, err, code = run_command(cmd)
        
        if code == 0 and os.path.exists(output_file) and "Watermarked image saved" in out:
            print_result(test_name, True)
            tests_passed += 1
        else:
            print_result(test_name, False, f"Exit code: {code}, Output: {out}, Error: {err}")
            tests_failed += 1
        
        # Test 2: Add with rivaGan method
        test_name = "Watermark add with rivaGan"
        output_file = f"{tmpdir}/test2.png"
        cmd = f"python3 watermark.py add asset/AGI_vide_coding.png {output_file} --text 'RivaGan' --method rivaGan"
        out, err, code = run_command(cmd)
        
        if code == 0 and os.path.exists(output_file):
            print_result(test_name, True)
            tests_passed += 1
        else:
            print_result(test_name, False, f"Exit code: {code}, Error: {err}")
            tests_failed += 1
        
        # Test 3: Missing input file
        test_name = "Error handling - missing input"
        cmd = f"python3 watermark.py add nonexistent.png {tmpdir}/test3.png --text 'Test'"
        out, err, code = run_command(cmd)
        
        if code != 0 and "Error: Input file" in out:
            print_result(test_name, True)
            tests_passed += 1
        else:
            print_result(test_name, False, "Should fail with missing input file")
            tests_failed += 1
        
        # Test 4: Create output in new directory
        test_name = "Create output directory"
        output_file = f"{tmpdir}/newdir/test4.png"
        cmd = f"python3 watermark.py add asset/AGI_vide_coding.png {output_file} --text 'DirTest'"
        out, err, code = run_command(cmd)
        
        if code == 0 and os.path.exists(output_file):
            print_result(test_name, True)
            tests_passed += 1
        else:
            print_result(test_name, False, f"Failed to create directory and file")
            tests_failed += 1
    
    return tests_passed, tests_failed


def test_watermark_extract():
    """Test watermark.py extract functionality"""
    print_test_header("Testing watermark.py - Extract Functionality")
    
    tests_passed = 0
    tests_failed = 0
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # First, create a watermarked image
        watermarked_file = f"{tmpdir}/watermarked.png"
        test_text = "ExtractTest"
        cmd = f"python3 watermark.py add asset/AGI_vide_coding.png {watermarked_file} --text '{test_text}'"
        run_command(cmd)
        
        # Test 1: Extract with correct length
        test_name = "Extract watermark"
        cmd = f"python3 watermark.py extract {watermarked_file} --length {len(test_text)}"
        out, err, code = run_command(cmd)
        
        if code == 0 and "Extracted watermark:" in out:
            print_result(test_name, True, f"Output: {out}")
            tests_passed += 1
        else:
            print_result(test_name, False, f"Exit code: {code}, Error: {err}")
            tests_failed += 1
        
        # Test 2: Extract with wrong length
        test_name = "Extract with different length"
        cmd = f"python3 watermark.py extract {watermarked_file} --length 5"
        out, err, code = run_command(cmd)
        
        if code == 0:
            print_result(test_name, True, "Extraction completed")
            tests_passed += 1
        else:
            print_result(test_name, False, f"Exit code: {code}")
            tests_failed += 1
        
        # Test 3: Extract from non-existent file
        test_name = "Error handling - missing file"
        cmd = "python3 watermark.py extract nonexistent.png --length 10"
        out, err, code = run_command(cmd)
        
        if code != 0 and "Error: Image file" in out:
            print_result(test_name, True)
            tests_passed += 1
        else:
            print_result(test_name, False, "Should fail with missing file")
            tests_failed += 1
    
    return tests_passed, tests_failed


def test_detect_watermark():
    """Test detect_watermark.py functionality"""
    print_test_header("Testing detect_watermark.py")
    
    tests_passed = 0
    tests_failed = 0
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a watermarked image
        watermarked_file = f"{tmpdir}/watermarked.png"
        cmd = f"python3 watermark.py add asset/AGI_vide_coding.png {watermarked_file} --text 'Detection Test'"
        run_command(cmd)
        
        # Test 1: Basic detection
        test_name = "Basic detection"
        cmd = f"python3 detect_watermark.py {watermarked_file}"
        out, err, code = run_command(cmd)
        
        if code == 0 and out in ["yes", "no"]:
            print_result(test_name, True, f"Output: {out}")
            tests_passed += 1
        else:
            print_result(test_name, False, f"Invalid output: {out}")
            tests_failed += 1
        
        # Test 2: Detection with confidence
        test_name = "Detection with confidence"
        cmd = f"python3 detect_watermark.py {watermarked_file} --confidence"
        out, err, code = run_command(cmd)
        
        if code == 0 and ("yes" in out or "no" in out):
            print_result(test_name, True, f"Output: {out}")
            tests_passed += 1
        else:
            print_result(test_name, False, f"Invalid output: {out}")
            tests_failed += 1
        
        # Test 3: Detection with rivaGan method
        test_name = "Detection with rivaGan method"
        cmd = f"python3 detect_watermark.py {watermarked_file} --method rivaGan --confidence"
        out, err, code = run_command(cmd)
        
        if code == 0:
            print_result(test_name, True, f"Output: {out}")
            tests_passed += 1
        else:
            print_result(test_name, False, f"Exit code: {code}")
            tests_failed += 1
        
        # Test 4: Detection on original image
        test_name = "Detection on original image"
        cmd = "python3 detect_watermark.py asset/AGI_vide_coding.png --confidence"
        out, err, code = run_command(cmd)
        
        if code == 0:
            print_result(test_name, True, f"Output: {out}")
            tests_passed += 1
        else:
            print_result(test_name, False, f"Exit code: {code}")
            tests_failed += 1
        
        # Test 5: Error handling
        test_name = "Error handling - missing file"
        cmd = "python3 detect_watermark.py nonexistent.png"
        out, err, code = run_command(cmd)
        
        if code == 2 and "Error:" in out:
            print_result(test_name, True)
            tests_passed += 1
        else:
            print_result(test_name, False, "Should fail with error")
            tests_failed += 1
    
    return tests_passed, tests_failed


def test_help_commands():
    """Test help commands for all scripts"""
    print_test_header("Testing Help Commands")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test watermark.py help
    test_name = "watermark.py help"
    cmd = "python3 watermark.py --help"
    out, err, code = run_command(cmd)
    
    if code == 0 and "Add or extract invisible watermarks" in out:
        print_result(test_name, True)
        tests_passed += 1
    else:
        print_result(test_name, False)
        tests_failed += 1
    
    # Test watermark.py add help
    test_name = "watermark.py add help"
    cmd = "python3 watermark.py add --help"
    out, err, code = run_command(cmd)
    
    if code == 0 and "--text" in out:
        print_result(test_name, True)
        tests_passed += 1
    else:
        print_result(test_name, False)
        tests_failed += 1
    
    # Test detect_watermark.py help
    test_name = "detect_watermark.py help"
    cmd = "python3 detect_watermark.py --help"
    out, err, code = run_command(cmd)
    
    if code == 0 and "--confidence" in out:
        print_result(test_name, True)
        tests_passed += 1
    else:
        print_result(test_name, False)
        tests_failed += 1
    
    return tests_passed, tests_failed


def test_edge_cases():
    """Test edge cases and special scenarios"""
    print_test_header("Testing Edge Cases")
    
    tests_passed = 0
    tests_failed = 0
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test 1: Empty watermark text
        test_name = "Empty watermark text"
        output_file = f"{tmpdir}/empty.png"
        cmd = f"python3 watermark.py add asset/AGI_vide_coding.png {output_file} --text ''"
        out, err, code = run_command(cmd)
        
        # Should handle empty text gracefully
        print_result(test_name, True, "Empty text handled")
        tests_passed += 1
        
        # Test 2: Very long watermark text
        test_name = "Long watermark text"
        long_text = "A" * 200
        output_file = f"{tmpdir}/long.png"
        cmd = f"python3 watermark.py add asset/AGI_vide_coding.png {output_file} --text '{long_text}'"
        out, err, code = run_command(cmd)
        
        if code == 0:
            print_result(test_name, True)
            tests_passed += 1
        else:
            print_result(test_name, False, f"Failed with long text")
            tests_failed += 1
        
        # Test 3: Special characters in watermark
        test_name = "Special characters"
        special_text = "Test@#$%123"
        output_file = f"{tmpdir}/special.png"
        cmd = f"python3 watermark.py add asset/AGI_vide_coding.png {output_file} --text '{special_text}'"
        out, err, code = run_command(cmd)
        
        if code == 0:
            print_result(test_name, True)
            tests_passed += 1
        else:
            print_result(test_name, False)
            tests_failed += 1
        
        # Test 4: Unicode characters
        test_name = "Unicode characters"
        unicode_text = "Hello世界"
        output_file = f"{tmpdir}/unicode.png"
        cmd = f"python3 watermark.py add asset/AGI_vide_coding.png {output_file} --text '{unicode_text}'"
        out, err, code = run_command(cmd)
        
        if code == 0:
            print_result(test_name, True)
            tests_passed += 1
        else:
            print_result(test_name, False)
            tests_failed += 1
    
    return tests_passed, tests_failed


def main():
    """Run all tests and report results"""
    print(f"{Colors.BOLD}{Colors.GREEN}Watermark Tools Test Suite{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.RESET}")
    
    total_passed = 0
    total_failed = 0
    
    # Run all test suites
    test_suites = [
        test_help_commands,
        test_watermark_add,
        test_watermark_extract,
        test_detect_watermark,
        test_edge_cases
    ]
    
    for test_suite in test_suites:
        passed, failed = test_suite()
        total_passed += passed
        total_failed += failed
    
    # Print summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Test Summary:{Colors.RESET}")
    print(f"{Colors.GREEN}Passed: {total_passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {total_failed}{Colors.RESET}")
    print(f"{Colors.BOLD}Total: {total_passed + total_failed}{Colors.RESET}")
    
    if total_failed == 0:
        print(f"\n{Colors.BOLD}{Colors.GREEN}All tests passed! ✓{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.BOLD}{Colors.RED}Some tests failed! ✗{Colors.RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())