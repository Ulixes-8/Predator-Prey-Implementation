#!/usr/bin/env python3
"""
io_handlers.py

Input/output handlers for the predator-prey simulation.

This module provides functions for reading input files and generating output
files in CSV and PPM formats.

Author: s2659865
Date: April 2025
"""
import os
import numpy as np
from typing import Tuple, List

from predator_prey.utils.validation import validate_file_exists


def load_animal_file(file_path: str) -> Tuple[int, int, np.ndarray, np.ndarray]:
    """
    Load animal densities from a file.
    
    Args:
        file_path: Path to the input file
        
    Returns:
        Tuple of (width, height, mice_array, foxes_array)
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    # Validate file existence
    validate_file_exists(file_path)
    
    try:
        with open(file_path, "r") as f:
            # Read dimensions
            dimensions = f.readline().strip()
            try:
                w, h = [int(i) for i in dimensions.split()]
            except ValueError:
                raise ValueError(f"Invalid dimensions in file: {dimensions}")
            
            # Width and height including halo
            wh = w + 2
            hh = h + 2
            
            # Initialize arrays with zeros
            ms = np.zeros((hh, wh), dtype=np.float64)
            fs = np.zeros((hh, wh), dtype=np.float64)
            
            # Parse animal density values
            row = 1
            for line in f.readlines():
                if line.strip():  # Skip blank lines
                    try:
                        values = [int(i) for i in line.strip().split()]
                        
                        # Validate row length
                        if len(values) != w:
                            raise ValueError(f"Invalid row length in file: {len(values)}, expected {w}")
                        
                        # Read animals into array, padding with halo values
                        ms[row] = [0] + [i // 10 for i in values] + [0]
                        fs[row] = [0] + [i % 10 for i in values] + [0]
                        row += 1
                    except ValueError as e:
                        raise ValueError(f"Error parsing line {row}: {str(e)}")
            
            # Validate row count
            if row - 1 != h:
                raise ValueError(f"Invalid number of rows in file: {row-1}, expected {h}")
            
            return w, h, ms, fs
                
    except Exception as e:
        if isinstance(e, (FileNotFoundError, ValueError)):
            raise
        raise ValueError(f"Error reading animal file: {str(e)}")


def initialize_averages_csv() -> None:
    """
    Initialize the averages CSV file with a header.
    """
    with open("averages.csv", "w") as f:
        f.write("Timestep,Time,Mice,Foxes\n")


def append_averages_csv(timestep: int, time: float, mice_avg: float, foxes_avg: float) -> None:
    """
    Append a record to the averages CSV file.
    
    Args:
        timestep: Current time step
        time: Current simulation time
        mice_avg: Average mice density
        foxes_avg: Average foxes density
    """
    with open("averages.csv", "a") as f:
        f.write(f"{timestep},{time:.1f},{mice_avg:.17f},{foxes_avg:.17f}\n")


def generate_ppm(
    timestep: int, 
    width: int, 
    height: int, 
    landscape: np.ndarray,
    mice: np.ndarray, 
    foxes: np.ndarray, 
    mice_max: float, 
    foxes_max: float
) -> None:
    """
    Generate a PPM visualization of the current simulation state.
    
    Args:
        timestep: Current time step
        width: Width of the landscape (excluding halo)
        height: Height of the landscape (excluding halo)
        landscape: The landscape array
        mice: Mice density array
        foxes: Foxes density array
        mice_max: Maximum mice density (for scaling)
        foxes_max: Maximum foxes density (for scaling)
    """
    # Initialize color arrays
    mcols = np.zeros((height, width), dtype=np.int32)
    fcols = np.zeros((height, width), dtype=np.int32)
    
    # Calculate colors based on densities
    for x in range(1, height + 1):
        for y in range(1, width + 1):
            if landscape[x, y]:
                if mice_max != 0:
                    mcol = int((mice[x, y] / mice_max) * 255)
                else:
                    mcol = 0
                    
                if foxes_max != 0:
                    fcol = int((foxes[x, y] / foxes_max) * 255)
                else:
                    fcol = 0
                    
                mcols[x-1, y-1] = mcol
                fcols[x-1, y-1] = fcol
    
    # Write PPM file
    with open(f"map_{timestep:04d}.ppm", "w") as f:
        # Write header
        f.write(f"P3\n{width} {height}\n255\n")
        
        # Write pixel data
        for x in range(height):
            for y in range(width):
                if landscape[x+1, y+1]:
                    f.write(f"{fcols[x, y]} {mcols[x, y]} 0\n")
                else:
                    f.write("0 200 255\n")