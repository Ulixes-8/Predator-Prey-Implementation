"""
Visualization utilities for the performance experiment results.

This module provides functions for creating visualizations of benchmark results,
including execution time comparisons, memory usage, parameter sensitivity,
and profile call graphs.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import seaborn as sns
from typing import Dict, List, Any, Optional, Union
import subprocess
from performance_experiment.utils import ensure_dir_exists

plt.style.use('ggplot')  # Use a nicer style for plots

def plot_execution_times(results_df: pd.DataFrame, output_dir: str) -> None:
    """
    Create bar charts comparing execution times across versions.
    
    Args:
        results_df: DataFrame containing benchmark results
        output_dir: Directory where plots should be saved
    """
    ensure_dir_exists(output_dir)
    
    # Get unique config names and versions
    config_names = results_df['config_name'].unique()
    versions = results_df['version'].unique()
    
    # For each configuration, create a bar chart comparing versions
    for config_name in config_names:
        # Filter data for this configuration
        config_data = results_df[results_df['config_name'] == config_name]
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Plot bar chart
        x = np.arange(len(versions))
        times = [config_data[config_data['version'] == ver]['execution_time'].values[0] for ver in versions]
        errors = [config_data[config_data['version'] == ver]['execution_time_std'].values[0] for ver in versions]
        
        bars = plt.bar(x, times, yerr=errors, capsize=5)
        
        # Add labels and formatting
        plt.xlabel('Code Version')
        plt.ylabel('Execution Time (s)')
        plt.title(f'Execution Time Comparison for {config_name}')
        plt.xticks(x, versions, rotation=45, ha='right')
        plt.tight_layout()
        
        # Add value labels on top of bars
        for bar, time in zip(bars, times):
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width()/2.,
                height + 0.1,
                f'{time:.2f}s',
                ha='center', va='bottom'
            )
        
        # Save figure
        plt.savefig(os.path.join(output_dir, f"execution_times_{config_name}.png"))
        plt.close()

def plot_memory_usage(results_df: pd.DataFrame, output_dir: str) -> None:
    """
    Create bar charts comparing memory usage across versions.
    
    Args:
        results_df: DataFrame containing benchmark results
        output_dir: Directory where plots should be saved
    """
    ensure_dir_exists(output_dir)
    
    # Get unique config names and versions
    config_names = results_df['config_name'].unique()
    versions = results_df['version'].unique()
    
    # For each configuration, create a bar chart comparing versions
    for config_name in config_names:
        # Filter data for this configuration
        config_data = results_df[results_df['config_name'] == config_name]
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Plot bar chart
        x = np.arange(len(versions))
        memory = [config_data[config_data['version'] == ver]['memory_usage'].values[0] for ver in versions]
        errors = [config_data[config_data['version'] == ver]['memory_usage_std'].values[0] for ver in versions]
        
        bars = plt.bar(x, memory, yerr=errors, capsize=5)
        
        # Add labels and formatting
        plt.xlabel('Code Version')
        plt.ylabel('Memory Usage (MB)')
        plt.title(f'Memory Usage Comparison for {config_name}')
        plt.xticks(x, versions, rotation=45, ha='right')
        plt.tight_layout()
        
        # Add value labels on top of bars
        for bar, mem in zip(bars, memory):
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width()/2.,
                height + 0.1,
                f'{mem:.2f}MB',
                ha='center', va='bottom'
            )
        
        # Save figure
        plt.savefig(os.path.join(output_dir, f"memory_usage_{config_name}.png"))
        plt.close()

def plot_parameter_sensitivity(results_df: pd.DataFrame, parameter: str, output_dir: str) -> None:
    """
    Create line charts showing sensitivity to a specific parameter.
    
    Args:
        results_df: DataFrame containing benchmark results
        parameter: Parameter to analyze (e.g., 'landscape_prop', 'duration')
        output_dir: Directory where plots should be saved
    """
    ensure_dir_exists(output_dir)
    
    # Get unique versions
    versions = results_df['version'].unique()
    
    # Create figure
    plt.figure(figsize=(12, 6))
    
    # For each version, create a line showing parameter sensitivity
    for version in versions:
        # Filter data for this version
        version_data = results_df[results_df['version'] == version]
        
        # Get parameter values and execution times
        # Filter out rows where other parameters vary
        base_config = results_df.iloc[0]
        relevant_columns = [col for col in results_df.columns if col != parameter 
                          and col != 'version' and col != 'execution_time' 
                          and col != 'execution_time_std' and col != 'memory_usage'
                          and col != 'memory_usage_std' and col != 'cpu_usage'
                          and col != 'cpu_usage_std' and col != 'config_name']
        
        matching_rows = version_data
        for col in relevant_columns:
            matching_rows = matching_rows[matching_rows[col] == base_config[col]]
        
        if len(matching_rows) < 2:
            continue  # Skip if not enough data points
            
        param_values = matching_rows[parameter].values
        times = matching_rows['execution_time'].values
        
        # Sort by parameter value
        sorted_indices = np.argsort(param_values)
        param_values = param_values[sorted_indices]
        times = times[sorted_indices]
        
        # Plot line
        plt.plot(param_values, times, 'o-', label=version)
    
    # Add labels and formatting
    plt.xlabel(parameter)
    plt.ylabel('Execution Time (s)')
    plt.title(f'Sensitivity to {parameter}')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save figure
    plt.savefig(os.path.join(output_dir, f"sensitivity_{parameter}.png"))
    plt.close()

def plot_speedup(results_df: pd.DataFrame, output_dir: str, baseline_version: Optional[str] = None) -> None:
    """
    Create bar charts showing speedup relative to baseline.
    
    Args:
        results_df: DataFrame containing benchmark results
        output_dir: Directory where plots should be saved
        baseline_version: Version to use as baseline (default: first version)
    """
    ensure_dir_exists(output_dir)
    
    # Get unique config names and versions
    config_names = results_df['config_name'].unique()
    versions = results_df['version'].unique()
    
    # If baseline version is not specified, use the first version
    if baseline_version is None:
        baseline_version = versions[0]
    
    # For each configuration, create a bar chart showing speedup
    for config_name in config_names:
        # Filter data for this configuration
        config_data = results_df[results_df['config_name'] == config_name]
        
        # Get baseline execution time
        baseline_time = config_data[config_data['version'] == baseline_version]['execution_time'].values[0]
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Calculate speedup for each version
        x = np.arange(len(versions))
        times = [config_data[config_data['version'] == ver]['execution_time'].values[0] for ver in versions]
        speedups = [baseline_time / time for time in times]
        
        bars = plt.bar(x, speedups)
        
        # Add reference line for baseline (speedup = 1.0)
        plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.7)
        
        # Add labels and formatting
        plt.xlabel('Code Version')
        plt.ylabel('Speedup (relative to baseline)')
        plt.title(f'Performance Speedup for {config_name} (relative to {baseline_version})')
        plt.xticks(x, versions, rotation=45, ha='right')
        plt.tight_layout()
        
        # Add value labels on top of bars
        for bar, speedup in zip(bars, speedups):
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width()/2.,
                height + 0.05,
                f'{speedup:.2f}x',
                ha='center', va='bottom'
            )
        
        # Save figure
        plt.savefig(os.path.join(output_dir, f"speedup_{config_name}.png"))
        plt.close()
        
        # Also create a log-scale version for better visualization
        plt.figure(figsize=(12, 6))
        plt.bar(x, speedups)
        plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.7)
        plt.xlabel('Code Version')
        plt.ylabel('Speedup (log scale)')
        plt.title(f'Performance Speedup for {config_name} (Log Scale, relative to {baseline_version})')
        plt.xticks(x, versions, rotation=45, ha='right')
        plt.yscale('log')
        plt.tight_layout()
        
        # Add value labels on top of bars
        for i, speedup in enumerate(speedups):
            plt.text(
                i,
                speedup * 1.05,
                f'{speedup:.2f}x',
                ha='center', va='bottom'
            )
        
        plt.savefig(os.path.join(output_dir, f"speedup_log_{config_name}.png"))
        plt.close()

def plot_heatmap(results_df: pd.DataFrame, row_param: str, col_param: str, 
                 version: str, metric: str, output_dir: str) -> None:
    """
    Create a heatmap showing how two parameters interact to affect performance.
    
    Args:
        results_df: DataFrame containing benchmark results
        row_param: Parameter to use for heatmap rows
        col_param: Parameter to use for heatmap columns
        version: Version to analyze
        metric: Metric to show in heatmap ('execution_time', 'memory_usage', etc.)
        output_dir: Directory where plots should be saved
    """
    ensure_dir_exists(output_dir)
    
    # Filter data for this version
    version_data = results_df[results_df['version'] == version]
    
    # Get unique values for row and column parameters
    row_values = version_data[row_param].unique()
    col_values = version_data[col_param].unique()
    
    # Create a 2D array for the heatmap
    heatmap_data = np.zeros((len(row_values), len(col_values)))
    
    # Fill the heatmap data
    for i, row_val in enumerate(row_values):
        for j, col_val in enumerate(col_values):
            matching_rows = version_data[(version_data[row_param] == row_val) & 
                                         (version_data[col_param] == col_val)]
            if not matching_rows.empty:
                heatmap_data[i, j] = matching_rows[metric].values[0]
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Create heatmap
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="viridis",
                xticklabels=col_values, yticklabels=row_values)
    
    # Add labels and formatting
    plt.xlabel(col_param)
    plt.ylabel(row_param)
    plt.title(f'{metric} Heatmap for {version} - {row_param} vs {col_param}')
    plt.tight_layout()
    
    # Save figure
    plt.savefig(os.path.join(output_dir, f"heatmap_{version}_{row_param}_{col_param}_{metric}.png"))
    plt.close()

def create_profile_visualization(profile_file: str, output_dir: str, format_type: str = 'png') -> None:
    """
    Generate visualization for a profile file using gprof2dot and graphviz.
    
    Args:
        profile_file: Path to the profile file
        output_dir: Directory where visualizations should be saved
        format_type: Output format ('png', 'svg', 'pdf')
    """
    ensure_dir_exists(output_dir)
    
    # Generate profile visualization
    base_name = os.path.splitext(os.path.basename(profile_file))[0]
    dot_file = os.path.join(output_dir, f"{base_name}.dot")
    output_file = os.path.join(output_dir, f"{base_name}.{format_type}")
    
    try:
        # Convert profile to DOT format
        dot_cmd = [
            "python", "-m", "gprof2dot",
            "-f", "pstats",
            profile_file,
            "-o", dot_file
        ]
        subprocess.run(dot_cmd, check=True)
        
        # Convert DOT to desired output format
        dot_cmd = [
            "dot",
            "-T" + format_type,
            dot_file,
            "-o", output_file
        ]
        subprocess.run(dot_cmd, check=True)
        
        print(f"Created profile visualization: {output_file}")
        return output_file
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Error creating profile visualization: {e}")
        return None

def generate_all_visualizations(results_df: pd.DataFrame, output_dir: str) -> None:
    """
    Generate all visualizations for benchmark results.
    
    Args:
        results_df: DataFrame containing benchmark results
        output_dir: Directory where visualizations should be saved
    """
    # Create base directory
    ensure_dir_exists(output_dir)
    
    # 1. Plot execution times
    plot_execution_times(results_df, os.path.join(output_dir, "execution_times"))
    
    # 2. Plot memory usage
    plot_memory_usage(results_df, os.path.join(output_dir, "memory_usage"))
    
    # 3. Plot parameter sensitivity for various parameters
    sensitivity_dir = os.path.join(output_dir, "sensitivity")
    ensure_dir_exists(sensitivity_dir)
    for param in ['landscape_prop', 'duration', 'delta_t', 'birth_mice', 'death_mice', 
                  'diffusion_mice', 'birth_foxes', 'death_foxes', 'diffusion_foxes']:
        plot_parameter_sensitivity(results_df, param, sensitivity_dir)
    
    # 4. Plot speedup relative to baseline
    plot_speedup(results_df, os.path.join(output_dir, "speedup"))
    
    # 5. Plot heatmaps for parameter interactions
    # For each version, create heatmaps for important parameter pairs
    heatmap_dir = os.path.join(output_dir, "heatmaps")
    ensure_dir_exists(heatmap_dir)
    
    versions = results_df['version'].unique()
    param_pairs = [
        ('birth_mice', 'death_mice'),
        ('birth_foxes', 'death_foxes'),
        ('diffusion_mice', 'diffusion_foxes'),
        ('landscape_prop', 'duration')
    ]
    
    for version in versions:
        for row_param, col_param in param_pairs:
            plot_heatmap(results_df, row_param, col_param, version, 'execution_time', heatmap_dir)
            plot_heatmap(results_df, row_param, col_param, version, 'memory_usage', heatmap_dir)
    
    # Create summary visualizations
    # TODO: Add more summary visualizations as needed
    
    print(f"All visualizations generated in {output_dir}")