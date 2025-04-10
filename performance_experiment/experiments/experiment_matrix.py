#!/usr/bin/env python3
"""
experiment_matrix.py

Full matrix experiment for predator-prey simulation.
Tests all combinations of grid sizes and land proportions to create a comprehensive
performance profile.

Author: s2659865
Date: April 2025
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import os
import sys
import numpy as np
from typing import Dict, List, Any

# Import from other modules
from performance_experiment.src.performance_core import (
    GRID_SIZES,
    LAND_PROPS,
    SEEDS,
    RESULTS_DIR,
    get_experiment_tag
)
from performance_experiment.src.performance_runner import benchmark
from performance_experiment.src.performance_reporting import save_json, print_summary_table

# ── Full Matrix Experiment ────────────────────────────────────────────────────
def run_full_matrix_experiment() -> Dict[str, Dict[str, List[float]]]:
    """
    Run a full matrix experiment testing all combinations of grid sizes and land proportions.
    
    This provides a comprehensive performance profile of the simulation across
    different configurations.
    
    Returns:
        Dict: Results of the full matrix experiment
    """
    print("\n[RUNNING EXPERIMENT 4: FULL RUNTIME MATRIX]\n")
    
    # Run the benchmark with all combinations
    full_matrix = benchmark(
        grid_sizes=GRID_SIZES,
        land_props=LAND_PROPS,
        seeds=SEEDS
    )
    
    # Save results to JSON
    experiment_tag = get_experiment_tag()
    save_json(
        full_matrix,
        os.path.join(RESULTS_DIR, "full_matrix", f"{experiment_tag}_runtime_matrix.json"),
        {
            "experiment": "grid_x_landprop_matrix",
            "seeds": SEEDS
        }
    )
    
    # Print a summary table
    print_summary_table(full_matrix, "full_matrix", LAND_PROPS)
    
    return full_matrix

# ── Main Entry Point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Running full matrix experiment as standalone")
    run_full_matrix_experiment()