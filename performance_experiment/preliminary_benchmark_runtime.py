#!/usr/bin/env python3
"""
preliminary_benchmark_runtime.py

Benchmarks simulation runtime under four scenarios:
1. Grid size sweep (default land prop)
2. Land proportion sweep (default grid size)
3. CPU scaling sweep (default grid + land prop)
4. Full matrix (grid × land prop, no plots)

Each test is repeated across multiple seeds to ensure robustness,
and the results are saved as JSON for later visualization and comparison.

System info and full configuration are also saved for reproducibility.

Author: s2659865
Date: April 2025
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import os
import sys
import time
import json
import glob
import platform
import inspect
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
import psutil
import threading

# ── Import Simulation Entrypoint ──────────────────────────────────────────────
from baseline import simCommLineIntf

# ── Infer Experiment Tag Dynamically ─────────────────────────────────────────--
EXPERIMENT_TAG: str = os.path.splitext(os.path.basename(inspect.getfile(simCommLineIntf)))[0].upper()

# ── Configurations ─────────────────────────────────────────────────────────────
LANDSCAPE_DIR: str = os.path.join("..", "animals")
RESULTS_DIR: str = "performance_results"

GRID_SIZES: List[int] = [10, 20, 40]
LAND_PROPS: List[float] = [0.1, 0.2, 0.4, 0.8]
DEFAULT_GRID: int = 40
DEFAULT_LAND_PROP: float = 0.75

NUM_SEEDS: int = 3
SEEDS: List[int] = list(range(1, NUM_SEEDS + 1))
CPU_COUNTS: List[int] = [4, 8, 16, 32]
DEFAULT_CPU_COUNT: int = 32

# ── System Info ───────────────────────────────────────────────────────────────
def print_system_info() -> None:
    print("\n[SYSTEM INFO]")
    print(f"  OS              : {platform.system()} {platform.release()}")
    print(f"  Python Version  : {platform.python_version()}")
    print(f"  Max CPU Count   : {os.cpu_count()}")
    print(f"  Logical CPUs    : {psutil.cpu_count(logical=True)}")
    print(f"  Physical CPUs   : {psutil.cpu_count(logical=False)}")
    print("-" * 50)


# ── Simulation Wrapper with CPU Monitoring and Limiting ─────────────────────────
def run_simulation(landscape_file: str, land_prop: float, seed: int, cpu_override: int = None) -> Tuple[float, float, int]:
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
    requested_cpu_count = cpu_override if cpu_override else DEFAULT_CPU_COUNT
    sys.argv = [
        f"{EXPERIMENT_TAG.lower()}.py",
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
    import platform
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


# ── Benchmark Function ────────────────────────────────────────────────────────
def benchmark(
    grid_sizes: List[int],
    land_props: List[float],
    seeds: List[int],
    cpu_override: int = None
) -> Dict[str, Dict[str, List[float]]]:
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


# ── Save JSON Results ─────────────────────────────────────────────────────────
def save_json(results: Dict, path: str, meta: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    enriched_meta = meta.copy()
    enriched_meta.update({
        "seeds": SEEDS,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "logical_cpus": psutil.cpu_count(logical=True),
        "physical_cpus": psutil.cpu_count(logical=False),
        "omp_num_threads": meta.get("cpu_counts", [DEFAULT_CPU_COUNT]),
        "experiment_date": time.strftime("%Y-%m-%d %H:%M:%S")
    })

    out = {"metadata": enriched_meta, "results": results}

    with open(path, "w") as f:
        json.dump(out, f, indent=4)

    print(f"[INFO] Saved: {path}")


# ── Table Output ──────────────────────────────────────────────────────────────
def print_summary_table(results: Dict[str, Dict[str, List]], mode: str, axis_vals: List) -> None:
    print(f"\n[SUMMARY TABLE: {mode.upper()} — avg ± stdev over {NUM_SEEDS} seeds]")
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


# ── Cleanup ───────────────────────────────────────────────────────────────────
def cleanup_artifacts() -> None:
    if os.path.exists("averages.csv"):
        os.remove("averages.csv")

    for ppm_file in glob.glob("map_*.ppm"):
        try:
            os.remove(ppm_file)
        except Exception:
            pass


# ── CPU Scaling Experiment ─────────────────────────────────────────────────────
def run_cpu_scaling_experiment() -> Dict[str, Dict[str, List]]:
    print("\n[RUNNING EXPERIMENT 3: CPU SCALING]\n")
    cpu_results: Dict[str, Dict[str, List]] = {}
    
    for cpu in CPU_COUNTS:
        print(f"\n[CPU EXPERIMENT] Running with {cpu} CPUs\n")
        cpu_key = str(cpu)
        cpu_results[cpu_key] = {"runtime": [], "cpu_usage": [], "active_cores": []}
        
        for seed in SEEDS:
            print(f"[INFO] Running CPU scaling test: CPUs={cpu}, seed={seed}")
            landscape_file = os.path.join(LANDSCAPE_DIR, f"performance_experiment_{DEFAULT_GRID}x{DEFAULT_GRID}.dat")
            
            runtime, peak_usage, active_cores = run_simulation(
                landscape_file,
                0.90, 
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
    
    return cpu_results


# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print_system_info()

    print("\n[RUNNING EXPERIMENT 1: GRID SIZE SCALING]\n")
    grid_only = benchmark(GRID_SIZES, [DEFAULT_LAND_PROP], SEEDS)
    save_json(
        grid_only,
        os.path.join(RESULTS_DIR, "grid_scaling", f"{EXPERIMENT_TAG}_grid_scaling.json"),
        {"experiment": "grid_scaling", "land_prop": DEFAULT_LAND_PROP}
    )
    print_summary_table(grid_only, "grid_scaling", GRID_SIZES)

    print("\n[RUNNING EXPERIMENT 2: LANDSCAPE PROPORTION SCALING]\n")
    land_only = benchmark([DEFAULT_GRID], LAND_PROPS, SEEDS)
    save_json(
        land_only,
        os.path.join(RESULTS_DIR, "landscape_prop", f"{EXPERIMENT_TAG}_landscape_prop.json"),
        {"experiment": "landscape_prop", "grid_size": DEFAULT_GRID}
    )
    print_summary_table(land_only, "landscape_prop", LAND_PROPS)

    print("\n[RUNNING EXPERIMENT 3: CPU SCALING]\n")
    cpu_results = run_cpu_scaling_experiment()
    save_json(
        cpu_results,
        os.path.join(RESULTS_DIR, "cpu_scaling", f"{EXPERIMENT_TAG}_cpu_scaling.json"),
        {"experiment": "cpu_scaling", "grid_size": DEFAULT_GRID, "land_prop": 0.90, "cpu_counts": CPU_COUNTS}
    )
    print_summary_table(cpu_results, "cpu_scaling", CPU_COUNTS)

    print("\n[RUNNING EXPERIMENT 4: FULL RUNTIME MATRIX]\n")
    full_matrix = benchmark(GRID_SIZES, LAND_PROPS, SEEDS)
    save_json(
        full_matrix,
        os.path.join(RESULTS_DIR, "full_matrix", f"{EXPERIMENT_TAG}_runtime_matrix.json"),
        {"experiment": "grid_x_landprop_matrix"}
    )
    print("\n[SUMMARY] Full Runtime Matrix (avg ± stdev):\n")
    for grid in GRID_SIZES:
        row = f"{grid}x{grid}".ljust(12)
        for lp in LAND_PROPS:
            vals = full_matrix.get(f"{grid}x{grid}", {}).get(f"{lp:.2f}", [])
            if vals:
                mean = np.mean(vals)
                std = np.std(vals)
                row += f"{mean:.2f}±{std:.2f}".ljust(15)
            else:
                row += "N/A".ljust(15)
        print(row)