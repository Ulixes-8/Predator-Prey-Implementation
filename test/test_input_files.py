#!/usr/bin/env python3
"""
test_input_files.py

Tests for different input files in predator-prey simulation refactoring.
These tests verify that refactored implementations process all available
animal density files identically to the original implementation.

Author: s2659865
Date: April 2025
"""

import os
import sys
import pytest
from typing import List

# Add the current directory to the path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from utility modules
from test_utilities import (
    load_refactored_implementation,
    run_output_comparison,
    original_sim
)

# ─── Input File Tests ─────────────────────────────────────────────────────────
class TestInputFiles:
    """
    Tests for different input files.
    
    These tests verify that refactored implementations process all available
    animal data files identically to the original implementation.
    """
    
    def test_all_animal_files(self, available_refactorings: List[str], all_animal_files: List[str]) -> None:
        """
        Test all available animal files with default parameters.
        
        Args:
            available_refactorings: List of available refactored implementation modules
            all_animal_files: List of all animal density file paths
        """
        if not available_refactorings:
            pytest.skip("No refactored implementations available")
        
        # Pick the first available refactored implementation
        refactor_name = available_refactorings[0]
        refactored_sim = load_refactored_implementation(refactor_name)
        
        # Default parameters excluding the animal file
        default_args_prefix = (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 30)
        default_args_suffix = (1, 0.75, 2)
        
        # Test each animal file
        for animal_file in all_animal_files:
            # Skip very large files to keep test duration reasonable
            file_size = os.path.getsize(animal_file)
            if file_size > 10000:  # Skip files larger than ~1000KB
                continue
                
            # Create full args tuple with this animal file
            args = default_args_prefix + (animal_file,) + default_args_suffix
            
            # Run comparison
            print(f"Testing file: {os.path.basename(animal_file)}")
            results = run_output_comparison(original_sim, refactored_sim, args)
            
            # Check results
            file_name = os.path.basename(animal_file)
            assert results["stdout_match"], f"Different stdout for {file_name}"
            assert results["csv_match"], f"Different CSV output for {file_name}"
            assert results["ppm_match"], f"Different PPM output for {file_name}"