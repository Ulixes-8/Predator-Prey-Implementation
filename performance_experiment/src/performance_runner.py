#!/usr/bin/env python3
"""
performance_runner.py

Simulation execution and benchmarking utilities for predator-prey experiments.
This module provides functions for running simulations with controlled CPU usage,
monitoring resource utilization, and collecting performance metrics.

Author: s2659865
Date: April 2025
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import os
import sys
import time
import threading
import platform
import numpy as np
import psutil
from typing import Dict, List, Tuple, Any, Optional

# Import core functionality
from performance_experiment.src.performance_core import (
    LANDSCAPE_DIR,
    cleanup_artifacts,
    DEFAULT_CPU_COUNT,
    get_sim_command_line_interface,
    get_implementation
)

# ── Simulation Wrapper with CPU Monitoring ────────────────────────────────────
def run_simulation(
    landscape_file: str, 
    land_prop: float, 
    seed: int, 
    cpu_override: Optional[int] = None
) -> Tuple[float, float, int]:
    """
    Run simulation with the given parameters, monitor CPU usage, and enforce CPU limits.
    
    Args:
        landscape_file: Path to landscape file
        land_prop: Land proportion
        seed: Random seed
        cpu_override: Number of CPUs to use (or DEFAULT_CPU_COUNT if None)
    
    Returns:
        Tuple[float, float, int]: (runtime in seconds, peak CPU utilization percentage, max active cores)
    """
    # Get the simulation function from the current implementation
    simCommLineIntf = get_sim_command_line_interface()
    
    requested_cpu_count = cpu_override if cpu_override is not None else DEFAULT_CPU_COUNT
    sys.argv = [
        f"{get_implementation()}.py",
        "--landscape-file", landscape_file,
        "--landscape-prop", str(land_prop),
        "--landscape-seed", str(seed)
    ]

    # Set multiple environment variables to control CPU usage across different libraries and frameworks
    os.environ["OMP_NUM_THREADS"] = str(requested_cpu_count)
    os.environ["MKL_NUM_THREADS"] = str(requested_cpu_count)  # Intel MKL
    os.environ["NUMEXPR_NUM_THREADS"] = str(requested_cpu_count)  # NumExpr
    os.environ["OPENBLAS_NUM_THREADS"] = str(requested_cpu_count)  # OpenBLAS
    os.environ["VECLIB_MAXIMUM_THREADS"] = str(requested_cpu_count)  # Accelerate
    os.environ["NUMBA_NUM_THREADS"] = str(requested_cpu_count)  # Numba
    os.environ["TBB_NUM_THREADS"] = str(requested_cpu_count)  # Intel TBB
    os.environ["PYTHONEXECUTABLE"] = sys.executable  # Ensure subprocesses inherit env vars
    
    print(f"[CPU INFO] Requested CPU count: {requested_cpu_count}")
    print(f"[CPU INFO] Set thread limits for OMP, MKL, NumExpr, OpenBLAS, VecLib, Numba, and TBB")
    
    # Use process affinity to hard-limit available CPUs (only works on Linux and Windows)
    try:
        if platform.system() in ["Linux", "Windows"]:
            p = psutil.Process()
            total_cpus = psutil.cpu_count(logical=True)
            
            if total_cpus <= requested_cpu_count:
                # If requesting all or more CPUs than available, use all CPUs
                cpu_list = list(range(total_cpus))
            else:
                # Otherwise, limit to first N CPUs
                cpu_list = list(range(requested_cpu_count))
            
            p.cpu_affinity(cpu_list)
            print(f"[CPU LIMIT] Process affinity set to CPUs: {p.cpu_affinity()}")
        else:
            print(f"[CPU LIMIT] Process affinity not supported on {platform.system()}")
    except Exception as e:
        print(f"[WARNING] Unable to set CPU affinity: {e}")
    
    # Use shared variables to collect monitoring results
    cpu_monitor_results = {
        "max_usage": 0.0,
        "max_active_cores": 0,
        "monitoring_active": True,
        "exceeded_limit": False
    }
    
    # Define CPU monitoring function with limit checking
    def monitor_cpu_usage():
        while cpu_monitor_results["monitoring_active"]:
            # Get per-CPU utilization percentages
            per_cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # Calculate how many cores are actively being used (>50% utilization)
            active_cores = sum(1 for cpu_percent in per_cpu_percent if cpu_percent > 50)
            cpu_monitor_results["max_active_cores"] = max(cpu_monitor_results["max_active_cores"], active_cores)
            
            # Check if exceeding requested CPU count (with a small tolerance)
            if active_cores > requested_cpu_count + 1:  # Allow 1 extra for monitoring overhead
                cpu_monitor_results["exceeded_limit"] = True
                print(f"[CPU WARNING] Using {active_cores} cores, exceeds requested {requested_cpu_count}")
            
            # Get overall CPU usage
            usage = psutil.cpu_percent(interval=0)
            cpu_monitor_results["max_usage"] = max(cpu_monitor_results["max_usage"], usage)
            
            # Print real-time feedback periodically
            if active_cores > 0:
                status = "✓" if active_cores <= requested_cpu_count else "!"
                print(f"[CPU MONITOR] {status} Active cores: {active_cores}/{psutil.cpu_count(logical=True)}, Usage: {usage:.1f}%", 
                      end="\r", flush=True)
            
            time.sleep(0.5)
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_cpu_usage)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Run simulation
    start = time.perf_counter()
    simCommLineIntf()
    end = time.perf_counter()
    
    # Stop monitoring
    cpu_monitor_results["monitoring_active"] = False
    monitor_thread.join(timeout=1.0)
    
    print()  # New line after carriage returns
    print(f"[CPU MONITORING] Peak CPU usage: {cpu_monitor_results['max_usage']:.1f}%, "
          f"Max active cores: {cpu_monitor_results['max_active_cores']}/{psutil.cpu_count(logical=True)}")
    print(f"[CPU VERIFICATION] Requested: {requested_cpu_count}, "
          f"Actual max cores active: {cpu_monitor_results['max_active_cores']}")
    
    # Print warnings if CPU limits were exceeded
    if cpu_monitor_results["exceeded_limit"]:
        print(f"[CPU WARNING] The simulation exceeded the requested CPU limit of {requested_cpu_count}!")
        print(f"[CPU WARNING] This may indicate that OpenMP/thread limiting is not working properly.")
    
    # Calculate core utilization efficiency
    if requested_cpu_count > 0:
        efficiency = (cpu_monitor_results['max_active_cores'] / requested_cpu_count) * 100
        print(f"[CPU EFFICIENCY] {efficiency:.1f}% of requested cores were utilized")
    
    cleanup_artifacts()
    
    return end - start, cpu_monitor_results["max_usage"], cpu_monitor_results["max_active_cores"]


# ── Benchmarking Function ────────────────────────────────────────────────────
def benchmark(
    grid_sizes: List[int],
    land_props: List[float],
    seeds: List[int],
    cpu_override: Optional[int] = None
) -> Dict[str, Dict[str, List[float]]]:
    """
    Run benchmarks across multiple grid sizes, land proportions, and seeds.
    
    Args:
        grid_sizes: List of grid sizes to test
        land_props: List of land proportions to test
        seeds: List of random seeds to use
        cpu_override: Number of CPUs to use (or None for default)
    
    Returns:
        Nested dictionary of results indexed by grid size and land proportion
    """
    results: Dict[str, Dict[str, List[float]]] = {}

    for grid in grid_sizes:
        grid_key = f"{grid}x{grid}"
        landscape_path = os.path.join(LANDSCAPE_DIR, f"performance_experiment_{grid}x{grid}.dat")

        if not os.path.exists(landscape_path):
            print(f"[WARNING] Missing file: {landscape_path}")
            continue

        results[grid_key] = {}

        for lp in land_props:
            lp_key = f"{lp:.2f}"
            times = []

            print(f"[EXPERIMENT] Now running: Grid Size = {grid}, Land Prop = {lp_key}")

            for seed in seeds:
                print(f"[INFO] Running: {grid_key}, land={lp_key}, seed={seed}")
                t, _, _ = run_simulation(landscape_path, lp, seed, cpu_override)
                times.append(t)

            print(f"[DEBUG] Completed {grid_key} | land={lp_key} → Mean: {np.mean(times):.3f}s ± {np.std(times):.3f}s\n")
            results[grid_key][lp_key] = times

    return results

# ── Main Entry Point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("This module is not intended to be run directly.")
    print("Please use performance_experiment.py instead.")
    sys.exit(1)