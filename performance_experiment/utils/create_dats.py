#!/usr/bin/env python3
"""
create_dats.py

Generates `.dat` landscape files for predator-prey simulation experiments.
Each file represents a grid of a given size, where every cell is initialized
with a fixed encoded value (default: 21 = 2 mice and 1 fox).

Output files are saved in: ../animals/
Filenames follow the pattern:
    performance_experiment_<width>x<height>.dat

Author: s2659865
Date: April 2025
"""

import os
from typing import List

# ─── Output Configuration ──────────────────────────────────────────────────────
# Directory where generated .dat files will be stored
# Using relative path from the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "animals")

# ─── File Generator Function ───────────────────────────────────────────────────
def create_performance_dat_file(width: int, height: int, value: int = 21) -> None:
    """
    Creates a .dat file in the output directory with a uniform value for all cells.

    Args:
        width (int): Number of columns in the grid.
        height (int): Number of rows in the grid.
        value (int): Encoded integer value for each cell (default is 21, representing 2 mice and 1 fox).
    """
    # Ensure the target output directory exists (create if missing)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Construct the filename based on the grid dimensions
    filename = f"performance_experiment_{width}x{height}.dat"
    filepath = os.path.join(OUTPUT_DIR, filename)

    try:
        with open(filepath, "w") as f:
            # Write the first line: the grid size (header)
            f.write(f"{width} {height}\n")

            # Generate one row string with all cells having the same value
            row_data = " ".join([str(value)] * width)

            # Write that row for each row in the grid
            for _ in range(height):
                f.write(f"{row_data}\n")

        print(f"[INFO] Created: {filepath}")

    except IOError as e:
        # Handle potential disk write or file permission errors
        print(f"[ERROR] Failed to write file {filepath}: {e}")

# ─── Bulk File Generation ──────────────────────────────────────────────────────
def generate_all_landscapes(grid_sizes: List[int], default_value: int = 21) -> None:
    """
    Generates multiple .dat landscape files for various grid sizes.

    Args:
        grid_sizes (List[int]): List of square grid dimensions (e.g., [10, 20, 40]).
        default_value (int): Value assigned to every cell in each grid (default: 21).
    """
    print(f"[INFO] Generating landscape files in: {OUTPUT_DIR}\n")

    # Loop through each grid size and generate a corresponding landscape file
    for size in grid_sizes:
        create_performance_dat_file(width=size, height=size, value=default_value)

    print("\n[INFO] All landscape files generated successfully.")

# ─── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Define the grid sizes to generate
    GRID_SIZES = [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5120]

    # Launch the file generation process
    generate_all_landscapes(grid_sizes=GRID_SIZES)