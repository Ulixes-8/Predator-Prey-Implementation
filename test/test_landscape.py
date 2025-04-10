#!/usr/bin/env python3
"""
test_landscape.py

Tests for landscape-specific parameters in predator-prey simulation refactoring.
These tests verify that land proportions and smoothing passes produce identical 
results across different implementations.

Author: s2659865
Date: April 2025
"""

import os
import pytest
from typing import Tuple

# Import from utility modules
from test_utilities import (
    ANIMALS_DIR, 
    load_refactored_implementation,
    run_output_comparison,
    original_sim
)

# ─── Landscape Parameter Tests ─────────────────────────────────────────────────
@pytest.mark.parametrize("refactor_name", ["simulate_predator_prey", "refactor_1", "refactor_2", "refactor_3"])
class TestLandscapeVariations:
    """
    Tests for different landscape parameters.
    
    These tests verify that refactored implementations handle land proportions
    and smoothing passes identically to the original implementation.
    """
    
    @pytest.mark.parametrize("land_prop", [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0])
    def test_land_proportions(self, refactor_name: str, land_prop: float) -> None:
        """
        Test a range of land proportions.
        
        Args:
            refactor_name: Name of the refactored implementation module
            land_prop: Land proportion value to test
        """
        if refactor_name.startswith("refactor_"):
            refactor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                        "performance_experiment", f"{refactor_name}.py")
            if not os.path.exists(refactor_path):
                pytest.skip(f"Refactored implementation {refactor_name} not found")
            
        try:
            refactored_sim = load_refactored_implementation(refactor_name)
        except ImportError as e:
            pytest.skip(f"Could not load {refactor_name}: {str(e)}")
        
        # Create args with the specified land proportion
        args = (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 30,
               os.path.join(ANIMALS_DIR, "3x3.dat"),
               1, land_prop, 2)
        
        # Run comparison
        results = run_output_comparison(original_sim, refactored_sim, args)
        
        # Check results
        assert results["all_match"], (
            f"{refactor_name} produces different output with land proportion {land_prop}")
    
    @pytest.mark.parametrize("smoothing", [0, 1, 3, 5, 10])
    def test_smoothing_passes(self, refactor_name: str, smoothing: int) -> None:
        """
        Test a range of smoothing pass values.
        
        Args:
            refactor_name: Name of the refactored implementation module
            smoothing: Number of landscape smoothing passes to test
        """
        if refactor_name.startswith("refactor_"):
            refactor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                        "performance_experiment", f"{refactor_name}.py")
            if not os.path.exists(refactor_path):
                pytest.skip(f"Refactored implementation {refactor_name} not found")
            
        try:
            refactored_sim = load_refactored_implementation(refactor_name)
        except ImportError as e:
            pytest.skip(f"Could not load {refactor_name}: {str(e)}")
        
        # Create args with the specified smoothing passes
        args = (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 30,
               os.path.join(ANIMALS_DIR, "3x3.dat"),
               1, 0.75, smoothing)
        
        # Run comparison
        results = run_output_comparison(original_sim, refactored_sim, args)
        
        # Check results
        assert results["all_match"], (
            f"{refactor_name} produces different output with {smoothing} smoothing passes")