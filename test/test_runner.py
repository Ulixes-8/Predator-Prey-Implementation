#!/usr/bin/env python3
"""
test_runner.py

Main script to run all predator-prey refactoring tests.
This script provides a convenient entry point to execute all tests
with appropriate configuration and reporting.

Author: s2659865
Date: April 2025
"""

import os
import sys
import pytest
from typing import List

# Add the project root to the path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests() -> int:
    """
    Run all predator-prey refactoring tests.
    
    Returns:
        Exit code from pytest (0 for success, non-zero for failure)
    """
    # Define arguments for pytest
    pytest_args: List[str] = [
        # Discover tests in the current directory
        os.path.dirname(os.path.abspath(__file__)),
        
        # Verbose output
        "-v",
        
        # Generate reports
        "--junitxml=test-results.xml",
        
        # Output to console
        "-s",
        
        # Show local variables in tracebacks
        "--showlocals",
        
        # Color output
        "--color=yes"
    ]
    
    # Add any arguments from command line
    pytest_args.extend(sys.argv[1:])
    
    # Run pytest with these arguments
    return pytest.main(pytest_args)

if __name__ == "__main__":
    print("=" * 80)
    print("Running predator-prey simulation refactoring tests")
    print("=" * 80)
    
    # Exit with the same code as pytest
    sys.exit(run_tests())