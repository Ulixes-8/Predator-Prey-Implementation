#!/usr/bin/env python3
"""
Performance Experiment for Predator-Prey Simulation

This module provides a clean, simple framework for measuring the performance
of different versions of the predator-prey simulation code. It runs a series
of test configurations and compares execution times and speedups across
different refactoring versions.

Usage:
    python performance_experiment.py --version [version_name] --test-set [test_set]

Example:
    python performance_experiment.py --version original --test-set quick
    python performance_experiment.py --version refactor_1 --test-set comprehensive
"""

import os
import time
import argparse
import logging
import json
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Set up logging for clarity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Define test configurations
def get_test_configs(test_set: str = "quick") -> List[Dict[str, Any]]:
    """
    Get a set of test configurations based on the specified test set.
    
    Args:
        test_set: The test set to use ("quick", "medium", or "comprehensive")
        
    Returns:
        A list of test configuration dictionaries
    """
    # Base configuration with default values
    base_config = {
        "birth_mice": 0.08,         # Birth rate of mice
        "death_mice": 0.04,         # Rate at which foxes eat mice
        "diffusion_mice": 0.2,      # Diffusion rate of mice
        "birth_foxes": 0.02,        # Birth rate of foxes
        "death_foxes": 0.06,        # Rate at which foxes starve
        "diffusion_foxes": 0.2,     # Diffusion rate of foxes
        "delta_t": 0.4,             # Time step size (seconds)
        "time_step": 10,            # Number of time steps at which to output files
        "duration": 500,            # Time to run the simulation (seconds)
        "landscape_seed": 1,        # Random seed for initialising landscape
        "landscape_prop": 0.75,     # Average proportion of landscape that will initially be land
        "landscape_smooth": 2,      # Number of smoothing passes
        "landscape_file": "./animals/20x10.dat"  # Default input file
    }
    
    # Quick test set - just a few key test configurations
    if test_set == "quick":
        return [
            # Base configuration
            {**base_config, "name": "base_config"},
            
            # Small grid size
            {**base_config, "name": "small_grid", "landscape_file": "./animals/10x20.dat"},
            
            # Shorter duration
            {**base_config, "name": "short_duration", "duration": 100},
            
            # Different land proportion
            {**base_config, "name": "high_land", "landscape_prop": 0.9}
        ]
    
    # Medium test set - more comprehensive but still reasonable
    elif test_set == "medium":
        configs = []
        
        # Landscape size tests
        for size, file in [
            ("tiny", "./animals/1x1.dat"),
            ("small", "./animals/10x20.dat"),
            ("medium", "./animals/20x10.dat")
        ]:
            configs.append({
                **base_config,
                "name": f"landscape_size_{size}",
                "landscape_file": file
            })
        
        # Duration tests
        for duration in [50, 200, 500]:
            configs.append({
                **base_config,
                "name": f"duration_{duration}",
                "duration": duration
            })
        
        # Delta t tests
        for dt in [0.2, 0.4, 0.8]:
            configs.append({
                **base_config,
                "name": f"delta_t_{dt}",
                "delta_t": dt
            })
        
        # Land proportion tests
        for prop in [0.5, 0.75, 1.0]:
            configs.append({
                **base_config,
                "name": f"land_prop_{int(prop*100)}",
                "landscape_prop": prop
            })
        
        return configs
    
    # Comprehensive test set - all possible configurations
    elif test_set == "comprehensive":
        configs = []
        
        # Landscape size tests
        for size, file in [
            ("tiny", "./animals/1x1.dat"),
            ("small", "./animals/10x20.dat"),
            ("medium", "./animals/20x10.dat"),
            ("large", "./animals/small.dat")  # This is 50x50 despite the name
        ]:
            configs.append({
                **base_config,
                "name": f"landscape_size_{size}",
                "landscape_file": file
            })
        
        # Landscape proportion tests
        for prop in [0.25, 0.5, 0.75, 1.0]:
            configs.append({
                **base_config,
                "name": f"land_prop_{int(prop*100)}",
                "landscape_prop": prop
            })
        
        # Landscape smoothing tests
        for smooth in [0, 2, 5, 10]:
            configs.append({
                **base_config,
                "name": f"smoothing_{smooth}",
                "landscape_smooth": smooth
            })
        
        # Duration tests
        for duration in [50, 200, 500, 1000]:
            configs.append({
                **base_config,
                "name": f"duration_{duration}",
                "duration": duration
            })
        
        # Time step size tests
        for dt in [0.1, 0.2, 0.4, 0.8]:
            configs.append({
                **base_config,
                "name": f"delta_t_{dt}",
                "delta_t": dt
            })
        
        # Output frequency tests
        for freq in [5, 10, 20, 50]:
            configs.append({
                **base_config,
                "name": f"time_step_{freq}",
                "time_step": freq
            })
        
        # Model parameter tests - mice birth rate
        for rate in [0.04, 0.08, 0.12, 0.16]:
            configs.append({
                **base_config,
                "name": f"birth_mice_{rate}",
                "birth_mice": rate
            })
        
        # Model parameter tests - mice death rate
        for rate in [0.02, 0.04, 0.06, 0.08]:
            configs.append({
                **base_config,
                "name": f"death_mice_{rate}",
                "death_mice": rate
            })
        
        # Model parameter tests - mice diffusion rate
        for rate in [0.1, 0.2, 0.3, 0.4]:
            configs.append({
                **base_config,
                "name": f"diffusion_mice_{rate}",
                "diffusion_mice": rate
            })
        
        # Model parameter tests - foxes birth rate
        for rate in [0.01, 0.02, 0.03, 0.04]:
            configs.append({
                **base_config,
                "name": f"birth_foxes_{rate}",
                "birth_foxes": rate
            })
        
        # Model parameter tests - foxes death rate
        for rate in [0.03, 0.06, 0.09, 0.12]:
            configs.append({
                **base_config,
                "name": f"death_foxes_{rate}",
                "death_foxes": rate
            })
        
        # Model parameter tests - foxes diffusion rate
        for rate in [0.1, 0.2, 0.3, 0.4]:
            configs.append({
                **base_config,
                "name": f"diffusion_foxes_{rate}",
                "diffusion_foxes": rate
            })
        
        # Compound scenarios
        # High activity scenario
        configs.append({
            **base_config,
            "name": "high_activity",
            "birth_mice": 0.16,
            "death_mice": 0.08,
            "birth_foxes": 0.04,
            "death_foxes": 0.12
        })
        
        # Low activity scenario
        configs.append({
            **base_config,
            "name": "low_activity",
            "birth_mice": 0.04,
            "death_mice": 0.02,
            "birth_foxes": 0.01,
            "death_foxes": 0.03
        })
        
        # High mobility scenario
        configs.append({
            **base_config,
            "name": "high_mobility",
            "diffusion_mice": 0.4,
            "diffusion_foxes": 0.4
        })
        
        # Low mobility scenario
        configs.append({
            **base_config,
            "name": "low_mobility",
            "diffusion_mice": 0.1,
            "diffusion_foxes": 0.1
        })
        
        return configs
    
    # If an invalid test set is specified, raise an error
    else:
        raise ValueError(f"Invalid test set: {test_set}. Use 'quick', 'medium', or 'comprehensive'.")

