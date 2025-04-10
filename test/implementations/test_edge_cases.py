#!/usr/bin/env python3
"""
test_edge_cases.py

Tests for edge cases and extreme parameters in predator-prey simulation refactoring.
These tests verify that refactored implementations handle unusual or extreme
parameter combinations identically to the original implementation.

Author: s2659865
Date: April 2025
"""

import os
import sys
import pytest
from typing import Tuple, Any, List

# Add the project root to the path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import from utility modules
from test.utils.test_utilities import (
    ANIMALS_DIR, 
    load_refactored_implementation,
    run_output_comparison,
    original_sim,
    get_file_hash,
    temporary_directory,
    captured_output
)

# ─── Random Seed Tests ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("refactor_name", ["simulate_predator_prey", "refactor_1", "refactor_2", "refactor_3"])
class TestEdgeCases:
    """
    Tests for edge cases and stress testing.
    
    These tests verify that refactored implementations handle a variety of
    random seeds and edge cases identically to the original implementation.
    """
    
    @pytest.mark.parametrize("seed", [1, 42, 123, 456, 789, 999])
    def test_random_seeds(self, refactor_name: str, seed: int) -> None:
        """
        Test with multiple random seeds.
        
        Args:
            refactor_name: Name of the refactored implementation module
            seed: Random seed value to test
        """
        if refactor_name.startswith("refactor_"):
            refactor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                        "performance_experiment", "implementations", f"{refactor_name}.py")
            if not os.path.exists(refactor_path):
                pytest.skip(f"Refactored implementation {refactor_name} not found at {refactor_path}")
            
        try:
            refactored_sim = load_refactored_implementation(refactor_name)
        except ImportError as e:
            pytest.skip(f"Could not load {refactor_name}: {str(e)}")
        
        # Create args with the specified seed
        args = (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 30,
               os.path.join(ANIMALS_DIR, "3x3.dat"),
               seed, 0.75, 2)
        
        # Run comparison
        results = run_output_comparison(original_sim, refactored_sim, args)
        
        # Check results
        assert results["all_match"], f"{refactor_name} produces different output with seed {seed}"


# ─── Extreme Parameter Tests ─────────────────────────────────────────────────
# Define parameter variations for extreme cases directly in this file
extreme_parameters = [
    ("explosive_growth", (0.5, 0.01, 0.2, 0.5, 0.01, 0.2, 0.5, 10, 30, "3x3.dat", 1, 0.75, 2)),
    ("population_crash", (0.01, 0.5, 0.2, 0.01, 0.5, 0.2, 0.5, 10, 30, "3x3.dat", 1, 0.75, 2)),
    ("rapid_diffusion", (0.1, 0.05, 0.9, 0.03, 0.09, 0.9, 0.5, 10, 30, "3x3.dat", 1, 0.75, 2)),
    ("tiny_timestep", (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.01, 10, 30, "3x3.dat", 1, 0.75, 2)),
    ("sparse_landscape", (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 30, "performance_experiment_20x20.dat", 1, 0.1, 2))
]

@pytest.mark.parametrize("refactor_name", ["simulate_predator_prey", "refactor_1", "refactor_2", "refactor_3"])
@pytest.mark.parametrize("test_case,args", extreme_parameters)
class TestExtremeParameters:
    """
    Tests for extreme parameter combinations.
    
    These tests verify that refactored implementations handle extreme parameter
    combinations identically to the original implementation.
    """
    
    def test_extreme_cases(self, refactor_name: str, test_case: str, args: Tuple[Any, ...]) -> None:
        """
        Test extreme parameter combinations.
        
        Args:
            refactor_name: Name of the refactored implementation module
            test_case: Name of the test case for identification
            args: Tuple of simulation parameters
        """
        if refactor_name.startswith("refactor_"):
            refactor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                        "performance_experiment", "implementations", f"{refactor_name}.py")
            if not os.path.exists(refactor_path):
                pytest.skip(f"Refactored implementation {refactor_name} not found at {refactor_path}")
            
        try:
            refactored_sim = load_refactored_implementation(refactor_name)
        except ImportError as e:
            pytest.skip(f"Could not load {refactor_name}: {str(e)}")
        
        # Convert animal file path
        args_list = list(args)
        args_list[9] = os.path.join(ANIMALS_DIR, args_list[9])
        updated_args = tuple(args_list)
        
        # Run comparison
        results = run_output_comparison(original_sim, refactored_sim, updated_args)
        
        # Check results
        assert results["all_match"], (
            f"{refactor_name} produces different output for extreme case {test_case}")


# ─── Determinism Tests ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("refactor_name", ["simulate_predator_prey", "refactor_1", "refactor_2", "refactor_3"])
class TestDeterminism:
    """
    Tests for simulation determinism.
    
    These tests verify that the simulation produces identical outputs when
    run multiple times with the same parameters and random seed.
    """
    
    def test_determinism(self, refactor_name: str) -> None:
        """
        Test determinism with the same inputs.
        
        Args:
            refactor_name: Name of the refactored implementation module
        """
        if refactor_name.startswith("refactor_"):
            refactor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                        "performance_experiment", "implementations", f"{refactor_name}.py")
            if not os.path.exists(refactor_path):
                pytest.skip(f"Refactored implementation {refactor_name} not found at {refactor_path}")
            
        try:
            refactored_sim = load_refactored_implementation(refactor_name)
        except ImportError as e:
            pytest.skip(f"Could not load {refactor_name}: {str(e)}")
        
        # Simple test case
        test_args = (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 30,
                     os.path.join(ANIMALS_DIR, "3x3.dat"),
                     1, 0.75, 2)
        
        # Run the original simulation once
        with temporary_directory() as dir1:
            with captured_output():
                original_sim(*test_args)
            
            # Save the CSV hash
            original_csv_hash = get_file_hash(os.path.join(dir1, "averages.csv"))
            
            # Run the refactored simulation twice
            with temporary_directory() as dir2:
                with captured_output():
                    refactored_sim(*test_args)
                
                refactored_csv_hash1 = get_file_hash(os.path.join(dir2, "averages.csv"))
                
                with temporary_directory() as dir3:
                    with captured_output():
                        refactored_sim(*test_args)
                    
                    refactored_csv_hash2 = get_file_hash(os.path.join(dir3, "averages.csv"))
        
        # All hashes should match, confirming determinism
        assert original_csv_hash == refactored_csv_hash1, (
            f"{refactor_name} doesn't match original simulation")
        
        assert refactored_csv_hash1 == refactored_csv_hash2, (
            f"{refactor_name} is not deterministic with the same inputs")