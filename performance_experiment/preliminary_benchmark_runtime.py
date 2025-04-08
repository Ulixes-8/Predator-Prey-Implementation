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


# ── Simulation Wrapper ─────────────────────────────────────────────────────────
def run_simulation(landscape_file: str, land_prop: float, seed: int, cpu_override: int = None) -> float:
    sys.argv = [
        f"{EXPERIMENT_TAG.lower()}.py",
        "--landscape-file", landscape_file,
        "--landscape-prop", str(land_prop),
        "--landscape-seed", str(seed)
    ]

    os.environ["OMP_NUM_THREADS"] = str(cpu_override if cpu_override else DEFAULT_CPU_COUNT)

    start = time.perf_counter()
    simCommLineIntf()
    end = time.perf_counter()

    cleanup_artifacts()

    return end - start


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
                t = run_simulation(landscape_path, lp, seed, cpu_override)
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
        "omp_num_threads": meta.get("cpu_counts", [DEFAULT_CPU_COUNT])
    })

    out = {"metadata": enriched_meta, "results": results}

    with open(path, "w") as f:
        json.dump(out, f, indent=4)

    print(f"[INFO] Saved: {path}")


# ── Table Output ──────────────────────────────────────────────────────────────
def print_summary_table(results: Dict[str, Dict[str, List[float]]], mode: str, axis_vals: List) -> None:
    print(f"\n[SUMMARY TABLE: {mode.upper()} — avg ± stdev over {NUM_SEEDS} seeds]")
    print("-" * 80)
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
        print("CPU Count".ljust(12) + "Runtime (s)".rjust(20))
        for cpu in axis_vals:
            times = results.get(str(cpu), [])
            if times:
                print(f"{str(cpu).ljust(12)}{np.mean(times):>10.3f} ± {np.std(times):<.3f}")
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
    cpu_results: Dict[str, List[float]] = {}
    for cpu in CPU_COUNTS:
        print(f"\n[CPU EXPERIMENT] Running with {cpu} CPUs\n")
        result = benchmark([DEFAULT_GRID], [0.90], SEEDS, cpu_override=cpu)
        cpu_results[str(cpu)] = result[f"{DEFAULT_GRID}x{DEFAULT_GRID}"]["0.90"]

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