class PerformanceTest:
    """
    A single performance test that measures execution time for a specific configuration.
    
    Attributes:
        name: Name of the test configuration
        config: Dictionary containing simulation parameters
        times: List of execution times for each repetition
    """
    
    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        """
        Initialize a PerformanceTest with a name and configuration.
        
        Args:
            name: Name of the test configuration
            config: Dictionary containing simulation parameters
        """
        self.name: str = name
        self.config: Dict[str, Any] = config
        self.times: List[float] = []
    
    def run(self, version_module: Any, repetitions: int = 3) -> None:
        """
        Run the test for a specified number of repetitions.
        
        Args:
            version_module: Module containing the simulation code to test
            repetitions: Number of times to repeat the test
        """
        logger.info(f"Running test '{self.name}' ({repetitions} repetitions)")
        
        for i in range(repetitions):
            start_time = time.perf_counter()
            
            # Run the simulation
            version_module.sim(
                self.config["birth_mice"],
                self.config["death_mice"],
                self.config["diffusion_mice"],
                self.config["birth_foxes"],
                self.config["death_foxes"],
                self.config["diffusion_foxes"],
                self.config["delta_t"],
                self.config["time_step"],
                self.config["duration"],
                self.config["landscape_file"],
                self.config["landscape_seed"],
                self.config["landscape_prop"],
                self.config["landscape_smooth"]
            )
            
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            self.times.append(execution_time)
            
            logger.info(f"  Repetition {i+1}: {execution_time:.4f} seconds")
        
        # Calculate statistics
        avg_time = np.mean(self.times)
        std_dev = np.std(self.times)
        logger.info(f"  Average: {avg_time:.4f} seconds (±{std_dev:.4f})")
    
    def get_average_time(self) -> float:
        """
        Calculate the average execution time for this test.
        
        Returns:
            The average execution time in seconds
        """
        if not self.times:
            return 0.0
        return np.mean(self.times)
    
    def get_std_dev(self) -> float:
        """
        Calculate the standard deviation of execution times.
        
        Returns:
            The standard deviation in seconds
        """
        if len(self.times) < 2:
            return 0.0
        return np.std(self.times)

