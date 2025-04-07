#!/usr/bin/env python3
"""
Module: testing_configs.py
Description:
    This module defines test configurations for the predator-prey simulation
    performance experiments. It extracts default values directly from the
    simulation code to ensure consistency.
    
    The module provides predefined test sets of varying complexity for measuring
    the impact of code refactoring.
"""

import os
import json
import logging
import importlib
from typing import Dict, List, Any
from argparse import ArgumentParser

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Function to get defaults from the simulation code
def get_simulation_defaults() -> Dict[str, Any]:
    """
    Extract default parameter values directly from the simulation code.
    
    Returns:
        Dictionary with default parameter values
    """
    try:
        # Import the simulation module
        from predator_prey.simulate_predator_prey import simCommLineIntf
        
        # Create a parser to extract default values
        parser = ArgumentParser()
        # Call the function that sets up the argument parser
        simCommLineIntf.__globals__['ArgumentParser'] = lambda: parser
        simCommLineIntf()
        
        # Extract default values from parser
        defaults = {}
        for action in parser._actions:
            if action.dest != 'help' and action.default is not None:
                defaults[action.dest] = action.default
        
        logger.info("Successfully extracted defaults from simulation code")
        return defaults
    
    except (ImportError, AttributeError) as e:
        logger.warning(f"Could not extract defaults from simulation code: {e}")
        logger.warning("Using hardcoded defaults instead")
        
        # Return hardcoded defaults based on the simulation code
        return {
            "birth_mice": 0.1,
            "death_mice": 0.05,
            "diffusion_mice": 0.2,
            "birth_foxes": 0.03,
            "death_foxes": 0.09,
            "diffusion_foxes": 0.2,
            "delta_t": 0.5,
            "time_step": 10,
            "duration": 500,
            "landscape_seed": 1,
            "landscape_prop": 0.75,
            "landscape_smooth": 2
        }

# Define landscape files
def get_landscape_files() -> Dict[str, str]:
    """
    Get a dictionary mapping landscape size names to file paths.
    This function handles different possible locations of animal files.
    
    Returns:
        Dictionary mapping size names to file paths
    """
    # Try different potential locations for the animal files
    potential_animal_dirs = [
        "animals",  # Current directory
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "animals"),  # Same directory as this script
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "animals"),  # Parent directory
    ]
    
    for animals_dir in potential_animal_dirs:
        if os.path.exists(animals_dir):
            logger.info(f"Found animals directory at {animals_dir}")
            return {
                "tiny": os.path.join(animals_dir, "1x1.dat"),
                "small": os.path.join(animals_dir, "10x20.dat"),
                "medium": os.path.join(animals_dir, "20x10.dat"),
                "large": os.path.join(animals_dir, "small.dat")  # 50x50 grid, despite the name
            }
    
    # If no directory is found, use relative paths and log a warning
    logger.warning("Could not find animals directory, using relative paths")
    return {
        "tiny": "animals/1x1.dat",
        "small": "animals/10x20.dat",
        "medium": "animals/20x10.dat",
        "large": "animals/small.dat"
    }

# Get landscape file paths
LANDSCAPE_FILES = get_landscape_files()

# Get defaults from simulation code
SIM_DEFAULTS = get_simulation_defaults()

# Base configuration with default parameters from simulation code
BASE_CONFIG = {
    "birth_mice": SIM_DEFAULTS.get("birth_mice", 0.1),
    "death_mice": SIM_DEFAULTS.get("death_mice", 0.05),
    "diffusion_mice": SIM_DEFAULTS.get("diffusion_mice", 0.2),
    "birth_foxes": SIM_DEFAULTS.get("birth_foxes", 0.03),
    "death_foxes": SIM_DEFAULTS.get("death_foxes", 0.09),
    "diffusion_foxes": SIM_DEFAULTS.get("diffusion_foxes", 0.2),
    "delta_t": SIM_DEFAULTS.get("delta_t", 0.5),
    "time_step": SIM_DEFAULTS.get("time_step", 10),
    "duration": SIM_DEFAULTS.get("duration", 500),
    "landscape_seed": SIM_DEFAULTS.get("landscape_seed", 1),
    "landscape_prop": SIM_DEFAULTS.get("landscape_prop", 0.75),
    "landscape_smooth": SIM_DEFAULTS.get("landscape_smooth", 2),
    "landscape_file": LANDSCAPE_FILES["medium"],  # Default input file
    "name": "base_config"      # Test configuration name
}

