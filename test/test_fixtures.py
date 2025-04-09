#!/usr/bin/env python3
"""
test_fixtures.py

Test fixtures for predator-prey simulation refactoring tests.
This module provides reusable pytest fixtures that are shared across
multiple test modules to maintain consistency and reduce duplication.

Author: s2659865
Date: April 2025
"""

import os
import pytest
from typing import List

# Import path constants from utilities
from test_utilities import ANIMALS_DIR, PERF_DIR

@pytest.fixture
def available_refactorings() -> List[str]:
    """
    Return a list of available refactored implementation module names.
    
    This fixture looks for refactor_1.py, refactor_2.py, etc. files
    in the performance_experiment directory.
    
    Returns:
        List of refactored implementation module names without .py extension
    """
    refactorings = []
    for i in range(1, 4):  # Check refactor_1, refactor_2, refactor_3
        refactor_path = os.path.join(PERF_DIR, f"refactor_{i}.py")
        if os.path.exists(refactor_path):
            refactorings.append(f"refactor_{i}")
    return refactorings


@pytest.fixture
def all_animal_files() -> List[str]:
    """
    Return a list of all animal density files in the animals directory.
    
    These files contain the initial distribution of predators and prey.
    
    Returns:
        List of absolute paths to all .dat files in the animals directory
    """
    files = []
    for filename in os.listdir(ANIMALS_DIR):
        if filename.endswith(".dat"):
            files.append(os.path.join(ANIMALS_DIR, filename))
    return files


# Definition of standard test parameter sets for reuse across test modules
# Each tuple contains a name and the actual parameters for the simulation

# Basic parameter variations for testing
basic_parameters = [
    ("small_basic", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("medium_grid", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "performance_experiment_40x40.dat", 1, 0.75, 2),
    ("large_grid", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "performance_experiment_80x80.dat", 1, 0.75, 2),
]

# Parameter variations focused on birth rates
birth_parameters = [
    ("high_birth", 0.2, 0.05, 0.2, 0.1, 0.09, 0.2, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("zero_birth", 0.0, 0.05, 0.2, 0.0, 0.09, 0.2, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
]

# Parameter variations focused on predation and diffusion
movement_parameters = [
    ("high_predation", 0.1, 0.2, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("high_diffusion", 0.1, 0.05, 0.5, 0.03, 0.09, 0.5, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("zero_diffusion", 0.1, 0.05, 0.0, 0.03, 0.09, 0.0, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
]

# Parameter variations focused on timesteps
timestep_parameters = [
    ("small_timestep", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.1, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("large_timestep", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 1.0, 10, 50, "3x3.dat", 1, 0.75, 2),
    ("frequent_output", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 5, 50, "3x3.dat", 1, 0.75, 2),
]

# Parameter variations focused on grid configuration
grid_parameters = [
    ("single_cell", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "1x1.dat", 1, 0.75, 2),
    ("only_mice", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "1x1prey.dat", 1, 0.75, 2),
    ("only_foxes", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "1x1pred.dat", 1, 0.75, 2),
    ("logo_pattern", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "40x20ps.dat", 1, 0.75, 2),
]

# Parameter variations for extreme cases
extreme_parameters = [
    ("explosive_growth", 0.5, 0.01, 0.2, 0.5, 0.01, 0.2, 0.5, 10, 30, "3x3.dat", 1, 0.75, 2),
    ("population_crash", 0.01, 0.5, 0.2, 0.01, 0.5, 0.2, 0.5, 10, 30, "3x3.dat", 1, 0.75, 2),
    ("rapid_diffusion", 0.1, 0.05, 0.9, 0.03, 0.09, 0.9, 0.5, 10, 30, "3x3.dat", 1, 0.75, 2),
    ("tiny_timestep", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.01, 10, 30, "3x3.dat", 1, 0.75, 2),
    ("sparse_landscape", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 30, "performance_experiment_20x20.dat", 1, 0.1, 2)
]

# Combined parameter list for comprehensive testing
all_parameter_variations = (
    basic_parameters + 
    birth_parameters + 
    movement_parameters + 
    timestep_parameters + 
    grid_parameters
)