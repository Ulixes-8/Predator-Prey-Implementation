"""
Predator-Prey Simulation Performance Benchmarking Framework

This module provides the core functionality for benchmarking different versions
of the predator-prey simulation code. It enables systematic measurement of
performance metrics across various test configurations and code versions.

Author: [Your Name]
Date: April 2025
"""

import cProfile
import pstats
import io
import time
import os
import sys
import subprocess
from typing import Dict, List, Tuple, Any, Optional, Union
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class BenchmarkSuite:
    """
    A comprehensive benchmarking framework for the predator-prey simulation.
    
    This class provides functionality to:
    - Benchmark multiple versions of the simulation code
    - Test each version with various configurations
    - Collect performance metrics (execution time, memory usage, CPU utilization)
    - Generate visualizations and comparative analyses
    
    Attributes:
        output_dir (str): Directory where benchmark results will be stored
        repetitions (int): Number of times each test is repeated for statistical validity
        results (Dict): Dictionary storing all benchmark results
        results_df (pd.DataFrame): DataFrame for analysis and visualization
    """
    
    def __init__(self, output_dir: str = "./benchmark_results", repetitions: int = 5) -> None:
        """
        Initialize the benchmark suite.
        
        Args:
            output_dir: Directory to store benchmark results
            repetitions: Number of repetitions for each test
        """
        self.output_dir = output_dir
        self.repetitions = repetitions
        self.results = {}
        self.current_version = None
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize results dataframe with appropriate columns
        self.results_df = pd.DataFrame(columns=[
            'version', 'version_desc', 'config_name', 
            'landscape_size', 'landscape_prop', 'duration',
            'delta_t', 'birth_mice', 'death_mice', 'diffusion_mice',
            'birth_foxes', 'death_foxes', 'diffusion_foxes',
            'time_step', 'landscape_smooth', 'landscape_seed',
            'execution_time', 'execution_time_std', 'memory_usage',
            'memory_usage_std', 'cpu_usage', 'cpu_usage_std'
        ])
        
        print(f"Benchmark suite initialized. Results will be stored in: {output_dir}")