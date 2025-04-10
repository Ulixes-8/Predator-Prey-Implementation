#!/usr/bin/env python3
"""
performance_core.py

Core utilities and configuration for predator-prey simulation performance experiments.
This module contains shared constants, system information utilities, and cleanup functions
used by the performance experiment framework.

Author: s2659865
Date: April 2025
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import os
import sys
import glob
import platform
import psutil
import time
import inspect
import importlib
from typing import Dict, Any, Optional

# ── Directories and Paths ──────────────────────────────────────────────────────
# Base directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
LANDSCAPE_DIR = os.path.join(PROJECT_ROOT, "animals")
RESULTS_DIR = "performance_results"

# ── Implementation Selection ────────────────────────────────────────────────────
# Default implementation to use
DEFAULT_IMPLEMENTATION = "baseline"
# Currently selected implementation (set by set_implementation)
CURRENT_IMPLEMENTATION = None
# Cached simulation function
SIM_COMMAND_LINE_INTERFACE = None

def set_implementation(implementation: str) -> None:
    """
    Set the implementation to use for experiments.
    
    Args:
        implementation: Name of the implementation module (e.g., 'baseline', 'refactor_1')
    """
    global CURRENT_IMPLEMENTATION, SIM_COMMAND_LINE_INTERFACE
    
    if implementation not in get_available_implementations():
        raise ValueError(f"Implementation '{implementation}' not found. Available implementations: {get_available_implementations()}")
    
    CURRENT_IMPLEMENTATION = implementation
    
    # Dynamically import the specified implementation
    try:
        implementation_module = importlib.import_module(implementation)
        SIM_COMMAND_LINE_INTERFACE = implementation_module.simCommLineIntf
    except (ImportError, AttributeError) as e:
        print(f"[ERROR] Failed to import implementation '{implementation}': {e}")
        sys.exit(1)
    
    print(f"[INFO] Using implementation: {implementation.upper()}")

def get_implementation() -> str:
    """
    Get the currently selected implementation.
    
    Returns:
        str: Name of the current implementation
    """
    global CURRENT_IMPLEMENTATION
    if CURRENT_IMPLEMENTATION is None:
        set_implementation(DEFAULT_IMPLEMENTATION)
    return CURRENT_IMPLEMENTATION

def get_sim_command_line_interface():
    """
    Get the simulation command line interface function from the current implementation.
    
    Returns:
        function: The simCommLineIntf function from the current implementation
    """
    global SIM_COMMAND_LINE_INTERFACE
    if SIM_COMMAND_LINE_INTERFACE is None:
        get_implementation()  # This will set SIM_COMMAND_LINE_INTERFACE
    return SIM_COMMAND_LINE_INTERFACE

def get_available_implementations() -> list:
    """
    Get a list of available implementations in the current directory.
    
    Returns:
        list: List of implementation module names
    """
    implementations = []
    
    # Check for baseline
    if os.path.exists(os.path.join(SCRIPT_DIR, "baseline.py")):
        implementations.append("baseline")
    
    # Check for main implementation wrapper
    if os.path.exists(os.path.join(SCRIPT_DIR, "simulate_predator_prey_wrapper.py")):
        implementations.append("simulate_predator_prey_wrapper")
    
    # Check for refactored implementations
    for i in range(1, 10):  # Assuming we won't have more than 9 refactored versions
        refactor_file = f"refactor_{i}.py"
        if os.path.exists(os.path.join(SCRIPT_DIR, refactor_file)):
            implementations.append(f"refactor_{i}")
    
    return implementations

# Create results directory structure if it doesn't exist
def ensure_results_dirs() -> None:
    """
    Create the directory structure for storing experiment results if it doesn't exist.
    """
    for subdir in ["grid_scaling", "landscape_prop", "cpu_scaling", "full_matrix"]:
        os.makedirs(os.path.join(RESULTS_DIR, subdir), exist_ok=True)

# ── Experiment Configuration ────────────────────────────────────────────────────
# Grid sizes for experiments
GRID_SIZES = [10, 20, 40, 80, 160]  # For most experiments
# GRID_SIZES = [320, 640, 1280, 2560]  # For specific grid scaling tests

# Land proportion values
LAND_PROPS = [0.1, 0.2, 0.4, 0.8]
DEFAULT_LAND_PROP = 0.75

# CPU configurations
DEFAULT_GRID = 160
DEFAULT_CPU_COUNT = os.cpu_count()  # Default to the maximum available 

# CPU counts should be 4 up to cpu count in increments of 4
CPU_COUNTS = [n for n in range(4, DEFAULT_CPU_COUNT + 1, 4) if n <= DEFAULT_CPU_COUNT]

# Repetition for statistical validity
NUM_SEEDS = 3
SEEDS = list(range(1, NUM_SEEDS + 1))

# ── Experiment Tag Generation ────────────────────────────────────────────────────
def get_experiment_tag() -> str:
    """
    Get a tag for the current experiment based on the implementation being used.
    
    Returns:
        str: The uppercase name of the current implementation (e.g., 'BASELINE', 'REFACTOR_1')
    """
    implementation = get_implementation()
    if implementation == "simulate_predator_prey_wrapper":
        return "MAIN_IMPLEMENTATION"
    return implementation.upper()

# ── System Information ───────────────────────────────────────────────────────────
def get_system_info() -> Dict[str, Any]:
    """
    Gather system information for reproducibility of experiments.
    
    Returns:
        Dict[str, Any]: Dictionary containing system specifications
    """
    return {
        "os": f"{platform.system()} {platform.release()}",
        "python_version": platform.python_version(),
        "cpu_model": platform.processor(),
        "max_cpu_count": os.cpu_count(),
        "logical_cpus": psutil.cpu_count(logical=True),
        "physical_cpus": psutil.cpu_count(logical=False),
        "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "platform_full": platform.platform(),
        "implementation": get_implementation()
    }

def print_system_info() -> None:
    """
    Print system information to the console in a human-readable format.
    """
    info = get_system_info()
    print("\n[SYSTEM INFO]")
    print(f"  OS              : {info['os']}")
    print(f"  Python Version  : {info['python_version']}")
    print(f"  CPU Model       : {info['cpu_model']}")
    print(f"  Max CPU Count   : {info['max_cpu_count']}")
    print(f"  Logical CPUs    : {info['logical_cpus']}")
    print(f"  Physical CPUs   : {info['physical_cpus']}")
    print(f"  Memory (GB)     : {info['total_memory_gb']}")
    print(f"  Implementation  : {info['implementation'].upper()}")
    print("-" * 50)

# ── Cleanup Utilities ───────────────────────────────────────────────────────────
def cleanup_artifacts() -> None:
    """
    Remove temporary files generated by the simulation.
    
    This includes averages.csv and map_*.ppm files that are created
    during each simulation run.
    """
    if os.path.exists("averages.csv"):
        os.remove("averages.csv")

    for ppm_file in glob.glob("map_*.ppm"):
        try:
            os.remove(ppm_file)
        except Exception as e:
            print(f"[WARNING] Failed to remove {ppm_file}: {e}")

# ── Main Entry Point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("This module is not intended to be run directly.")
    print("Please use performance_experiment.py instead.")
    sys.exit(1)