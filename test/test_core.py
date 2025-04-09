#!/usr/bin/env python3
"""
test_core.py

Core tests for predator-prey simulation refactoring.
These tests verify that basic interfaces and functionality remain consistent
across all refactored implementations.

Author: s2659865
Date: April 2025
"""

import os
import sys
import importlib.util
import pytest
from typing import List

# Add the current directory to the path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from utility modules
from test_utilities import PERF_DIR, captured_output, temporary_directory
from test_fixtures import available_refactorings

# ─── Interface Tests ──────────────────────────────────────────────────────────
class TestRefactoringCore:
    """
    Core tests for all refactored implementations.
    
    These tests verify that interfaces, version numbers, and command-line
    functionality remain consistent across all refactored implementations.
    """
    
    def test_version_consistency(self, available_refactorings: List[str]) -> None:
        """
        Test that all implementations report the same version.
        
        Args:
            available_refactorings: List of available refactored implementation modules
        """
        # Import the original version function
        from predator_prey.simulate_predator_prey import getVersion as original_get_version
        
        # Check original version
        assert original_get_version() == 4.0, "Original implementation version mismatch"
        
        # Check each refactored implementation
        for refactor_name in available_refactorings:
            # Import the module
            spec = importlib.util.spec_from_file_location(
                refactor_name, 
                os.path.join(PERF_DIR, f"{refactor_name}.py")
            )
            assert spec is not None, f"Could not create spec for {refactor_name}"
            assert spec.loader is not None, f"Could not create loader for {refactor_name}"
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Test getVersion if it exists
            assert hasattr(module, 'getVersion'), f"{refactor_name} is missing getVersion function"
            assert module.getVersion() == 4.0, f"{refactor_name} reports incorrect version"
    
    def test_cli_existence(self, available_refactorings: List[str]) -> None:
        """
        Test that all implementations maintain the command line interface.
        
        Args:
            available_refactorings: List of available refactored implementation modules
        """
        for refactor_name in available_refactorings:
            # Import the module
            spec = importlib.util.spec_from_file_location(
                refactor_name, 
                os.path.join(PERF_DIR, f"{refactor_name}.py")
            )
            assert spec is not None, f"Could not create spec for {refactor_name}"
            assert spec.loader is not None, f"Could not create loader for {refactor_name}"
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Test simCommLineIntf if it exists
            assert hasattr(module, 'simCommLineIntf'), f"{refactor_name} is missing simCommLineIntf function"
            assert callable(module.simCommLineIntf), f"{refactor_name} has non-callable simCommLineIntf"


# ─── Basic Implementation Tests ────────────────────────────────────────────────
@pytest.mark.parametrize("refactor_name", ["refactor_1", "refactor_2", "refactor_3"])
class TestRefactoringImplementation:
    """
    Tests for individual refactored implementations.
    
    These tests verify that each refactored implementation can be loaded
    and executed without errors.
    """
    
    def test_implementation_exists(self, refactor_name: str) -> None:
        """
        Test that the refactored implementation exists.
        
        Args:
            refactor_name: Name of the refactored implementation module
        """
        refactor_path = os.path.join(PERF_DIR, f"{refactor_name}.py")
        if not os.path.exists(refactor_path):
            pytest.skip(f"Refactored implementation {refactor_name} not found")
    
    def test_implementation_loadable(self, refactor_name: str) -> None:
        """
        Test that the refactored implementation can be loaded.
        
        Args:
            refactor_name: Name of the refactored implementation module
        """
        try:
            # Import test utility functions
            from test_utilities import load_refactored_implementation
            
            # Try to load the refactored implementation
            refactored_sim = load_refactored_implementation(refactor_name)
            assert callable(refactored_sim), f"{refactor_name}.sim is not callable"
        except ImportError as e:
            pytest.skip(f"Could not load {refactor_name}: {str(e)}")
    
    def test_basic_execution(self, refactor_name: str) -> None:
        """
        Test basic execution without errors.
        
        Args:
            refactor_name: Name of the refactored implementation module
        """
        try:
            # Import test utility functions
            from test_utilities import load_refactored_implementation, ANIMALS_DIR
            
            # Try to load the refactored implementation
            refactored_sim = load_refactored_implementation(refactor_name)
        except ImportError:
            pytest.skip(f"Could not load {refactor_name}")
        
        # Use a simple test case
        args = (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50,
                os.path.join(ANIMALS_DIR, "3x3.dat"), 
                1, 0.75, 2)
        
        with temporary_directory():
            with captured_output():
                # This should not raise an exception
                refactored_sim(*args)