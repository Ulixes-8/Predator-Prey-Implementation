"""
Landscape generation and management for the predator-prey simulation.

This module provides functions for creating and manipulating the landscape
in which the predator-prey simulation takes place.
"""
import random
import numpy as np
from typing import Tuple


def generate_landscape(width: int, height: int, seed: int, land_proportion: float) -> np.ndarray:
    """
    Generate a random landscape with land and water.
    
    Args:
        width: Width of the landscape (excluding halo)
        height: Height of the landscape (excluding halo)
        seed: Random seed for repeatability
        land_proportion: Proportion of the landscape that should be land (0-1)
        
    Returns:
        2D NumPy array representing the landscape, where 1 is land and 0 is water
        The array includes a halo of water cells around the edges.
    """
    # Width and height including halo
    wh = width + 2
    hh = height + 2
    
    # Initialize landscape with zeros (all water)
    lscape = np.zeros((hh, wh), dtype=np.int32)
    
    # Seed the random number generator for repeatability
    random.seed(seed)
    
    # Generate random landscape based on land proportion
    for x in range(1, height + 1):
        for y in range(1, width + 1):
            prop = random.random()
            if prop <= land_proportion:
                lscape[x, y] = 1
                
    return lscape


def smooth_landscape(landscape: np.ndarray, smooth_passes: int) -> np.ndarray:
    """
    Apply smoothing to make the landscape more realistic.
    
    This function changes any land cells mostly surrounded by water into water cells,
    and vice versa, to reduce the number of isolated cells.
    
    Args:
        landscape: The landscape array to smooth
        smooth_passes: Number of smoothing iterations to perform
        
    Returns:
        Smoothed landscape array
    """
    # Make a copy to avoid modifying the input
    lscape = landscape.copy()
    
    # Get dimensions
    hh, wh = lscape.shape
    h, w = hh - 2, wh - 2
    
    # Apply smoothing passes
    for _ in range(smooth_passes):
        for i in range(1, h + 1):
            for j in range(1, w + 1):
                # Calculate sum of this cell and its neighbors
                nbr_sum = (lscape[i, j] + 
                          lscape[i-1, j] + lscape[i+1, j] + 
                          lscape[i, j-1] + lscape[i, j+1])
                
                # If mostly water, make it water
                if nbr_sum < 2:
                    lscape[i, j] = 0
                # If mostly land, make it land
                if nbr_sum > 2:
                    lscape[i, j] = 1
    
    return lscape


def calculate_neighbors(landscape: np.ndarray) -> np.ndarray:
    """
    Calculate the number of land neighbors for each cell.
    
    Args:
        landscape: The landscape array
        
    Returns:
        Array containing the number of land neighbors for each cell
    """
    # Get dimensions
    hh, wh = landscape.shape
    
    # Initialize neighbors array
    neighbors = np.zeros((hh, wh), dtype=np.int32)
    
    # Calculate number of land neighbors
    for x in range(1, hh - 1):
        for y in range(1, wh - 1):
            neighbors[x, y] = (landscape[x-1, y] + 
                              landscape[x+1, y] + 
                              landscape[x, y-1] + 
                              landscape[x, y+1])
    
    return neighbors


def create_land_mask(landscape: np.ndarray) -> np.ndarray:
    """
    Create a boolean mask for land cells.
    
    Args:
        landscape: The landscape array
        
    Returns:
        Boolean array where True indicates land
    """
    return landscape == 1