#!/usr/bin/env python3
"""
experiment_grid.py

Grid size scaling experiment for predator-prey simulation.
Tests how simulation performance scales with increasing grid sizes.

Author: s2659865
Date: April 2025
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import os
import sys
from typing import Dict, List, Any

# Import from other modules
from performance_experiment.src.performance_core import (
    GRID_SIZES, 
    DEFAULT_LAND_PROP, 
    SEEDS,
    RESULTS_DIR,
    get_experiment_tag
)
from performance_experiment.src.performance_runner import benchmark
from performance_experiment.src.performance_reporting import save_json, print_summary_table

# ── Grid Scaling Experiment ──────────────────────────────────────────────────
def run_grid_scaling_experiment() -> Dict[str, Dict[str, List[float]]]:
    """
    Run an experiment to measure how simulation performance scales with grid size.
    
    The experiment runs simulations for different grid sizes while keeping
    all other parameters constant.
    
    Returns:
        Dict: Results of the grid scaling experiment
    """
    print("\n[RUNNING EXPERIMENT 1: GRID SIZE SCALING]\n")
    
    # Run the benchmark for different grid sizes
    grid_results = benchmark(
        grid_sizes=GRID_SIZES,  
        land_props=[DEFAULT_LAND_PROP],  # Use only the default land proportion
        seeds=SEEDS
    )
    
    # Save results to JSON
    experiment_tag = get_experiment_tag()
    save_json(
        grid_results,
        os.path.join(RESULTS_DIR, "grid_scaling", f"{experiment_tag}_grid_scaling.json"),
        {
            "experiment": "grid_scaling", 
            "land_prop": DEFAULT_LAND_PROP,
            "seeds": SEEDS
        }
    )
    
    # Print a summary table
    print_summary_table(grid_results, "grid_scaling", GRID_SIZES)
    
    return grid_results

# ── Main Entry Point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Running grid scaling experiment as standalone")
    run_grid_scaling_experiment()