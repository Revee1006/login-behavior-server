#!/usr/bin/env python3
"""
Test Runner for TechStore E-commerce Project
============================================

This script provides a comprehensive test runner for the Selenium WebDriver test suite.
It supports running different types of tests with various configurations.

Usage:
    python run_tests.py [options]

Options:
    --smoke          Run smoke tests only
    --integration    Run integration tests only
    --e2e           Run end-to-end tests only
    --regression    Run regression tests only
    --all           Run all tests (default)
    --browser       Specify browser (chrome, firefox)
    --headless      Run in headless mode
    --parallel      Run tests in parallel
    --coverage      Generate coverage report
    --html          Generate HTML report
    --slow          Include slow tests
    --verbose       Verbose output
    --help          Show this help message

Examples:
    python run_tests.py --smoke --browser chrome
    python run_tests.py --all --headless --parallel
    python run_tests.py --e2e --browser firefox --html
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

def run_command(command, description=""):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(command, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"\nExit Code: {result.returncode}")
    print(f"Duration: {end_time - start_time:.2f} seconds")
    
    if result.stdout:
        print("\nSTDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    return result.returncode == 0

def setup_environment():
    """Setup the testing environment"""
    print("Setting up testing environment...")
    
    # Create necessary directories
    directories = ["screenshots", "reports", "coverage"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Install dependencies if requirements.txt exists
    if Path("requirements.txt").exists():
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("Environment setup complete!")

def run_smoke_tests(browser="chrome", headless=False, parallel=False, html=False):
    """Run smoke tests"""
    command = [
        sys.executable, "-m", "pytest",
        "tests/test_smoke.py",
        "-v",
        f"--browser={browser}"
    ]
    
    if headless:
        command.append("--headless")
    
    if parallel:
        command.extend(["-n", "auto"])
    
    if html:
        command.extend(["--html=reports/smoke_report.html", "--self-contained-html"])
    
    return run_command(command, "Smoke Tests")

def run_integration_tests(browser="chrome", headless=False, parallel=False, html=False):
    """Run integration tests"""
    command = [
        sys.executable, "-m", "pytest",
        "tests/test_integration.py",
        "-v",
        f"--browser={browser}"
    ]
    
    if headless:
        command.append("--headless")
    
    if parallel:
        command.extend(["-n", "auto"])
    
    if html:
        command.extend(["--html=reports/integration_report.html", "--self-contained-html"])
    
    return run_command(command, "Integration Tests")

def run_e2e_tests(browser="chrome", headless=False, parallel=False, html=False):
    """Run end-to-end tests"""
    command = [
        sys.executable, "-m", "pytest",
        "tests/test_e2e.py",
        "-v",
        f"--browser={browser}"
    ]
    
    if headless:
        command.append("--headless")
    
    if parallel:
        command.extend(["-n", "auto"])
    
    if html:
        command.extend(["--html=reports/e2e_report.html", "--self-contained-html"])
    
    return run_command(command, "End-to-End Tests")

def run_regression_tests(browser="chrome", headless=False, parallel=False, html=False):
    """Run regression tests"""
    command = [
        sys.executable, "-m", "pytest",
        "tests/test_regression.py",
        "-v",
        f"--browser={browser}"
    ]
    
    if headless:
        command.append("--headless")
    
    if parallel:
        command.extend(["-n", "auto"])
    
    if html:
        command.extend(["--html=reports/regression_report.html", "--self-contained-html"])
    
    return run_command(command, "Regression Tests")

def run_all_tests(browser="chrome", headless=False, parallel=False, html=False, coverage=False):
    """Run all tests"""
    command = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        f"--browser={browser}"
    ]
    
    if headless:
        command.append("--headless")
    
    if parallel:
        command.extend(["-n", "auto"])
    
    if html:
        command.extend(["--html=reports/all_tests_report.html", "--self-contained-html"])
    
    if coverage:
        command.extend([
            "--cov=shop",
            "--cov=accounts",
            "--cov-report=html:coverage/html",
            "--cov-report=term-missing"
        ])
    
    return run_command(command, "All Tests")

def run_coverage_report():
    """Generate coverage report"""
    command = [
        sys.executable, "-m", "coverage",
        "run", "--source=shop,accounts",
        "-m", "pytest", "tests/"
    ]
    
    success = run_command(command, "Coverage Analysis")
    
    if success:
        # Generate HTML report
        subprocess.run([sys.executable, "-m", "coverage", "html", "-d", "coverage/html"])
        print("\nCoverage report generated in coverage/html/")
    
    return success

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Test Runner for TechStore E-commerce Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests only")
    parser.add_argument("--regression", action="store_true", help="Run regression tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument("--browser", choices=["chrome", "firefox"], default="chrome", help="Browser to use")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--slow", action="store_true", help="Include slow tests")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Determine which tests to run
    if args.smoke:
        success = run_smoke_tests(args.browser, args.headless, args.parallel, args.html)
    elif args.integration:
        success = run_integration_tests(args.browser, args.headless, args.parallel, args.html)
    elif args.e2e:
        success = run_e2e_tests(args.browser, args.headless, args.parallel, args.html)
    elif args.regression:
        success = run_regression_tests(args.browser, args.headless, args.parallel, args.html)
    else:
        # Default to all tests
        success = run_all_tests(args.browser, args.headless, args.parallel, args.html, args.coverage)
    
    # Run coverage if requested
    if args.coverage and not args.smoke and not args.integration and not args.e2e and not args.regression:
        coverage_success = run_coverage_report()
        success = success and coverage_success
    
    # Print summary
    print(f"\n{'='*60}")
    if success:
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed!")
    print(f"{'='*60}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 