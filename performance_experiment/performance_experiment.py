#!/usr/bin/env python3
"""
performance_experiment.py

Main entry point for predator-prey simulation performance experiments.
Coordinates the execution of multiple experiments to evaluate performance characteristics
of the simulation under different conditions.

Author: s2659865
Date: April 2025
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import os
import sys
import time
from typing import Dict, List, Any

# Import core modules
from performance_core import (
    print_system_info,
    ensure_results_dirs,
    get_experiment_tag
)

# Import experiment modules
from experiment_grid import run_grid_scaling_experiment
from experiment_landscape import run_landscape_prop_experiment
from experiment_cpu import run_cpu_scaling_experiment
from experiment_matrix import run_full_matrix_experiment

# ── Main Function ───────────────────────────────────────────────────────────────
def main() -> None:
    """
    Main function to run all performance experiments in sequence.
    
    This function is the primary entry point for the performance experiment suite
    and coordinates the execution of all experiments.
    """
    # Ensure results directories exist
    ensure_results_dirs()
    
    # Print header
    print("=" * 80)
    print(f"PREDATOR-PREY SIMULATION PERFORMANCE EXPERIMENTS: {get_experiment_tag()}")
    print("=" * 80)
    
    # Print system information for reproducibility
    print_system_info()
    
    # Track overall execution time
    start_time = time.time()
    
    # Run Grid Size Scaling Experiment
    grid_results = run_grid_scaling_experiment()
    
    # Run Landscape Proportion Experiment
    landscape_results = run_landscape_prop_experiment()
    
    # Run CPU Scaling Experiment
    cpu_results = run_cpu_scaling_experiment()
    
    # Run Full Matrix Experiment
    matrix_results = run_full_matrix_experiment()
    
    # Print overall execution time
    total_time = time.time() - start_time
    minutes, seconds = divmod(total_time, 60)
    hours, minutes = divmod(minutes, 60)
    
    print("\n" + "=" * 80)
    print(f"All experiments completed in {int(hours):02d}:{int(minutes):02d}:{seconds:.2f}")
    print(f"Results stored in {os.path.abspath(os.path.join(os.path.dirname(__file__), 'performance_results'))}")
    print("=" * 80)

# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()