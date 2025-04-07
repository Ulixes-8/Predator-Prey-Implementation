"""
Predator-Prey Simulation Performance Benchmarking Framework

This module provides the core functionality for benchmarking different versions
of the predator-prey simulation code. It enables systematic measurement of
performance metrics across various test configurations and code versions.
"""

import cProfile
import pstats
import io
import time
import os
import sys
import subprocess
import pickle
import importlib
from typing import Dict, List, Tuple, Any, Optional, Union
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shutil
import tempfile

from performance_experiment.utils import ensure_dir_exists, compute_statistics, detect_outliers

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
        ensure_dir_exists(output_dir)
        
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
        
    def benchmark_version(self, 
                        version_name: str, 
                        version_desc: str,
                        version_module_path: str,
                        test_configs: List[Dict[str, Any]]) -> None:
        """
        Benchmark a specific version of the code across all test configurations.
        
        Args:
            version_name: Identifier for the code version
            version_desc: Description of the code version
            version_module_path: Path to the Python module containing the code
            test_configs: List of test configurations
        """
        self.current_version = {
            'name': version_name,
            'desc': version_desc,
            'module_path': version_module_path,
            'results': {}
        }
        
        print(f"Benchmarking version: {version_name} - {version_desc}")
        print(f"Module path: {version_module_path}")
        
        # Create version directory
        version_dir = os.path.join(self.output_dir, version_name)
        ensure_dir_exists(version_dir)
        
        # Run benchmarks for each configuration
        for config in test_configs:
            self._run_benchmark_for_config(config)
            
        # Save this version's results
        with open(os.path.join(version_dir, 'results.pkl'), 'wb') as f:
            pickle.dump(self.current_version, f)
            
        # Update overall results dictionary
        self.results[version_name] = self.current_version
        
        print(f"Benchmarking completed for version: {version_name}")


    def _measure_cpu_usage(self, cmd: List[str]) -> float:
        """
        Estimate CPU usage percentage of a command.
        
        Args:
            cmd: Command to execute as a list of strings
        
        Returns:
            Estimated CPU usage percentage
        """
        try:
            import psutil
            import time
            
            # Measure CPU usage using subprocess
            start_time = time.time()
            start_cpu_time = time.process_time()
            
            # Run the command
            subprocess.run(cmd, check=True)
            
            # Calculate times
            end_time = time.time()
            end_cpu_time = time.process_time()
            
            # Calculate CPU usage
            wall_time = end_time - start_time
            cpu_time = end_cpu_time - start_cpu_time
            
            # Estimate CPU usage as percentage
            if wall_time > 0:
                return (cpu_time / wall_time) * 100
            return 0.0
        
        except ImportError:
            print("Warning: psutil not available. Falling back to simple CPU time measurement.")
            start_time = time.time()
            start_cpu_time = time.process_time()
            
            subprocess.run(cmd, check=True)
            
            end_time = time.time()
            end_cpu_time = time.process_time()
            
            wall_time = end_time - start_time
            cpu_time = end_cpu_time - start_cpu_time
            
            if wall_time > 0:
                return (cpu_time / wall_time) * 100
            return 0.0
        
        except Exception as e:
            print(f"Error measuring CPU usage: {e}")
            return 0.0
    
    def _run_benchmark_for_config(self, config: Dict[str, Any]) -> None:
        """
        Run benchmark for a specific configuration.
        
        Args:
            config: Configuration dictionary with parameters
        """
        config_name = config['name']
        print(f"  Running configuration: {config_name}")
        
        # Create directory for this specific configuration
        config_dir = os.path.join(
            self.output_dir, 
            self.current_version['name'], 
            config_name
        )
        os.makedirs(config_dir, exist_ok=True)
        
        times = []
        memory_usages = []
        cpu_usages = []
        profile_data = []
        
        for i in range(self.repetitions):
            print(f"    Repetition {i+1}/{self.repetitions}")
            
            # Create a run-specific subdirectory
            run_dir = os.path.join(config_dir, f"run_{i+1}")
            os.makedirs(run_dir, exist_ok=True)
            
            # Construct profile path
            profile_path = os.path.join(run_dir, f"profile_{i+1}.prof")
            
            # Construct command
            cmd = [
                "python", 
                "-m", 
                self.current_version['module_path'],
                "-f", config["landscape_file"],
                "-r", str(config["birth_mice"]),
                "-a", str(config["death_mice"]),
                "-k", str(config["diffusion_mice"]),
                "-b", str(config["birth_foxes"]),
                "-m", str(config["death_foxes"]),
                "-l", str(config["diffusion_foxes"]),
                "-dt", str(config["delta_t"]),
                "-t", str(config["time_step"]),
                "-d", str(config["duration"]),
                "-ls", str(config["landscape_seed"]),
                "-lp", str(config["landscape_prop"]),
                "-lsm", str(config["landscape_smooth"])
            ]
            
            try:
                # Profile with cProfile
                start_time = time.time()
                
                # Run the simulation with profiling
                subprocess.run([
                    "python", "-m", "cProfile", 
                    "-o", profile_path, 
                    *cmd[1:]  # Skip the 'python' part
                ], check=True, capture_output=True, text=True)
                
                end_time = time.time()
                execution_time = end_time - start_time
                times.append(execution_time)
                
                # Load and analyze the profile data
                profile_stats = pstats.Stats(profile_path)
                profile_data.append(profile_stats)
                
                # Measure memory usage
                mem_usage = self._measure_memory_usage(cmd)
                memory_usages.append(mem_usage)
                
                # Estimate CPU usage
                cpu_usage = self._measure_cpu_usage(cmd)
                cpu_usages.append(cpu_usage)
            
            except subprocess.CalledProcessError as e:
                print(f"    Error running benchmark: {e}")
                print(f"    stdout: {e.stdout}")
                print(f"    stderr: {e.stderr}")
                continue
            except Exception as e:
                print(f"    Unexpected error: {e}")
                continue
        
        # Only process results if we have some successful runs
        if times:
            # Extract landscape dimensions from file name
            landscape_size = self._extract_landscape_size(config["landscape_file"])
            
            # Process and save results
            avg_time = np.mean(times)
            std_time = np.std(times)
            avg_memory = np.mean(memory_usages)
            std_memory = np.std(memory_usages)
            avg_cpu = np.mean(cpu_usages)
            std_cpu = np.std(cpu_usages)
            
            # Store in results dataframe
            new_row = {
                'version': self.current_version['name'],
                'version_desc': self.current_version['desc'],
                'config_name': config_name,
                'landscape_size': landscape_size,
                'landscape_prop': config['landscape_prop'],
                'duration': config['duration'],
                'delta_t': config['delta_t'],
                'birth_mice': config['birth_mice'],
                'death_mice': config['death_mice'],
                'diffusion_mice': config['diffusion_mice'],
                'birth_foxes': config['birth_foxes'], 
                'death_foxes': config['death_foxes'],
                'diffusion_foxes': config['diffusion_foxes'],
                'time_step': config['time_step'],
                'landscape_smooth': config['landscape_smooth'],
                'landscape_seed': config['landscape_seed'],
                'execution_time': avg_time,
                'execution_time_std': std_time,
                'memory_usage': avg_memory,
                'memory_usage_std': std_memory,
                'cpu_usage': avg_cpu,
                'cpu_usage_std': std_cpu
            }
            
            self.results_df = pd.concat([
                self.results_df, 
                pd.DataFrame([new_row])
            ], ignore_index=True)
            
            # Save this configuration's results in version data
            self.current_version['results'][config_name] = {
                'times': times,
                'avg_time': avg_time,
                'std_time': std_time,
                'memory_usages': memory_usages,
                'avg_memory': avg_memory,
                'std_memory': std_memory,
                'cpu_usages': cpu_usages,
                'avg_cpu': avg_cpu,
                'std_cpu': std_cpu,
                'profile_data': profile_data,
                'config': config
            }
            
            # Generate visualizations for this specific configuration
            try:
                self._generate_profile_visualization(profile_data[0], config_dir)
            except Exception as e:
                print(f"    Could not generate profile visualization: {e}")
            
            print(f"    Average execution time: {avg_time:.2f}s ± {std_time:.2f}s")
            print(f"    Average memory usage: {avg_memory:.2f}MB ± {std_memory:.2f}MB")
            print(f"    Average CPU usage: {avg_cpu:.2f}% ± {std_cpu:.2f}%")
        else:
            print("    No successful runs for this configuration")
    
    def _run_single_benchmark(self, config: Dict[str, Any], profile_path: str) -> Tuple[float, float, float, str]:
        """
        Run a single benchmark and collect performance metrics.
        
        Args:
            config: Configuration dictionary with parameters
            profile_path: Path to save the profile data
            
        Returns:
            Tuple of (execution_time, memory_usage, cpu_usage, profile_path)
        """
        # Construct command to run the simulation
        cmd = [
            "python", "-m", "cProfile", "-o", profile_path,
            "-m", self.current_version['module_path'],
            "-f", config["landscape_file"],
            "-r", str(config["birth_mice"]),
            "-a", str(config["death_mice"]),
            "-k", str(config["diffusion_mice"]),
            "-b", str(config["birth_foxes"]),
            "-m", str(config["death_foxes"]),
            "-l", str(config["diffusion_foxes"]),
            "-dt", str(config["delta_t"]),
            "-t", str(config["time_step"]),
            "-d", str(config["duration"]),
            "-ls", str(config["landscape_seed"]),
            "-lp", str(config["landscape_prop"]),
            "-lsm", str(config["landscape_smooth"])
        ]
        
        # Measure execution time
        start_time = time.time()
        start_cpu_time = time.process_time()
        
        # Run the command
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        # Check for errors
        if process.returncode != 0:
            print(f"Error running benchmark: {process.stderr}")
            return 0.0, 0.0, 0.0, profile_path
        
        # Calculate execution time
        end_time = time.time()
        end_cpu_time = time.process_time()
        
        execution_time = end_time - start_time
        cpu_time = end_cpu_time - start_cpu_time
        
        # Estimate CPU usage
        if execution_time > 0:
            cpu_usage = (cpu_time / execution_time) * 100
        else:
            cpu_usage = 0.0
        
        # Estimate memory usage by running with memory_profiler in a separate process
        memory_usage = self._measure_memory_usage(cmd[1:])  # Skip the cProfile part
        
        return execution_time, memory_usage, cpu_usage, profile_path
    
    def _measure_memory_usage(self, cmd: List[str]) -> float:
        """
        Measure peak memory usage of the command.
        
        Args:
            cmd: Command to run (without the python part)
            
        Returns:
            Peak memory usage in MB
        """
        try:
            import psutil
            
            # Create a similar command but without cProfile
            python_cmd = [sys.executable]
            module_index = cmd.index("-m")
            python_cmd.extend(cmd[module_index:])
            
            # Start the process
            process = subprocess.Popen(python_cmd)
            
            # Monitor memory usage
            p = psutil.Process(process.pid)
            peak_memory = 0.0
            
            while process.poll() is None:
                try:
                    memory_info = p.memory_info()
                    current_memory = memory_info.rss / (1024 * 1024)  # Convert to MB
                    peak_memory = max(peak_memory, current_memory)
                    time.sleep(0.1)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break
            
            return peak_memory
        except ImportError:
            print("Warning: psutil not available. Memory usage measurement disabled.")
            return 0.0
        except Exception as e:
            print(f"Error measuring memory usage: {e}")
            return 0.0
    
    def _extract_landscape_size(self, landscape_file: str) -> str:
        """
        Extract landscape size from filename.
        
        Args:
            landscape_file: Path to the landscape file
            
        Returns:
            String representation of landscape size (e.g., "10x20")
        """
        file_name = os.path.basename(landscape_file)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Try to extract dimensions from common formats like '10x20'
        if 'x' in file_name_without_ext:
            return file_name_without_ext
        
        # Otherwise just return the filename
        return file_name_without_ext
    
    def _generate_profile_visualization(self, profile_stats: pstats.Stats, output_dir: str) -> None:
        """
        Generate visualization for profile data.
        
        Args:
            profile_stats: Profile statistics object
            output_dir: Directory to save visualization
        """
        ensure_dir_exists(output_dir)
        
        # Save text-based profile statistics
        stats_file = os.path.join(output_dir, "profile_stats.txt")
        with open(stats_file, 'w') as f:
            # Redirect stdout to file
            original_stdout = sys.stdout
            sys.stdout = f
            
            # Print multiple views of the profile data
            print("=== Profile Statistics (sorted by cumulative time) ===")
            profile_stats.strip_dirs().sort_stats('cumulative').print_stats(30)
            
            print("\n=== Profile Statistics (sorted by total time) ===")
            profile_stats.strip_dirs().sort_stats('time').print_stats(30)
            
            print("\n=== Profile Statistics (sorted by call count) ===")
            profile_stats.strip_dirs().sort_stats('calls').print_stats(30)
            
            # Restore stdout
            sys.stdout = original_stdout
        
        # Try to generate graphical visualization using gprof2dot + dot
        try:
            # Generate DOT file
            dot_file = os.path.join(output_dir, "profile.dot")
            subprocess.run([
                "python", "-m", "gprof2dot",
                "-f", "pstats",
                profile_stats.stats_file,
                "-o", dot_file
            ], check=True)
            
            # Generate PNG from DOT
            png_file = os.path.join(output_dir, "profile.png")
            subprocess.run([
                "dot",
                "-Tpng",
                dot_file,
                "-o", png_file
            ], check=True)
            
            print(f"    Profile visualization saved to {png_file}")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"    Warning: Could not generate profile visualization: {e}")
            print("    Make sure gprof2dot and graphviz are installed.")
    
    def save_results(self) -> None:
        """Save all results to files."""
        # Save results dataframe to CSV
        csv_path = os.path.join(self.output_dir, "results.csv")
        self.results_df.to_csv(csv_path, index=False)
        
        # Save full results dictionary to pickle
        pickle_path = os.path.join(self.output_dir, "results.pkl")
        with open(pickle_path, 'wb') as f:
            pickle.dump(self.results, f)
        
        print(f"Results saved to {csv_path} and {pickle_path}")