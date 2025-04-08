
#!/usr/bin/env python3
"""
preliminary_benchmark_runtime.py

Benchmarks the impact of varying --landscape-prop and grid size on simulation runtime,
using the default values of all other parameters. This preliminary test is designed to
identify the most significant factors affecting performance.

Author: s2659865
Date: April 2025
"""

import os
import sys
import time
import importlib
from typing import List, Tuple

# ─── Configuration ─────────────────────────────────────────────────────────────
# Directory containing .dat landscape files
LANDSCAPE_DIR = os.path.join("..", "animals")

# Grid sizes to test (width = height)
GRID_SIZES: List[int] = [10, 20, 40, 80, 160, 320]

# Proportions of landscape that should be initialized as land
LAND_PROPS: List[float] = [0.05, 0.1, 0.2, 0.4, 0.8]

# Random seeds for landscape generation
NUM_SEEDS: int = 5
LANDSCAPE_SEEDS: List[int] = [i for i in range(1, NUM_SEEDS + 1)]

# ─── Import Simulation Module ──────────────────────────────────────────────────
# Append simulation script directory to Python path
PREDATOR_PREY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "predator_prey"))
sys.path.insert(0, PREDATOR_PREY_PATH)

# Import the simulation module
simulate_predator_prey = importlib.import_module("simulate_predator_prey")

# ─── Benchmark Function ────────────────────────────────────────────────────────
def run_simulation(landscape_path: str, land_prop: float) -> float:
    """
    Runs a simulation with the specified landscape file and land proportion.
    Uses sys.argv mocking to invoke the simulate_predator_prey CLI interface.

    Args:
        landscape_path (str): Full path to the landscape .dat file.
        land_prop (float): Value of --landscape-prop to use for this run.

    Returns:
        float: Total wall-clock time in seconds using time.perf_counter().
    """
    # Replace sys.argv to simulate CLI input
    sys.argv = [
        "simulate_predator_prey.py",
        "--landscape-file", landscape_path,
        "--landscape-prop", str(land_prop)
    ]

    print(f"[INFO] Running: {os.path.basename(landscape_path)} | land-prop={land_prop:.2f}")

    # Use perf_counter for high-precision wall-clock timing
    start = time.perf_counter()
    simulate_predator_prey.simCommLineIntf()
    end = time.perf_counter()

    runtime = end - start
    print(f"[INFO] Completed in {runtime:.2f} seconds\n")
    return runtime

# ─── Sweep Benchmark ───────────────────────────────────────────────────────────
def benchmark_all() -> List[Tuple[int, float, float]]:
    """
    Runs the simulation for all combinations of grid size and landscape proportion.

    Returns:
        List[Tuple[int, float, float]]: List of (grid_size, land_prop, runtime) results.
    """
    results = []
    for size in GRID_SIZES:
        # Construct filename from grid size
        filename = f"performance_experiment_{size}x{size}.dat"
        landscape_path = os.path.join(LANDSCAPE_DIR, filename)

        # Skip missing files
        if not os.path.exists(landscape_path):
            print(f"[WARNING] Missing: {landscape_path}")
            continue

        # Test each land proportion for this grid size
        for lp in LAND_PROPS:
            runtime = run_simulation(landscape_path, lp)
            results.append((size, lp, runtime))

    return results

# ─── Results Table ─────────────────────────────────────────────────────────────
def print_results_table(results: List[Tuple[int, float, float]]) -> None:
    """
    Displays a matrix of runtimes for each grid size and land proportion.

    Args:
        results (List[Tuple[int, float, float]]): List of benchmark data.
    """
    print("\n[RESULTS] Runtime Matrix (seconds)")
    print("-" * 60)

    # Print header row with land proportions
    header = "Grid Size".ljust(12) + "".join([f"{lp:^10.2f}" for lp in LAND_PROPS])
    print(header)
    print("-" * len(header))

    # Group results by grid size
    grouped = {size: {} for size in GRID_SIZES}
    for size, lp, rt in results:
        grouped[size][lp] = rt

    # Print each row
    for size in GRID_SIZES:
        row = f"{size}x{size}".ljust(12)
        for lp in LAND_PROPS:
            rt = grouped.get(size, {}).get(lp, None)
            row += f"{rt:>10.2f}" if rt is not None else f"{'N/A':>10}"
        print(row)

# ─── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    all_results = benchmark_all()
    print_results_table(all_results)