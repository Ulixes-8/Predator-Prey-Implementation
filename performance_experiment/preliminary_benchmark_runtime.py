#!/usr/bin/env python3
"""
preliminary_benchmark_runtime.py

Benchmarks simulation runtime under three scenarios:
1. Grid size sweep (default land prop)
2. Land proportion sweep (default grid size)
3. Full matrix (grid × land prop, no plots)

Each test is repeated across multiple seeds to ensure robustness,
and the results are saved as JSON for later visualization and comparison.

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

# ── Import Simulation Entrypoint ──────────────────────────────────────────────
# Use the simulation logic from baseline implementation
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
CPU_COUNT: int = 32

# ── System Info ───────────────────────────────────────────────────────────────
def print_system_info() -> None:
    print("\n[SYSTEM INFO]")
    print(f"  OS              : {platform.system()} {platform.release()}")
    print(f"  Python Version  : {platform.python_version()}")
    print(f"  CPU Count Used  : {CPU_COUNT}")
    print("-" * 50)


# ── Simulation Wrapper ─────────────────────────────────────────────────────────
def run_simulation(landscape_file: str, land_prop: float, seed: int) -> float:
    """
    Mocks CLI args and times the simulation run.

    Args:
        landscape_file (str): .dat landscape path.
        land_prop (float): Proportion of land cells.
        seed (int): Random seed for reproducibility.

    Returns:
        float: Runtime in seconds.
    """
    sys.argv = [
        "simulate_predator_prey.py",
        "--landscape-file", landscape_file,
        "--landscape-prop", str(land_prop),
        "--landscape-seed", str(seed)
    ]

    start = time.perf_counter()
    simCommLineIntf()
    end = time.perf_counter()

    cleanup_artifacts()

    return end - start


# ── Benchmark Function ────────────────────────────────────────────────────────
def benchmark(
    grid_sizes: List[int],
    land_props: List[float],
    seeds: List[int]
) -> Dict[str, Dict[str, List[float]]]:
    """
    Runs simulation for all (grid, land_prop, seed) combinations.

    Returns:
        Dict[str, Dict[str, List[float]]]: Nested results[grid][land_prop] = [runtimes...]
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
                t = run_simulation(landscape_path, lp, seed)
                times.append(t)

            print(f"[DEBUG] Completed {grid_key} | land={lp_key} → Mean: {np.mean(times):.3f}s ± {np.std(times):.3f}s\n")
            results[grid_key][lp_key] = times

    return results


# ── Save JSON Results ─────────────────────────────────────────────────────────
def save_json(results: Dict[str, Dict[str, List[float]]], path: str, meta: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out = {"metadata": meta, "results": results}

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


# ── Plotting ──────────────────────────────────────────────────────────────────
def plot_experiment(
    results: Dict[str, Dict[str, List[float]]],
    x_axis: List[float],
    x_label: str,
    filename: str,
    mode: str
) -> None:
    plt.figure(figsize=(10, 6))

    if mode == "grid_scaling":
        means, stds = [], []
        for grid in x_axis:
            key = f"{grid}x{grid}"
            times = list(results.get(key, {}).values())[0]
            means.append(np.mean(times) if times else np.nan)
            stds.append(np.std(times) if times else np.nan)

        means = np.array(means)
        stds = np.array(stds)
        plt.plot(x_axis, means, label=EXPERIMENT_TAG, marker="o")
        plt.fill_between(x_axis, means - stds, means + stds, alpha=0.2)

    elif mode == "landscape_prop":
        grid_key = list(results.keys())[0]
        means, stds = [], []
        for lp in x_axis:
            lp_key = f"{lp:.2f}"
            times = results[grid_key].get(lp_key, [])
            means.append(np.mean(times) if times else np.nan)
            stds.append(np.std(times) if times else np.nan)

        means = np.array(means)
        stds = np.array(stds)
        plt.plot(x_axis, means, label=grid_key, marker="o")
        plt.fill_between(x_axis, means - stds, means + stds, alpha=0.2)

    plt.title(f"Runtime vs {x_label} (avg ± stdev over {NUM_SEEDS} seeds)")
    plt.xlabel(x_label)
    plt.ylabel("Runtime (s)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    print(f"[INFO] Saved: {filename}")


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
        {"experiment": "grid_scaling", "land_prop": DEFAULT_LAND_PROP, "cpu_count": CPU_COUNT, "seeds": SEEDS}
    )
    plot_experiment(
        grid_only,
        GRID_SIZES,
        "Grid Size (NxN)",
        os.path.join(RESULTS_DIR, "grid_scaling", f"{EXPERIMENT_TAG}_runtime_vs_gridsize.png"),
        mode="grid_scaling"
    )
    print_summary_table(grid_only, "grid_scaling", GRID_SIZES)

    print("\n[RUNNING EXPERIMENT 2: LANDSCAPE PROPORTION SCALING]\n")
    land_only = benchmark([DEFAULT_GRID], LAND_PROPS, SEEDS)
    save_json(
        land_only,
        os.path.join(RESULTS_DIR, "landscape_prop", f"{EXPERIMENT_TAG}_landscape_prop.json"),
        {"experiment": "landscape_prop", "grid_size": DEFAULT_GRID, "cpu_count": CPU_COUNT, "seeds": SEEDS}
    )
    plot_experiment(
        land_only,
        LAND_PROPS,
        "Land Proportion",
        os.path.join(RESULTS_DIR, "landscape_prop", f"{EXPERIMENT_TAG}_runtime_vs_landprop.png"),
        mode="landscape_prop"
    )
    print_summary_table(land_only, "landscape_prop", LAND_PROPS)

    print("\n[RUNNING EXPERIMENT 3: FULL RUNTIME MATRIX]\n")
    full_matrix = benchmark(GRID_SIZES, LAND_PROPS, SEEDS)
    save_json(
        full_matrix,
        os.path.join(RESULTS_DIR, "full_matrix", f"{EXPERIMENT_TAG}_runtime_matrix.json"),
        {"experiment": "grid_x_landprop_matrix", "cpu_count": CPU_COUNT, "seeds": SEEDS}
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
