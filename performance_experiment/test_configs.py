"""
Test configuration definitions for the predator-prey simulation benchmarking.

This module defines all test configurations for systematically benchmarking
different versions of the predator-prey simulation code.
"""

import os
from typing import Dict, List, Any

# Get the absolute path to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Update LANDSCAPE_FILES with absolute paths
LANDSCAPE_FILES = {
    'small': os.path.join(PROJECT_ROOT, 'animals', '10x20.dat'),
    'medium': os.path.join(PROJECT_ROOT, 'animals', '20x10.dat'),
    'large': os.path.join(PROJECT_ROOT, 'animals', 'small.dat'),
    'tiny': os.path.join(PROJECT_ROOT, 'animals', '1x1.dat'),
}
# Base configuration with default parameters
BASE_CONFIG = {
    'birth_mice': 0.08,        # Birth rate of mice
    'death_mice': 0.04,        # Rate at which foxes eat mice
    'diffusion_mice': 0.2,     # Diffusion rate of mice
    'birth_foxes': 0.02,       # Birth rate of foxes
    'death_foxes': 0.06,       # Rate at which foxes starve
    'diffusion_foxes': 0.2,    # Diffusion rate of foxes
    'delta_t': 0.4,            # Time step size (seconds)
    'time_step': 10,           # Number of time steps at which to output files
    'duration': 500,           # Time to run the simulation (seconds)
    'landscape_seed': 1,       # Random seed for initialising landscape
    'landscape_prop': 0.75,    # Average proportion of landscape that will initially be land
    'landscape_smooth': 2,     # Number of smoothing passes after landscape initialisation
    'landscape_file': 'animals/20x10.dat',  # Default input file
}

