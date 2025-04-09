#!/usr/bin/env python3
"""
experiment_landscape.py

Landscape proportion scaling experiment for predator-prey simulation.
Tests how simulation performance scales with different proportions of land vs. water.

Author: s2659865
Date: April 2025
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import os
import sys
from typing import Dict, List, Any

# Import from other modules
from performance_core import (
    LAND_PROPS,
    DEFAULT_GRID,
    SEEDS,
    RESULTS_DIR,
    get_experiment_tag
)
from performance_runner import benchmark
from performance_reporting import save_json, print_summary_table

# ── Landscape Proportion Experiment ───────────────────────────────────────────
def run_landscape_prop_experiment() -> Dict[str, Dict[str, List[float]]]:
    """
    Run an experiment to measure how simulation performance scales with landscape proportion.
    
    The experiment runs simulations for different proportions of land vs. water
    while keeping all other parameters constant.
    
    Returns:
        Dict: Results of the landscape proportion experiment
    """
    print("\n[RUNNING EXPERIMENT 2: LANDSCAPE PROPORTION SCALING]\n")
    
    # Run the benchmark with different land proportions
    land_results = benchmark(
        grid_sizes=[DEFAULT_GRID],  # Use only the default grid size
        land_props=LAND_PROPS,
        seeds=SEEDS
    )
    
    # Save results to JSON
    experiment_tag = get_experiment_tag()
    save_json(
        land_results,
        os.path.join(RESULTS_DIR, "landscape_prop", f"{experiment_tag}_landscape_prop.json"),
        {
            "experiment": "landscape_prop", 
            "grid_size": DEFAULT_GRID,
            "seeds": SEEDS
        }
    )
    
    # Print a summary table
    print_summary_table(land_results, "landscape_prop", LAND_PROPS)
    
    return land_results

# ── Main Entry Point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Running landscape proportion experiment as standalone")
    run_landscape_prop_experiment()