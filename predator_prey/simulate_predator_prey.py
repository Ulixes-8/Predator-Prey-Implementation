"""
Predator-prey simulation. Foxes and mice.

Version 4.0, last updated in January 2025.

This module implements a simulation of the interaction between foxes (predators)
and field mice (prey) in a two-dimensional landscape. The simulation is based on
partial differential equations that model birth, death, and diffusion processes.
"""
from argparse import ArgumentParser
import numpy as np
import random
import time
from typing import Tuple

from predator_prey.utils.validation import validate_simulation_parameters, validate_file_exists
from predator_prey.src.landscape import generate_landscape, smooth_landscape, calculate_neighbors, create_land_mask
from predator_prey.src.population import initialize_populations
from predator_prey.src.io_handlers import load_animal_file
from predator_prey.src.simulation import run_simulation


def getVersion():
    """Return the version number of the simulation."""
    return 4.0


def simCommLineIntf():
    """
    Command-line interface for the predator-prey simulation.
    
    This function parses command-line arguments and calls the main simulation
    function with the parsed parameters.
    """
    par = ArgumentParser()
    par.add_argument("-r", "--birth-mice", type=float, default=0.1, help="Birth rate of mice")
    par.add_argument("-a", "--death-mice", type=float, default=0.05, help="Rate at which foxes eat mice")
    par.add_argument("-k", "--diffusion-mice", type=float, default=0.2, help="Diffusion rate of mice")
    par.add_argument("-b", "--birth-foxes", type=float, default=0.03, help="Birth rate of foxes")
    par.add_argument("-m", "--death-foxes", type=float, default=0.09, help="Rate at which foxes starve")
    par.add_argument("-l", "--diffusion-foxes", type=float, default=0.2, help="Diffusion rate of foxes")
    par.add_argument("-dt", "--delta-t", type=float, default=0.5, help="Time step size")
    par.add_argument("-t", "--time_step", type=int, default=10, help="Number of time steps at which to output files")
    par.add_argument("-d", "--duration", type=int, default=500, help="Time to run the simulation (in timesteps)")
    par.add_argument("-ls", "--landscape-seed", type=int, default=1, help="Random seed for initialising landscape")
    par.add_argument("-lp", "--landscape-prop", type=float, default=0.75, help="Average proportion of landscape that will initially be land")
    par.add_argument("-lsm", "--landscape-smooth", type=int, default=2, help="Number of smoothing passes after landscape initialisation")
    par.add_argument("-f", "--landscape-file", type=str, required=True,
                    help="Input landscape file")
    args = par.parse_args()
    
    sim(args.birth_mice, args.death_mice, args.diffusion_mice, 
        args.birth_foxes, args.death_foxes, args.diffusion_foxes,
        args.delta_t, args.time_step, args.duration, args.landscape_file,
        args.landscape_seed, args.landscape_prop, args.landscape_smooth)


def sim(r, a, k, b, m, l, dt, t, d, lfile, lseed, lp, lsm):
    """
    Run the predator-prey simulation with the given parameters.
    
    Args:
        r: Birth rate of mice
        a: Rate at which foxes eat mice
        k: Diffusion rate of mice
        b: Birth rate of foxes
        m: Rate at which foxes starve
        l: Diffusion rate of foxes
        dt: Time step size
        t: Number of time steps at which to output files
        d: Duration of the simulation
        lfile: Path to the landscape file
        lseed: Random seed for landscape generation
        lp: Proportion of landscape that is land
        lsm: Number of smoothing passes
    """
    print("Predator-prey simulation", getVersion())
    
    # Validate parameters
    try:
        validate_simulation_parameters(r, a, k, b, m, l, dt, t, d, lseed, lp, lsm)
        validate_file_exists(lfile)
    except (ValueError, FileNotFoundError, PermissionError) as e:
        print(f"Error: {str(e)}")
        return
    
    try:
        # Load animal file
        width, height, mice, foxes = load_animal_file(lfile)
        print(f"Width: {width} Height: {height}")
        
        # Generate landscape
        landscape = generate_landscape(width, height, lseed, lp)
        
        # Apply smoothing
        landscape = smooth_landscape(landscape, lsm)
        
        # Initialize populations
        mice, foxes = initialize_populations(mice, foxes, landscape)
        
        # Calculate land neighbors
        neighbors = calculate_neighbors(landscape)
        
        # Create land mask
        land_mask = create_land_mask(landscape)
        
        # Count land cells
        land_count = np.count_nonzero(land_mask)
        print(f"Number of land-only squares: {land_count}")
        
        # Run the simulation
        run_simulation(r, a, k, b, m, l, dt, t, d, width, height, mice, foxes, 
                      landscape, neighbors, land_mask)
                      
    except Exception as e:
        print(f"Error during simulation: {str(e)}")


if __name__ == "__main__":
    simCommLineIntf()