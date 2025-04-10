#!/usr/bin/env python3
"""
test_parameters.py

Tests for verifying that refactored predator-prey simulations
produce identical outputs across different parameter variations.

Author: s2659865
Date: April 2025
"""

import os
import sys
import pytest
from typing import Tuple, Any

# Add the project root to the path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import from utility modules
from test.utils.test_utilities import (
    ANIMALS_DIR, 
    load_refactored_implementation,
    run_output_comparison,
    original_sim
)

# ─── Parameter Variation Tests ────────────────────────────────────────────────
# Define parameter variations directly in this file, as in the original
all_parameter_variations = [
    ("small_basic", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("medium_grid", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "performance_experiment_40x40.dat", 1, 0.75, 2),
    ("large_grid", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "performance_experiment_80x80.dat", 1, 0.75, 2),
    ("high_birth", 0.2, 0.05, 0.2, 0.1, 0.09, 0.2, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("zero_birth", 0.0, 0.05, 0.2, 0.0, 0.09, 0.2, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("high_predation", 0.1, 0.2, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("high_diffusion", 0.1, 0.05, 0.5, 0.03, 0.09, 0.5, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("zero_diffusion", 0.1, 0.05, 0.0, 0.03, 0.09, 0.0, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("small_timestep", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.1, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("large_timestep", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 1.0, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("frequent_output", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 5, 50, "3x3.dat", 1, 0.75, 2),
    ("single_cell", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "1x1.dat", 1, 0.75, 2),
    ("only_mice", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "1x1prey.dat", 1, 0.75, 2),
    ("only_foxes", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "1x1pred.dat", 1, 0.75, 2),
    ("logo_pattern", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "40x20ps.dat", 1, 0.75, 2),
]

@pytest.mark.parametrize("refactor_name", ["simulate_predator_prey", "refactor_1", "refactor_2", "refactor_3"])
@pytest.mark.parametrize("test_case", all_parameter_variations)
class TestParameterVariations:
    """
    Tests for different parameter variations.
    
    These tests verify that the refactored implementations produce identical outputs
    to the original implementation across a wide range of parameter combinations.
    """
    
    def test_parameter_equivalence(self, refactor_name: str, test_case: Tuple[Any, ...]) -> None:
        """
        Test that refactored implementations produce identical outputs with various parameters.
        
        Args:
            refactor_name: Name of the refactored implementation module
            test_case: Tuple containing (test_name, param1, param2, ...)
        """
        if refactor_name.startswith("refactor_"):
            refactor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                        "performance_experiment", "implementations", f"{refactor_name}.py")
            if not os.path.exists(refactor_path):
                pytest.skip(f"Refactored implementation {refactor_name} not found at {refactor_path}")
        
        name = test_case[0]
        params = list(test_case[1:])
        
        # Convert animal file path
        params[9] = os.path.join(ANIMALS_DIR, params[9])
        
        try:
            refactored_sim = load_refactored_implementation(refactor_name)
        except ImportError as e:
            pytest.skip(f"Could not load {refactor_name}: {str(e)}")
        
        # Run the comparison
        results = run_output_comparison(original_sim, refactored_sim, tuple(params))
        
        # Check results
        assert results["stdout_match"], f"{refactor_name} produces different stdout for {name}"
        assert results["csv_match"], f"{refactor_name} produces different CSV output for {name}"
        assert results["ppm_match"], f"{refactor_name} produces different PPM output for {name}"