class PerformanceExperiment:
    """
    Manages the execution of performance tests for a specific version of the code.
    
    Attributes:
        version_name: Name of the code version being tested
        version_module: Module containing the simulation code
        results_dir: Directory where results are stored
    """
    
    def __init__(self, version_name: str, version_module: Any) -> None:
        """
        Initialize a PerformanceExperiment.
        
        Args:
            version_name: Name of the code version being tested
            version_module: Module containing the simulation code
        """
        self.version_name: str = version_name
        self.version_module: Any = version_module
        
        # Create results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir: str = f"results/{version_name}_{timestamp}"
        os.makedirs(self.results_dir, exist_ok=True)
        
        logger.info(f"Performance experiment initialized for version: {version_name}")
        logger.info(f"Results will be stored in: {self.results_dir}")
    
    def run_tests(self, test_configs: List[Dict[str, Any]], repetitions: int = 3) -> Dict[str, Any]:
        """
        Run all specified test configurations.
        
        Args:
            test_configs: List of test configuration dictionaries
            repetitions: Number of repetitions for each test
            
        Returns:
            Dictionary containing test results
        """
        results = {
            "version": self.version_name,
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        logger.info(f"Running {len(test_configs)} test configurations")
        
        for config in test_configs:
            test = PerformanceTest(config["name"], config)
            test.run(self.version_module, repetitions)
            
            # Store results
            results["tests"][config["name"]] = {
                "config": config,
                "times": test.times,
                "average_time": test.get_average_time(),
                "std_dev": test.get_std_dev()
            }
            
            # Clean up any output files created by the simulation
            self._clean_output_files()
        
        # Save results to file
        self._save_results(results)
        
        return results
    
    def _clean_output_files(self) -> None:
        """Remove output files created by the simulation"""
        try:
            if os.path.exists("averages.csv"):
                os.remove("averages.csv")
            
            # Remove any PPM image files
            for file in os.listdir():
                if file.startswith("map_") and file.endswith(".ppm"):
                    os.remove(file)
        except Exception as e:
            logger.warning(f"Error cleaning output files: {e}")
    
    def _save_results(self, results: Dict[str, Any]) -> None:
        """
        Save results to a JSON file.
        
        Args:
            results: Dictionary containing test results
        """
        file_path = os.path.join(self.results_dir, "results.json")
        
        with open(file_path, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {file_path}")

def analyze_results(versions: List[str], output_dir: str = "analysis") -> None:
    """
    Analyze results from multiple versions and generate comparative visualizations.
    
    Args:
        versions: List of version names to analyze
        output_dir: Directory where analysis results will be stored
    """
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Analyzing results for versions: {versions}")
    
    # Collect results for all versions
    all_results = {}
    for version in versions:
        # Find the most recent results file for this version
        results_dirs = [d for d in os.listdir("results") if d.startswith(f"{version}_")]
        if not results_dirs:
            logger.warning(f"No results found for version: {version}")
            continue
        
        # Sort by timestamp (assuming directory names end with timestamps)
        results_dirs.sort(reverse=True)
        latest_dir = os.path.join("results", results_dirs[0])
        
        # Load results
        with open(os.path.join(latest_dir, "results.json"), "r") as f:
            all_results[version] = json.load(f)
        
        logger.info(f"Loaded results for {version} from {latest_dir}")
    
    if not all_results:
        logger.error("No results found for any version")
        return
    
    # Get the list of tests from the first version
    first_version = next(iter(all_results.values()))
    test_names = list(first_version["tests"].keys())
    
    # Generate comparison charts for each test
    for test_name in test_names:
        _generate_comparison_chart(all_results, test_name, output_dir)
    
    # Generate speedup charts
    _generate_speedup_charts(all_results, test_names, output_dir)
    
    logger.info(f"Analysis complete. Results saved to {output_dir}")

def _generate_comparison_chart(all_results: Dict[str, Dict], test_name: str, output_dir: str) -> None:
    """
    Generate a chart comparing execution times for a specific test across versions.
    
    Args:
        all_results: Dictionary containing results for all versions
        test_name: Name of the test to compare
        output_dir: Directory where the chart will be saved
    """
    versions = list(all_results.keys())
    times = []
    std_devs = []
    
    for version in versions:
        if test_name in all_results[version]["tests"]:
            times.append(all_results[version]["tests"][test_name]["average_time"])
            std_devs.append(all_results[version]["tests"][test_name]["std_dev"])
        else:
            # Skip this version if it doesn't have this test
            logger.warning(f"Test '{test_name}' not found in version {version}")
            return
    
    # Create the chart
    plt.figure(figsize=(10, 6))
    x = np.arange(len(versions))
    
    plt.bar(x, times, yerr=std_devs, capsize=5)
    plt.xticks(x, versions, rotation=45)
    plt.xlabel("Version")
    plt.ylabel("Execution Time (s)")
    plt.title(f"Execution Time Comparison - {test_name}")
    plt.tight_layout()
    
    # Save the chart
    chart_path = os.path.join(output_dir, f"comparison_{test_name}.png")
    plt.savefig(chart_path)
    plt.close()
    
    logger.info(f"Saved comparison chart for {test_name} to {chart_path}")

def _generate_speedup_charts(all_results: Dict[str, Dict], test_names: List[str], output_dir: str) -> None:
    """
    Generate charts showing speedup relative to the baseline version.
    
    Args:
        all_results: Dictionary containing results for all versions
        test_names: List of test names
        output_dir: Directory where charts will be saved
    """
    versions = list(all_results.keys())
    if len(versions) < 2:
        logger.warning("Need at least two versions to calculate speedup")
        return
    
    baseline_version = versions[0]
    speedups = {}
    
    # Calculate speedups for each test
    for test_name in test_names:
        if test_name not in all_results[baseline_version]["tests"]:
            logger.warning(f"Test '{test_name}' not found in baseline version")
            continue
        
        baseline_time = all_results[baseline_version]["tests"][test_name]["average_time"]
        speedups[test_name] = []
        
        for version in versions:
            if test_name not in all_results[version]["tests"]:
                continue
            
            time = all_results[version]["tests"][test_name]["average_time"]
            speedup = baseline_time / time if time > 0 else 0
            speedups[test_name].append(speedup)
    
    # Generate an overall speedup chart
    plt.figure(figsize=(12, 8))
    x = np.arange(len(versions))
    width = 0.8 / len(test_names)
    
    for i, test_name in enumerate(test_names):
        if test_name not in speedups:
            continue
        
        if len(speedups[test_name]) != len(versions):
            continue
        
        plt.bar(x + (i - len(test_names)/2 + 0.5) * width, 
                speedups[test_name], 
                width, 
                label=test_name)
    
    plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.7)
    plt.xlabel("Version")
    plt.ylabel("Speedup (relative to baseline)")
    plt.title("Performance Speedup by Test Configuration")
    plt.xticks(x, versions, rotation=45)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Save the chart
    chart_path = os.path.join(output_dir, "speedup_overall.png")
    plt.savefig(chart_path)
    plt.close()
    
    logger.info(f"Saved overall speedup chart to {chart_path}")
    
    # Generate individual speedup charts for each test
    for test_name in test_names:
        if test_name not in speedups or len(speedups[test_name]) != len(versions):
            continue
        
        plt.figure(figsize=(10, 6))
        plt.bar(x, speedups[test_name], width=0.6)
        plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.7)
        plt.xlabel("Version")
        plt.ylabel("Speedup (relative to baseline)")
        plt.title(f"Performance Speedup - {test_name}")
        plt.xticks(x, versions, rotation=45)
        plt.tight_layout()
        
        # Save the chart
        chart_path = os.path.join(output_dir, f"speedup_{test_name}.png")
        plt.savefig(chart_path)
        plt.close()
        
        logger.info(f"Saved speedup chart for {test_name} to {chart_path}")

