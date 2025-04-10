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
import argparse
from typing import Dict, List, Any

# Import core modules
from performance_core import (
    print_system_info,
    ensure_results_dirs,
    get_experiment_tag,
    set_implementation,
    get_available_implementations,
    DEFAULT_IMPLEMENTATION
)

# Import experiment modules
from experiment_grid import run_grid_scaling_experiment
from experiment_landscape import run_landscape_prop_experiment
from experiment_cpu import run_cpu_scaling_experiment
from experiment_matrix import run_full_matrix_experiment

# ── Command-line Argument Processing ───────────────────────────────────────────
def parse_arguments():
    """
    Parse command line arguments for the performance experiment framework.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description="Predator-Prey Simulation Performance Experiments")
    
    # Get available implementations
    available_implementations = get_available_implementations()
    
    parser.add_argument(
        "-i", "--implementation",
        type=str,
        default=DEFAULT_IMPLEMENTATION,
        choices=available_implementations,
        help=f"Implementation to use for experiments. Available: {', '.join(available_implementations)}"
    )
    
    parser.add_argument(
        "-e", "--experiments",
        type=str,
        nargs="+",
        choices=["grid", "landscape", "cpu", "matrix", "all"],
        default=["all"],
        help="Experiments to run (grid, landscape, cpu, matrix, or all)"
    )
    
    return parser.parse_args()

# ── Main Function ───────────────────────────────────────────────────────────────
def main() -> None:
    """
    Main function to run all performance experiments in sequence.
    
    This function is the primary entry point for the performance experiment suite
    and coordinates the execution of all experiments.
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set the implementation to use
    set_implementation(args.implementation)
    
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
    
    # Determine which experiments to run
    experiments_to_run = args.experiments
    run_all = "all" in experiments_to_run
    
    # Run Grid Size Scaling Experiment
    if run_all or "grid" in experiments_to_run:
        grid_results = run_grid_scaling_experiment()
    
    # Run Landscape Proportion Experiment
    if run_all or "landscape" in experiments_to_run:
        landscape_results = run_landscape_prop_experiment()
    
    # Run CPU Scaling Experiment
    if run_all or "cpu" in experiments_to_run:
        cpu_results = run_cpu_scaling_experiment()
    
    # Run Full Matrix Experiment
    if run_all or "matrix" in experiments_to_run:
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