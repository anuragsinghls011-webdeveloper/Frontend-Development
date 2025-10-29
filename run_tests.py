#!/usr/bin/env python3
"""
Test runner script for KMRL DMS testing.
This script runs all tests and generates comprehensive reports.
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def run_tests():
    """Run all tests and generate reports."""
    print("🚀 Starting KMRL DMS Test Suite")
    print("=" * 50)
    
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Test categories
    test_categories = [
        ("API Tests", "tests/test_api.py"),
        ("Authentication Tests", "tests/test_auth.py"),
        ("Dashboard Tests", "tests/test_dashboard.py"),
        ("File Upload Tests", "tests/test_file_upload.py"),
        ("Integration Tests", "tests/test_integration.py")
    ]
    
    total_passed = 0
    total_failed = 0
    
    for category, test_file in test_categories:
        print(f"\n📋 Running {category}...")
        print("-" * 30)
        
        try:
            # Run pytest for this specific test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file,
                "-v",
                "--tb=short",
                "--html=reports/{}.html".format(category.lower().replace(" ", "_")),
                "--self-contained-html"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {category} PASSED")
                total_passed += 1
            else:
                print(f"❌ {category} FAILED")
                print(result.stdout)
                print(result.stderr)
                total_failed += 1
                
        except Exception as e:
            print(f"❌ Error running {category}: {e}")
            total_failed += 1
    
    # Run all tests together for comprehensive report
    print(f"\n📊 Running All Tests Together...")
    print("-" * 30)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--html=reports/comprehensive_test_report.html",
            "--self-contained-html",
            "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All Tests PASSED")
        else:
            print("❌ Some Tests FAILED")
            print(result.stdout)
            
    except Exception as e:
        print(f"❌ Error running comprehensive tests: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📈 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Categories Passed: {total_passed}")
    print(f"❌ Categories Failed: {total_failed}")
    print(f"📁 Reports saved in: {reports_dir.absolute()}")
    
    if total_failed == 0:
        print("\n🎉 All tests passed! Your KMRL DMS is working perfectly!")
        return 0
    else:
        print(f"\n⚠️  {total_failed} test categories failed. Check the reports for details.")
        return 1

def run_specific_tests(test_pattern):
    """Run specific tests based on pattern."""
    print(f"🎯 Running tests matching: {test_pattern}")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            f"tests/{test_pattern}",
            "-v",
            "--html=reports/specific_test_report.html",
            "--self-contained-html"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running specific tests: {e}")
        return 1

def run_quick_tests():
    """Run quick tests (excluding slow integration tests)."""
    print("⚡ Running Quick Tests (excluding slow tests)")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/test_api.py",
            "tests/test_auth.py",
            "-v",
            "--html=reports/quick_test_report.html",
            "--self-contained-html"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running quick tests: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            exit_code = run_quick_tests()
        elif sys.argv[1] == "specific":
            if len(sys.argv) > 2:
                exit_code = run_specific_tests(sys.argv[2])
            else:
                print("Usage: python run_tests.py specific <test_pattern>")
                exit_code = 1
        else:
            print("Usage: python run_tests.py [quick|specific <pattern>]")
            exit_code = 1
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)