def create_progressive_comparison(versions: List[str], output_dir: str = "progressive") -> None:
    """
    Create charts showing the progressive impact of each refactoring step.
    
    Args:
        versions: List of version names in order of implementation
        output_dir: Directory where charts will be saved
    """
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Creating progressive comparison for versions: {versions}")
    
    # Collect results for all versions
    all_results = {}
    for version in versions:
        # Find the most recent results file for this version
        results_dirs = [d for d in os.listdir("results") if d.startswith(f"{version}_")]
        if not results_dirs:
            logger.warning(f"No results found for version: {version}")
            continue
        
        # Sort by timestamp (assuming directory names end with timestamps)
        results_dirs.sort(reverse=True)
        latest_dir = os.path.join("results", results_dirs[0])
        
        # Load results
        with open(os.path.join(latest_dir, "results.json"), "r") as f:
            all_results[version] = json.load(f)
    
    if not all_results:
        logger.error("No results found for any version")
        return
    
    # Get the list of tests from the first version
    first_version = next(iter(all_results.values()))
    test_names = list(first_version["tests"].keys())
    
    # Generate progressive comparison charts
    for test_name in test_names:
        for i in range(2, len(versions) + 1):
            subset_versions = versions[:i]
            _generate_progressive_chart(all_results, test_name, subset_versions, output_dir)
    
    logger.info(f"Progressive comparison complete. Results saved to {output_dir}")

