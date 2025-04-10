#!/usr/bin/env python3
"""
simulation.py

Core simulation logic for the predator-prey model.

This module implements the main simulation loop and time step updates
for the predator-prey dynamics.

Author: s2659865
Date: April 2025
"""
import numpy as np
from typing import Tuple

from predator_prey.src.population import update_populations, calculate_statistics
from predator_prey.src.io_handlers import initialize_averages_csv, append_averages_csv, generate_ppm


def run_simulation(
    r: float, a: float, k: float, b: float, m: float, l: float,
    dt: float, output_steps: int, duration: int,
    width: int, height: int, mice: np.ndarray, foxes: np.ndarray,
    landscape: np.ndarray, neighbors: np.ndarray, land_mask: np.ndarray
) -> None:
    """
    Run the complete predator-prey simulation with vectorized updates.
    
    Args:
        r: Birth rate of mice
        a: Rate at which foxes eat mice
        k: Diffusion rate of mice
        b: Birth rate of foxes
        m: Rate at which foxes starve
        l: Diffusion rate of foxes
        dt: Time step size
        output_steps: Number of time steps between outputs
        duration: Total simulation duration in time units
        width: Width of the landscape (excluding halo)
        height: Height of the landscape (excluding halo)
        mice: Initial mice density array
        foxes: Initial foxes density array
        landscape: The landscape array
        neighbors: Number of land neighbors for each cell
        land_mask: Boolean mask for land cells
    """
    # Create working copies of the population arrays
    ms = mice.copy()
    fs = foxes.copy()
    ms_nu = ms.copy()
    fs_nu = fs.copy()
    
    # Count land cells for calculating averages
    land_count = np.count_nonzero(land_mask)
    
    # Calculate initial averages
    if land_count != 0:
        mice_avg = np.sum(ms) / land_count
        foxes_avg = np.sum(fs) / land_count
    else:
        mice_avg = 0
        foxes_avg = 0
    
    # Initialize the averages CSV file
    initialize_averages_csv()
    
    # Calculate the total number of time steps
    total_steps = int(duration / dt)
    
    # Main simulation loop
    for i in range(total_steps):
        # Output data at specified intervals
        if i % output_steps == 0:
            # Calculate maximum population values for scaling
            mice_max = np.max(ms)
            foxes_max = np.max(fs)
            
            # Calculate average populations
            if land_count != 0:
                mice_avg = np.sum(ms) / land_count
                foxes_avg = np.sum(fs) / land_count
            else:
                mice_avg = 0
                foxes_avg = 0
            
            # Append to averages CSV
            append_averages_csv(i, i * dt, mice_avg, foxes_avg)
            
            # Generate PPM visualization
            generate_ppm(i, width, height, landscape, ms, fs, mice_max, foxes_max)
        
        # Update populations for this time step
        ms_nu, fs_nu = update_populations(
            ms, fs, land_mask, neighbors,
            r, a, k, b, m, l, dt
        )
        
        # Swap arrays for next iteration
        ms, ms_nu = ms_nu, ms
        fs, fs_nu = fs_nu, fs