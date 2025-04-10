#!/usr/bin/env python3
"""
experiment_cpu.py

CPU scaling experiment for predator-prey simulation.
Tests how simulation performance scales with different numbers of CPU cores.

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
    LANDSCAPE_DIR,
    CPU_COUNTS,
    DEFAULT_GRID,
    SEEDS,
    RESULTS_DIR,
    get_experiment_tag
)
from performance_experiment.src.performance_runner import run_simulation
from performance_experiment.src.performance_reporting import save_json, print_summary_table

# ── CPU Scaling Experiment ────────────────────────────────────────────────────
def run_cpu_scaling_experiment() -> Dict[str, Dict[str, List]]:
    """
    Run an experiment to measure how simulation performance scales with CPU count.
    
    The experiment runs simulations with different CPU core allocations while 
    keeping all other parameters constant.
    
    Returns:
        Dict: Results of the CPU scaling experiment
    """
    print("\n[RUNNING EXPERIMENT 3: CPU SCALING]\n")
    cpu_results: Dict[str, Dict[str, List]] = {}
    
    # This experiment uses higher land proportion for better load
    high_land_prop = 0.90
    
    for cpu in CPU_COUNTS:
        print(f"\n[CPU EXPERIMENT] Running with {cpu} CPUs\n")
        cpu_key = str(cpu)
        cpu_results[cpu_key] = {"runtime": [], "cpu_usage": [], "active_cores": []}
        
        for seed in SEEDS:
            print(f"[INFO] Running CPU scaling test: CPUs={cpu}, seed={seed}")
            landscape_file = os.path.join(LANDSCAPE_DIR, f"performance_experiment_{DEFAULT_GRID}x{DEFAULT_GRID}.dat")
            
            runtime, peak_usage, active_cores = run_simulation(
                landscape_file,
                high_land_prop, 
                seed, 
                cpu_override=cpu
            )
            
            cpu_results[cpu_key]["runtime"].append(runtime)
            cpu_results[cpu_key]["cpu_usage"].append(peak_usage)
            cpu_results[cpu_key]["active_cores"].append(active_cores)
        
        # Calculate averages for this CPU count
        avg_runtime = np.mean(cpu_results[cpu_key]["runtime"])
        avg_usage = np.mean(cpu_results[cpu_key]["cpu_usage"])
        avg_cores = np.mean(cpu_results[cpu_key]["active_cores"])
        
        print(f"[CPU EXPERIMENT SUMMARY] CPUs={cpu}")
        print(f"  Average runtime: {avg_runtime:.3f}s ± {np.std(cpu_results[cpu_key]['runtime']):.3f}s")
        print(f"  Average CPU usage: {avg_usage:.1f}% ± {np.std(cpu_results[cpu_key]['cpu_usage']):.1f}%")
        print(f"  Average active cores: {avg_cores:.1f} ± {np.std(cpu_results[cpu_key]['active_cores']):.1f}")
        print(f"  Utilization efficiency: {(avg_cores/cpu)*100:.1f}% of requested cores")
    
    # Save results to JSON
    experiment_tag = get_experiment_tag()
    save_json(
        cpu_results,
        os.path.join(RESULTS_DIR, "cpu_scaling", f"{experiment_tag}_cpu_scaling.json"),
        {
            "experiment": "cpu_scaling", 
            "grid_size": DEFAULT_GRID, 
            "land_prop": high_land_prop, 
            "cpu_counts": CPU_COUNTS,
            "seeds": SEEDS
        }
    )
    
    # Print a summary table
    print_summary_table(cpu_results, "cpu_scaling", CPU_COUNTS)
    
    return cpu_results

# ── Main Entry Point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Running CPU scaling experiment as standalone")
    run_cpu_scaling_experiment()