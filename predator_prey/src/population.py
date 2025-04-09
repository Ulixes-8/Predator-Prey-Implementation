"""
Population dynamics for the predator-prey simulation.

This module implements the core equations governing the interactions
between predator and prey populations across the landscape.
"""
import numpy as np
from typing import Tuple


def initialize_populations(mice: np.ndarray, foxes: np.ndarray, landscape: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Initialize animal populations based on the landscape.
    
    Args:
        mice: Initial mice density array
        foxes: Initial foxes density array
        landscape: The landscape array
        
    Returns:
        Tuple of (mice, foxes) arrays with water cells set to zero
    """
    # Make copies to avoid modifying the input arrays
    mice_out = mice.copy()
    foxes_out = foxes.copy()
    
    # Set animal densities to zero where there is water
    water_mask = landscape == 0
    mice_out[water_mask] = 0
    foxes_out[water_mask] = 0
    
    return mice_out, foxes_out


def calculate_neighbor_sums(population: np.ndarray) -> np.ndarray:
    """
    Calculate the sum of neighbors for each cell in the population array.
    
    Args:
        population: Population density array
        
    Returns:
        Array containing the sum of neighboring cells' population values
    """
    # Get dimensions
    hh, wh = population.shape
    
    # Initialize output array
    neighbor_sums = np.zeros_like(population)
    
    # Calculate sums for the interior region [1..h, 1..w]
    neighbor_sums[1:hh-1, 1:wh-1] = (
        population[0:hh-2, 1:wh-1] +   # Top
        population[2:hh, 1:wh-1] +     # Bottom
        population[1:hh-1, 0:wh-2] +   # Left
        population[1:hh-1, 2:wh]       # Right
    )
    
    return neighbor_sums


def update_populations(
    mice: np.ndarray, 
    foxes: np.ndarray, 
    land_mask: np.ndarray,
    neighbor_counts: np.ndarray,
    r: float, a: float, k: float, 
    b: float, m: float, l: float,
    dt: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Update mice and foxes populations for one time step using vectorized operations.
    
    Args:
        mice: Current mice density array
        foxes: Current foxes density array
        land_mask: Boolean mask for land cells
        neighbor_counts: Number of land neighbors for each cell
        r: Birth rate of mice
        a: Rate at which foxes eat mice
        k: Diffusion rate of mice
        b: Birth rate of foxes
        m: Rate at which foxes starve
        l: Diffusion rate of foxes
        dt: Time step size
        
    Returns:
        Tuple of (updated_mice, updated_foxes) arrays
    """
    # Calculate neighbor sums for diffusion
    mice_neighbors = calculate_neighbor_sums(mice)
    foxes_neighbors = calculate_neighbor_sums(foxes)
    
    # Vectorized update equations
    mice_update = (r * mice) - (a * mice * foxes) + k * (mice_neighbors - (neighbor_counts * mice))
    foxes_update = (b * mice * foxes) - (m * foxes) + l * (foxes_neighbors - (neighbor_counts * foxes))
    
    # Apply updates
    mice_new = mice + dt * mice_update
    foxes_new = foxes + dt * foxes_update
    
    # Clamp negative values to zero
    mice_new[mice_new < 0] = 0
    foxes_new[foxes_new < 0] = 0
    
    # Force water cells to remain zero
    mice_new[~land_mask] = 0
    foxes_new[~land_mask] = 0
    
    return mice_new, foxes_new


def calculate_statistics(
    population: np.ndarray, 
    land_mask: np.ndarray
) -> Tuple[float, float]:
    """
    Calculate the average and maximum values of a population on land cells.
    
    Args:
        population: Population density array
        land_mask: Boolean mask for land cells
        
    Returns:
        Tuple of (average_density, maximum_density)
    """
    # Count land cells
    land_count = np.count_nonzero(land_mask)
    
    if land_count == 0:
        return 0.0, 0.0
    
    # Calculate average (only considering land cells)
    avg_density = np.sum(population) / land_count
    
    # Calculate maximum
    max_density = np.max(population)
    
    return avg_density, max_density