def create_test_matrix(test_set: str = "comprehensive") -> List[Dict[str, Any]]:
    """
    Create a test matrix of configurations based on the specified test set.
    
    Args:
        test_set: Level of testing to perform ("quick", "medium", or "comprehensive")
        
    Returns:
        List of configuration dictionaries for testing
    """
    test_configs = []
    
    # Quick test set - just a few configurations for fast feedback
    if test_set == "quick":
        # Add base configuration
        test_configs.append(BASE_CONFIG.copy())
        
        # Add a small landscape test
        small_config = BASE_CONFIG.copy()
        small_config.update({
            "name": "landscape_size_small",
            "landscape_file": LANDSCAPE_FILES["small"]
        })
        test_configs.append(small_config)
        
        # Add a short duration test
        short_config = BASE_CONFIG.copy()
        short_config.update({
            "name": "short_duration",
            "duration": 100
        })
        test_configs.append(short_config)
        
        # Add a different land proportion test
        land_config = BASE_CONFIG.copy()
        land_config.update({
            "name": "high_land",
            "landscape_prop": 0.9
        })
        test_configs.append(land_config)
        
        return test_configs
    
    # Medium test set - more comprehensive but still reasonably quick
    elif test_set == "medium":
        # Start with the quick test set
        test_configs = create_test_matrix("quick")
        
        # Add landscape size tests
        for size, file_path in [("tiny", LANDSCAPE_FILES["tiny"]), 
                              ("medium", LANDSCAPE_FILES["medium"])]:
            if size != "small":  # Small is already in the quick set
                config = BASE_CONFIG.copy()
                config.update({
                    "name": f"landscape_size_{size}",
                    "landscape_file": file_path
                })
                test_configs.append(config)
        
        # Add time step tests
        for dt in [0.2, 0.8]:
            config = BASE_CONFIG.copy()
            config.update({
                "name": f"delta_t_{dt}",
                "delta_t": dt
            })
            test_configs.append(config)
        
        # Add animal parameter tests
        for param, values in {
            "birth_mice": [BASE_CONFIG["birth_mice"] * 0.5, BASE_CONFIG["birth_mice"] * 1.5],
            "death_mice": [BASE_CONFIG["death_mice"] * 0.5, BASE_CONFIG["death_mice"] * 1.5],
            "birth_foxes": [BASE_CONFIG["birth_foxes"] * 0.5, BASE_CONFIG["birth_foxes"] * 1.5],
            "death_foxes": [BASE_CONFIG["death_foxes"] * 0.5, BASE_CONFIG["death_foxes"] * 1.5],
        }.items():
            for value in values:
                config = BASE_CONFIG.copy()
                config.update({
                    "name": f"{param}_{value}",
                    param: value
                })
                test_configs.append(config)
        
        return test_configs
    
    # Comprehensive test set - full range of parameter variations
    elif test_set == "comprehensive":
        # Add base configuration
        test_configs.append(BASE_CONFIG.copy())
        
        # 1. Landscape Size Tests
        for size, file_path in LANDSCAPE_FILES.items():
            config = BASE_CONFIG.copy()
            config.update({
                "name": f"landscape_size_{size}",
                "landscape_file": file_path
            })
            test_configs.append(config)
        
        # 2. Landscape Composition Tests (varying proportion of land)
        for prop in [0.25, 0.5, 0.75, 1.0]:
            config = BASE_CONFIG.copy()
            config.update({
                "name": f"land_proportion_{int(prop * 100)}",
                "landscape_prop": prop
            })
            test_configs.append(config)
        
        # 3. Landscape Smoothing Tests
        for smooth in [0, 2, 5, 10]:
            config = BASE_CONFIG.copy()
            config.update({
                "name": f"landscape_smooth_{smooth}",
                "landscape_smooth": smooth
            })
            test_configs.append(config)
        
        # 4. Simulation Duration Tests
        for duration in [50, 200, 500, 1000]:
            config = BASE_CONFIG.copy()
            config.update({
                "name": f"duration_{duration}",
                "duration": duration
            })
            test_configs.append(config)
        
        # 5. Time Step Size Tests
        base_dt = BASE_CONFIG["delta_t"]
        for dt in [base_dt*0.2, base_dt*0.5, base_dt, base_dt*1.5]:
            config = BASE_CONFIG.copy()
            config.update({
                "name": f"delta_t_{dt}",
                "delta_t": dt
            })
            test_configs.append(config)
        
        # 6. Output Frequency Tests
        for freq in [5, 10, 20, 50]:
            config = BASE_CONFIG.copy()
            config.update({
                "name": f"time_step_{freq}",
                "time_step": freq
            })
            test_configs.append(config)
        
        # 7. Model Parameter Tests: Mice Birth Rate
        base_birth_mice = BASE_CONFIG["birth_mice"]
        for factor in [0.4, 0.7, 1.0, 1.3, 1.6]:
            rate = base_birth_mice * factor
            config = BASE_CONFIG.copy()
            config.update({
                "name": f"birth_mice_{rate:.3f}",
                "birth_mice": rate
            })
            test_configs.append(config)
        
        # 8. Model Parameter Tests: Mice Death Rate
        base_death_mice = BASE_CONFIG["death_mice"]
        for factor in [0.4, 0.7, 1.0, 1.3, 1.6]:
            rate = base_death_mice * factor
            config = BASE_CONFIG.copy()
            config.update({
                "name": f"death_mice_{rate:.3f}",
                "death_mice": rate
            })
            test_configs.append(config)
        
        # 9. Model Parameter Tests: Mice Diffusion Rate
        base_diff_mice = BASE_CONFIG["diffusion_mice"]
        for factor in [0.5, 1.0, 1.5, 2.0]:
            rate = base_diff_mice * factor
            config = BASE_CONFIG.copy()
            config.update({
                "name": f"diffusion_mice_{rate:.2f}",
                "diffusion_mice": rate
            })
            test_configs.append(config)
        
        # 10. Model Parameter Tests: Foxes Birth Rate
        base_birth_foxes = BASE_CONFIG["birth_foxes"]
        for factor in [0.4, 0.7, 1.0, 1.3, 1.6]:
            rate = base_birth_foxes * factor
            config = BASE_CONFIG.copy()
            config.update({
                "name": f"birth_foxes_{rate:.3f}",
                "birth_foxes": rate
            })
            test_configs.append(config)
        
        # 11. Model Parameter Tests: Foxes Death Rate
        base_death_foxes = BASE_CONFIG["death_foxes"]
        for factor in [0.4, 0.7, 1.0, 1.3, 1.6]:
            rate = base_death_foxes * factor
            config = BASE_CONFIG.copy()
            config.update({
                "name": f"death_foxes_{rate:.3f}",
                "death_foxes": rate
            })
            test_configs.append(config)
        
        # 12. Model Parameter Tests: Foxes Diffusion Rate
        base_diff_foxes = BASE_CONFIG["diffusion_foxes"]
        for factor in [0.5, 1.0, 1.5, 2.0]:
            rate = base_diff_foxes * factor
            config = BASE_CONFIG.copy()
            config.update({
                "name": f"diffusion_foxes_{rate:.2f}",
                "diffusion_foxes": rate
            })
            test_configs.append(config)
        
        # 13. Compound Scenarios
        # 13.1 High Activity: High birth and death rates for both species
        config = BASE_CONFIG.copy()
        config.update({
            "name": "high_activity",
            "birth_mice": BASE_CONFIG["birth_mice"] * 1.6,
            "death_mice": BASE_CONFIG["death_mice"] * 1.6,
            "birth_foxes": BASE_CONFIG["birth_foxes"] * 1.3,
            "death_foxes": BASE_CONFIG["death_foxes"] * 1.3
        })
        test_configs.append(config)
        
        # 13.2 Low Activity: Low birth and death rates for both species
        config = BASE_CONFIG.copy()
        config.update({
            "name": "low_activity",
            "birth_mice": BASE_CONFIG["birth_mice"] * 0.4,
            "death_mice": BASE_CONFIG["death_mice"] * 0.4,
            "birth_foxes": BASE_CONFIG["birth_foxes"] * 0.4,
            "death_foxes": BASE_CONFIG["death_foxes"] * 0.4
        })
        test_configs.append(config)
        
        # 13.3 High Mobility: High diffusion rates for both species
        config = BASE_CONFIG.copy()
        config.update({
            "name": "high_mobility",
            "diffusion_mice": BASE_CONFIG["diffusion_mice"] * 2.0,
            "diffusion_foxes": BASE_CONFIG["diffusion_foxes"] * 2.0
        })
        test_configs.append(config)
        
        # 13.4 Low Mobility: Low diffusion rates for both species
        config = BASE_CONFIG.copy()
        config.update({
            "name": "low_mobility",
            "diffusion_mice": BASE_CONFIG["diffusion_mice"] * 0.5,
            "diffusion_foxes": BASE_CONFIG["diffusion_foxes"] * 0.5
        })
        test_configs.append(config)
        
        # 13.5 Quick Profile: Small landscape with short duration
        config = BASE_CONFIG.copy()
        config.update({
            "name": "quick_profile",
            "duration": 50,
            "landscape_file": LANDSCAPE_FILES["tiny"]
        })
        test_configs.append(config)
        
        # 13.6 Memory Stress: Large landscape with extended duration
        config = BASE_CONFIG.copy()
        config.update({
            "name": "memory_stress",
            "duration": 200,
            "landscape_file": LANDSCAPE_FILES["large"]
        })
        test_configs.append(config)
        
        return test_configs
    
    else:
        raise ValueError(f"Invalid test set: {test_set}. Use 'quick', 'medium', or 'comprehensive'.")

def print_test_summary(test_configs: List[Dict[str, Any]]) -> None:
    """
    Print a summary of the test configurations.
    
    Args:
        test_configs: List of test configurations
    """
    print(f"Generated {len(test_configs)} test configurations:")
    for i, config in enumerate(test_configs):
        print(f"  {i+1}. {config['name']}")

if __name__ == "__main__":
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate test configurations for predator-prey simulation")
    parser.add_argument("--test-set", type=str, default="comprehensive", 
                        choices=["quick", "medium", "comprehensive"], 
                        help="Test set to generate (quick, medium, or comprehensive)")
    parser.add_argument("--output", type=str, help="Output file for test configurations (JSON format)")
    parser.add_argument("--show-defaults", action="store_true", help="Display the default configuration values")
    
    args = parser.parse_args()
    
    # Show defaults if requested
    if args.show_defaults:
        print("Default configuration values (extracted from simulation code):")
        for key, value in SIM_DEFAULTS.items():
            print(f"  {key}: {value}")
        print()
    
    # Generate test configurations
    test_configs = create_test_matrix(args.test_set)
    
    # Print summary
    print_test_summary(test_configs)
    
    # Save to file if specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(test_configs, f, indent=2)
        print(f"Test configurations saved to {args.output}")