def _generate_progressive_chart(
    all_results: Dict[str, Dict], 
    test_name: str, 
    versions: List[str], 
    output_dir: str
) -> None:
    """
    Generate a chart showing the progressive impact of refactoring steps for a specific test.
    
    Args:
        all_results: Dictionary containing results for all versions
        test_name: Name of the test to compare
        versions: List of versions to include in the chart
        output_dir: Directory where the chart will be saved
    """
    times = []
    std_devs = []
    
    for version in versions:
        if version not in all_results or test_name not in all_results[version]["tests"]:
            logger.warning(f"Test '{test_name}' not found in version {version}")
            return
        
        times.append(all_results[version]["tests"][test_name]["average_time"])
        std_devs.append(all_results[version]["tests"][test_name]["std_dev"])
    
    # Create the chart
    plt.figure(figsize=(10, 6))
    x = np.arange(len(versions))
    
    plt.bar(x, times, yerr=std_devs, capsize=5)
    plt.xticks(x, versions, rotation=45)
    plt.xlabel("Version")
    plt.ylabel("Execution Time (s)")
    plt.title(f"Progressive Performance Improvement - {test_name}")
    plt.tight_layout()
    
    # Save the chart
    step_count = len(versions) - 1
    chart_path = os.path.join(output_dir, f"progressive_{test_name}_step{step_count}.png")
    plt.savefig(chart_path)
    plt.close()
    
    logger.info(f"Saved progressive chart for {test_name} (step {step_count}) to {chart_path}")

def main() -> None:
    """Main function to run the performance experiment"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run performance experiments for predator-prey simulation")
    parser.add_argument("--version", type=str, default="original", help="Version name (e.g., original, refactor_1)")
    parser.add_argument("--test-set", type=str, default="quick", choices=["quick", "medium", "comprehensive"], 
                        help="Test set to use (quick, medium, or comprehensive)")
    parser.add_argument("--repetitions", type=int, default=3, help="Number of repetitions for each test")
    parser.add_argument("--analyze", action="store_true", help="Analyze results instead of running tests")
    parser.add_argument("--versions", type=str, nargs="+", help="Versions to include in analysis")
    parser.add_argument("--progressive", action="store_true", help="Create progressive comparison charts")
    
    args = parser.parse_args()
    
    # If analyzing results, run analysis and exit
    if args.analyze:
        if not args.versions:
            parser.error("--analyze requires --versions")
        
        analyze_results(args.versions)
        
        if args.progressive:
            create_progressive_comparison(args.versions)
        
        return
    
    # Import the specified version module
    try:
        if args.version == "original":
            import predator_prey.simulate_predator_prey as version_module
        else:
            # Dynamically import the module based on version name
            module_path = f"predator_prey.versions.{args.version}.simulate_predator_prey"
            version_module = __import__(module_path, fromlist=["*"])
        
        logger.info(f"Successfully imported module for version: {args.version}")
    except ImportError as e:
        logger.error(f"Failed to import module for version {args.version}: {e}")
        return
    
    # Get test configurations
    test_configs = get_test_configs(args.test_set)
    logger.info(f"Using test set '{args.test_set}' with {len(test_configs)} configurations")
    
    # Run the experiment
    experiment = PerformanceExperiment(args.version, version_module)
    experiment.run_tests(test_configs, args.repetitions)
    
    logger.info("Performance experiment completed successfully")

if __name__ == "__main__":
    main()