def create_test_matrix() -> List[Dict[str, Any]]:
    """
    Create a comprehensive test matrix covering all parameter combinations of interest.
    
    Returns:
        List of test configuration dictionaries
    """
    test_configs = []
    
    # 1. Landscape Size Tests - varying grid dimensions
    for size_name, landscape_file in LANDSCAPE_FILES.items():
        config = BASE_CONFIG.copy()
        config.update({
            'name': f"landscape_size_{size_name}",
            'landscape_file': landscape_file,
        })
        test_configs.append(config)
    
    # 2. Landscape Composition Tests - varying land/water ratio
    landscape_proportions = [0.25, 0.5, 0.75, 1.0]
    for prop in landscape_proportions:
        config = BASE_CONFIG.copy()
        config.update({
            'name': f"land_proportion_{int(prop*100)}",
            'landscape_prop': prop,
        })
        test_configs.append(config)
    
    # 3. Simulation Duration Tests - varying runtime length
    durations = [50, 200, 500, 1000]
    for duration in durations:
        config = BASE_CONFIG.copy()
        config.update({
            'name': f"duration_{duration}",
            'duration': duration,
        })
        test_configs.append(config)
    
    # 4. Time Step Size Tests - varying dt
    delta_ts = [0.1, 0.2, 0.4, 0.8]
    for dt in delta_ts:
        config = BASE_CONFIG.copy()
        config.update({
            'name': f"timestep_{dt}",
            'delta_t': dt,
        })
        test_configs.append(config)
    
    # 5. Smoothing Level Tests - varying landscape smoothing
    smoothing_levels = [0, 2, 5, 10]
    for smooth in smoothing_levels:
        config = BASE_CONFIG.copy()
        config.update({
            'name': f"smoothing_{smooth}",
            'landscape_smooth': smooth,
        })
        test_configs.append(config)
    
    # 6. Animal Parameter Tests - varying rates
    # 6.1 Birth rate of mice
    birth_mice_rates = [0.04, 0.08, 0.12, 0.16]
    for rate in birth_mice_rates:
        config = BASE_CONFIG.copy()
        config.update({
            'name': f"birth_mice_{rate}",
            'birth_mice': rate,
        })
        test_configs.append(config)
    
    # 6.2 Death rate of mice
    death_mice_rates = [0.02, 0.04, 0.06, 0.08]
    for rate in death_mice_rates:
        config = BASE_CONFIG.copy()
        config.update({
            'name': f"death_mice_{rate}",
            'death_mice': rate,
        })
        test_configs.append(config)
    
    # 6.3 Diffusion rate of mice
    diffusion_mice_rates = [0.1, 0.2, 0.3, 0.4]
    for rate in diffusion_mice_rates:
        config = BASE_CONFIG.copy()
        config.update({
            'name': f"diffusion_mice_{rate}",
            'diffusion_mice': rate,
        })
        test_configs.append(config)
    
    # 6.4 Birth rate of foxes
    birth_foxes_rates = [0.01, 0.02, 0.03, 0.04]
    for rate in birth_foxes_rates:
        config = BASE_CONFIG.copy()
        config.update({
            'name': f"birth_foxes_{rate}",
            'birth_foxes': rate,
        })
        test_configs.append(config)
    
    # 6.5 Death rate of foxes
    death_foxes_rates = [0.03, 0.06, 0.09, 0.12]
    for rate in death_foxes_rates:
        config = BASE_CONFIG.copy()
        config.update({
            'name': f"death_foxes_{rate}",
            'death_foxes': rate,
        })
        test_configs.append(config)
    
    # 6.6 Diffusion rate of foxes
    diffusion_foxes_rates = [0.1, 0.2, 0.3, 0.4]
    for rate in diffusion_foxes_rates:
        config = BASE_CONFIG.copy()
        config.update({
            'name': f"diffusion_foxes_{rate}",
            'diffusion_foxes': rate,
        })
        test_configs.append(config)
    
    # 7. Output Frequency Tests - varying time_step
    output_frequencies = [5, 10, 20, 50]
    for freq in output_frequencies:
        config = BASE_CONFIG.copy()
        config.update({
            'name': f"output_freq_{freq}",
            'time_step': freq,
        })
        test_configs.append(config)
    
    # 8. Combined Parameter Tests - testing interactions between parameters
    # 8.1 High activity scenario (high birth/death rates)
    config = BASE_CONFIG.copy()
    config.update({
        'name': "high_activity",
        'birth_mice': 0.16,
        'death_mice': 0.08,
        'birth_foxes': 0.04,
        'death_foxes': 0.12,
    })
    test_configs.append(config)
    
    # 8.2 Low activity scenario (low birth/death rates)
    config = BASE_CONFIG.copy()
    config.update({
        'name': "low_activity",
        'birth_mice': 0.04,
        'death_mice': 0.02,
        'birth_foxes': 0.01,
        'death_foxes': 0.03,
    })
    test_configs.append(config)
    
    # 8.3 High mobility scenario (high diffusion rates)
    config = BASE_CONFIG.copy()
    config.update({
        'name': "high_mobility",
        'diffusion_mice': 0.4,
        'diffusion_foxes': 0.4,
    })
    test_configs.append(config)
    
    # 8.4 Low mobility scenario (low diffusion rates)
    config = BASE_CONFIG.copy()
    config.update({
        'name': "low_mobility",
        'diffusion_mice': 0.1,
        'diffusion_foxes': 0.1,
    })
    test_configs.append(config)
    
    # 9. Special configurations for profiling analysis
    # 9.1 Quick test for frequent profiling
    config = BASE_CONFIG.copy()
    config.update({
        'name': "quick_profile",
        'landscape_file': LANDSCAPE_FILES['small'],
        'duration': 50,
    })
    test_configs.append(config)
    
    # 9.2 Memory stress test
    config = BASE_CONFIG.copy()
    config.update({
        'name': "memory_stress",
        'landscape_file': LANDSCAPE_FILES['large'],
        'duration': 200,
    })
    test_configs.append(config)
    
    return test_configs

# Full test matrix
TEST_MATRIX = create_test_matrix()

# Simplified test subset for quicker iteration during development
QUICK_TESTS = [
    next(config for config in TEST_MATRIX if config['name'] == 'quick_profile'),
    next(config for config in TEST_MATRIX if config['name'] == 'landscape_size_tiny'),
]

# Medium test subset for more comprehensive testing
MEDIUM_TESTS = QUICK_TESTS + [
    next(config for config in TEST_MATRIX if config['name'] == 'landscape_size_small'),
    next(config for config in TEST_MATRIX if config['name'] == 'duration_50'),
    next(config for config in TEST_MATRIX if config['name'] == 'timestep_0.2'),
    next(config for config in TEST_MATRIX if config['name'] == 'high_activity'),
    next(config for config in TEST_MATRIX if config['name'] == 'low_activity'),
]

# Create a function to get a test set by name
def get_test_set(name):
    """Get a test set by name: quick, medium, full"""
    if name == 'quick':
        return QUICK_TESTS
    elif name == 'medium':
        return MEDIUM_TESTS
    elif name == 'full':
        return TEST_MATRIX
    else:
        raise ValueError(f"Unknown test set: {name}")