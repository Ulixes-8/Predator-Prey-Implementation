#!/usr/bin/env python3
"""
performance_reporting.py

Results handling and reporting utilities for predator-prey simulation experiments.
This module provides functions for saving results to JSON files, generating
summary tables, and visualizing experiment data.

Author: s2659865
Date: April 2025
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import os
import json
import time
import platform
import sys
import psutil
import numpy as np
from typing import Dict, List, Any

# ── JSON Results Storage ─────────────────────────────────────────────────────
def save_json(results: Dict, path: str, meta: Dict[str, Any]) -> None:
    """
    Save experiment results and metadata to a JSON file.
    
    Args:
        results: Experiment results to save
        path: File path for the JSON output
        meta: Metadata to include with the results
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Enrich metadata with system information and timestamps
    enriched_meta = meta.copy()
    enriched_meta.update({
        "seeds": meta.get("seeds", [1, 2, 3]),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "logical_cpus": psutil.cpu_count(logical=True),
        "physical_cpus": psutil.cpu_count(logical=False),
        "omp_num_threads": meta.get("cpu_counts", [32]),
        "experiment_date": time.strftime("%Y-%m-%d %H:%M:%S")
    })

    # Create output dictionary
    out = {"metadata": enriched_meta, "results": results}

    # Write JSON with indentation for human readability
    with open(path, "w") as f:
        json.dump(out, f, indent=4)

    print(f"[INFO] Saved: {path}")


# ── Summary Table Generation ─────────────────────────────────────────────────
def print_summary_table(results: Dict[str, Dict[str, List]], mode: str, axis_vals: List) -> None:
    """
    Print a formatted summary table of experiment results.
    
    Args:
        results: Dictionary containing experiment results
        mode: Type of experiment ('grid_scaling', 'landscape_prop', 'cpu_scaling')
        axis_vals: Values for the x-axis of the table
    """
    print(f"\n[SUMMARY TABLE: {mode.upper()} — avg ± stdev over {len(results.get(list(results.keys())[0], {}).get(list(results.get(list(results.keys())[0], {}).keys())[0], []))} seeds]")
    print("-" * 100)
    
    if mode == "grid_scaling":
        print("Grid Size".ljust(12) + "Runtime (s)".rjust(20))
        for grid in axis_vals:
            key = f"{grid}x{grid}"
            times = list(results.get(key, {}).values())[0]
            print(f"{key.ljust(12)}{np.mean(times):>10.3f} ± {np.std(times):<.3f}")
            
    elif mode == "landscape_prop":
        grid_key = list(results.keys())[0]
        print("Land Prop".ljust(12) + "Runtime (s)".rjust(20))
        for lp in axis_vals:
            times = results[grid_key].get(f"{lp:.2f}", [])
            print(f"{str(lp).ljust(12)}{np.mean(times):>10.3f} ± {np.std(times):<.3f}")
            
    elif mode == "cpu_scaling":
        header = ("CPU Count".ljust(12) + 
                 "Runtime (s)".rjust(20) + 
                 "CPU Usage (%)".rjust(20) + 
                 "Active Cores".rjust(15) + 
                 "Efficiency (%)".rjust(20))
        print(header)
        print("-" * 100)
        
        for cpu in axis_vals:
            cpu_key = str(cpu)
            if cpu_key in results:
                runtime = np.mean(results[cpu_key]["runtime"])
                runtime_std = np.std(results[cpu_key]["runtime"])
                usage = np.mean(results[cpu_key]["cpu_usage"])
                usage_std = np.std(results[cpu_key]["cpu_usage"])
                cores = np.mean(results[cpu_key]["active_cores"])
                cores_std = np.std(results[cpu_key]["active_cores"])
                efficiency = (cores / float(cpu)) * 100 if float(cpu) > 0 else 0
                
                print(f"{str(cpu).ljust(12)}" + 
                      f"{runtime:>10.3f} ± {runtime_std:<.3f}" + 
                      f"{usage:>15.1f} ± {usage_std:<.1f}" + 
                      f"{cores:>12.1f} ± {cores_std:<.1f}" + 
                      f"{efficiency:>17.1f}")
            else:
                print(f"{str(cpu).ljust(12)}{'N/A':>10}")
    
    elif mode == "full_matrix":
        print("\n[SUMMARY] Full Runtime Matrix (avg ± stdev):\n")
        # Print header row
        header = "Grid Size".ljust(12)
        for lp in axis_vals:
            header += f"Land {lp:.2f}".ljust(15)
        print(header)
        
        # Print data rows
        for grid in sorted([int(k.split('x')[0]) for k in results.keys()]):
            grid_key = f"{grid}x{grid}"
            if grid_key in results:
                row = grid_key.ljust(12)
                for lp in axis_vals:
                    lp_key = f"{lp:.2f}"
                    if lp_key in results[grid_key]:
                        vals = results[grid_key][lp_key]
                        mean = np.mean(vals)
                        std = np.std(vals)
                        row += f"{mean:.2f}±{std:.2f}".ljust(15)
                    else:
                        row += "N/A".ljust(15)
                print(row)


# ── Results Visualization ──────────────────────────────────────────────────────
def create_visualization(results_file: str, output_file: str = None) -> None:
    """
    Create a visualization of experiment results.
    
    Note: This is a placeholder function for future implementation.
    Currently it just prints a message about visualization.
    
    Args:
        results_file: Path to the JSON results file
        output_file: Path for the output visualization file (optional)
    """
    # This is a placeholder for potential visualizations
    
    # For now, just print a message
    print(f"[INFO] Visualization for {results_file} would be generated here.")
    print("[INFO] This functionality is not yet implemented.")


# ── Main Entry Point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("This module is not intended to be run directly.")
    print("Please use performance_experiment.py instead.")
    sys.exit(1)