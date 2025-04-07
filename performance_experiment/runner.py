"""
Main runner script for the predator-prey simulation performance experiments.

This module provides the main entry point for running the performance
experiments, orchestrating the benchmarking of different code versions
and configurations.
"""

import argparse
import os
import sys
import importlib
import pandas as pd
from typing import List, Dict, Any, Optional, Union
import time

from performance_experiment.benchmark import BenchmarkSuite
from performance_experiment.test_configs import get_test_set
from performance_experiment.utils import ensure_dir_exists
from performance_experiment.visualize import generate_all_visualizations

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run performance experiments for predator-prey simulation."
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./benchmark_results",
        help="Directory to store benchmark results (default: ./benchmark_results)"
    )
    
    parser.add_argument(
        "--repetitions",
        type=int,
        default=5,
        help="Number of repetitions for each benchmark (default: 5)"
    )
    
    parser.add_argument(
        "--test-set",
        type=str,
        choices=["quick", "medium", "full"],
        default="quick",
        help="Test set to use (default: quick)"
    )
    
    parser.add_argument(
        "--versions",
        type=str,
        nargs="+",
        default=["original"],
        help="Code versions to benchmark (default: original)"
    )
    
    parser.add_argument(
        "--module",
        type=str,
        default="predator_prey.simulate_predator_prey",
        help="Module path to import (default: predator_prey.simulate_predator_prey)"
    )
    
    parser.add_argument(
        "--description",
        type=str,
        default="Original implementation",
        help="Description of the code version (used in reports)"
    )
    
    parser.add_argument(
        "--visualize-only",
        action="store_true",
        help="Only generate visualizations from existing results"
    )
    
    return parser.parse_args()

def get_module_path(version: str) -> str:
    """
    Get the module path for a specific version.
    
    Args:
        version: Version name
        
    Returns:
        Module path for the specified version
    """
    # For now, we only have the original version
    if version == "original":
        return "predator_prey.simulate_predator_prey"
    else:
        # In the future, we'll have different versions in different modules
        return f"predator_prey.versions.{version}.simulate_predator_prey"

def main():
    """Main entry point."""
    args = parse_args()
    
    # Ensure output directory exists
    ensure_dir_exists(args.output_dir)
    
    # If only visualizing, load existing results and generate visualizations
    if args.visualize_only:
        results_file = os.path.join(args.output_dir, "results.csv")
        if not os.path.exists(results_file):
            print(f"Error: Results file not found: {results_file}")
            print("Please run the benchmarks first or specify a different output directory.")
            sys.exit(1)
        
        results_df = pd.read_csv(results_file)
        generate_all_visualizations(results_df, os.path.join(args.output_dir, "visualizations"))
        sys.exit(0)
    
    # Create benchmark suite
    benchmark = BenchmarkSuite(
        output_dir=args.output_dir,
        repetitions=args.repetitions
    )
    
    # Get test configurations
    print(f"Using test set: {args.test_set}")
    test_configs = get_test_set(args.test_set)
    print(f"Number of test configurations: {len(test_configs)}")
    
    # Benchmark each version
    for version in args.versions:
        version_name = version
        version_desc = args.description
        version_module = args.module
        
        print(f"Benchmarking version: {version_name} - {version_desc}")
        print(f"Module: {version_module}")
        
        # Run benchmarks for this version
        benchmark.benchmark_version(
            version_name=version_name,
            version_desc=version_desc,
            version_module_path=version_module,
            test_configs=test_configs
        )
    
    # Generate visualizations
    print("Generating visualizations...")
    generate_all_visualizations(
        benchmark.results_df,
        os.path.join(args.output_dir, "visualizations")
    )
    
    # Save results
    print("Saving results...")
    benchmark.save_results()
    
    print(f"All benchmarks completed. Results saved to {args.output_dir}")

if __name__ == "__main__":
    main()