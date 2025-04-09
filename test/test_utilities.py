#!/usr/bin/env python3
"""
test_utilities.py

Utility functions for testing the refactored versions of the predator-prey simulation.
These utilities facilitate capturing output, comparing results, loading modules dynamically,
and other common operations needed across multiple test files.

Author: s2659865
Date: April 2025
"""
# Imports
import os
import sys
import importlib.util
import filecmp
import tempfile
import shutil
import hashlib
from io import StringIO
from contextlib import contextmanager
from typing import Dict, List, Tuple, Generator, Any, Callable

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ANIMALS_DIR = os.path.join(PROJECT_ROOT, "animals")
PERF_DIR = os.path.join(PROJECT_ROOT, "performance_experiment")
sys.path.append(PROJECT_ROOT)

# Import the original simulation
from performance_experiment.baseline import sim as original_sim


# ─── Output Capture Utilities ───────────────────────────────────────────────────
@contextmanager
def captured_output() -> Generator[Tuple[StringIO, StringIO], None, None]:
    """
    Capture stdout and stderr for testing.
    
    Returns:
        Generator yielding a tuple of (stdout_capture, stderr_capture)
    """
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield new_out, new_err
    finally:
        sys.stdout, sys.stderr = old_out, old_err


@contextmanager
def temporary_directory() -> Generator[str, None, None]:
    """
    Create a temporary directory for test outputs and change to it.
    
    Returns:
        Generator yielding the path to the temporary directory
    """
    temp_dir = tempfile.mkdtemp()
    prev_dir = os.getcwd()
    try:
        os.chdir(temp_dir)
        yield temp_dir
    finally:
        os.chdir(prev_dir)
        shutil.rmtree(temp_dir)


# ─── Module Loading Utilities ────────────────────────────────────────────────────
def load_refactored_implementation(refactor_name: str) -> Callable:
    """
    Dynamically load a refactored implementation by name.
    
    Args:
        refactor_name: Name of the refactored module without .py extension
    
    Returns:
        The sim function from the loaded module
    
    Raises:
        ImportError: If the module cannot be found or doesn't have a sim function
    """
    refactor_path = os.path.join(PERF_DIR, f"{refactor_name}.py")
    
    if not os.path.exists(refactor_path):
        raise ImportError(f"Refactored implementation {refactor_name} not found at {refactor_path}")
    
    spec = importlib.util.spec_from_file_location(refactor_name, refactor_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to create module spec for {refactor_name}")
        
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Check if the module has a sim function
    if hasattr(module, 'sim'):
        return module.sim
    else:
        raise ImportError(f"Module {refactor_name} does not have a sim function")


# ─── Output Comparison Utilities ───────────────────────────────────────────────
def filter_stdout(stdout: str) -> List[str]:
    """
    Filter stdout content to ignore lines that might legitimately differ.
    
    Args:
        stdout: The captured standard output as a string
    
    Returns:
        List of filtered lines that should be identical between implementations
    """
    return [
        line for line in stdout.strip().split('\n')
        if "Predator-prey simulation" not in line  # Ignore version line
        and "Averages. Timestep:" not in line  # Ignore timestamp lines
    ]


def compare_output_files(dir1: str, dir2: str) -> Dict[str, bool]:
    """
    Compare output files between two directories.
    
    Args:
        dir1: Path to the first directory
        dir2: Path to the second directory
    
    Returns:
        Dictionary with comparison results for different file types
    """
    results = {
        "csv_match": False,
        "ppm_match": True  # Will be set to False if any PPM doesn't match
    }
    
    # Compare CSV files
    if os.path.exists(os.path.join(dir1, "averages.csv")) and os.path.exists(os.path.join(dir2, "averages.csv")):
        results["csv_match"] = filecmp.cmp(
            os.path.join(dir1, "averages.csv"),
            os.path.join(dir2, "averages.csv"),
            shallow=False
        )
    
    # Find all PPM files in dir1
    ppm_files = [f for f in os.listdir(dir1) if f.endswith(".ppm")]
    
    # Compare each PPM file
    for ppm_file in ppm_files:
        if not os.path.exists(os.path.join(dir2, ppm_file)):
            results["ppm_match"] = False
            break
            
        if not filecmp.cmp(
            os.path.join(dir1, ppm_file),
            os.path.join(dir2, ppm_file),
            shallow=False
        ):
            results["ppm_match"] = False
            break
    
    return results


def run_output_comparison(
    original_sim_func: Callable, 
    refactored_sim_func: Callable, 
    args: Tuple
) -> Dict[str, Any]:
    """
    Compare outputs from original and refactored simulations.
    
    Args:
        original_sim_func: Reference to the original simulation function
        refactored_sim_func: Reference to the refactored simulation function
        args: Tuple of arguments to pass to both simulation functions
    
    Returns:
        Dictionary with comparison results between the two implementations
    """
    # Run original implementation
    with temporary_directory() as original_dir:
        with captured_output() as (original_out, original_err):
            original_sim_func(*args)
        
        original_stdout = original_out.getvalue()
        original_filtered_stdout = filter_stdout(original_stdout)
        
        # Run refactored implementation
        with temporary_directory() as refactored_dir:
            with captured_output() as (refactored_out, refactored_err):
                refactored_sim_func(*args)
            
            refactored_stdout = refactored_out.getvalue()
            refactored_filtered_stdout = filter_stdout(refactored_stdout)
            
            # Compare standard output
            stdout_match = original_filtered_stdout == refactored_filtered_stdout
            
            # Compare output files
            file_comparison = compare_output_files(original_dir, refactored_dir)
            
            # Determine overall match
            all_match = stdout_match and file_comparison["csv_match"] and file_comparison["ppm_match"]
    
    return {
        "stdout_match": stdout_match,
        "csv_match": file_comparison["csv_match"],
        "ppm_match": file_comparison["ppm_match"],
        "all_match": all_match
    }


def get_file_hash(file_path: str) -> str:
    """
    Compute an MD5 hash of a file's contents.
    
    Args:
        file_path: Path to the file to hash
    
    Returns:
        Hexadecimal string representing the file's hash
    """
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()