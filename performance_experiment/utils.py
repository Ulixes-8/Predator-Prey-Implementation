"""
Utility functions for the performance experiment framework.

This module provides helper functions for processing data, file operations,
statistical analysis, and output comparison.
"""

import os
import numpy as np
import pandas as pd
import subprocess
import sys
import pickle
from typing import Dict, List, Any, Tuple, Optional, Union
import importlib
import importlib.util
import time
import tempfile
import shutil

def ensure_dir_exists(directory: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to check/create
    """
    os.makedirs(directory, exist_ok=True)

def load_results(results_file: str) -> Any:
    """
    Load benchmark results from a pickle file.
    
    Args:
        results_file: Path to the results file
        
    Returns:
        Loaded results data
    """
    with open(results_file, 'rb') as f:
        return pickle.load(f)

def save_results(results: Any, output_file: str) -> None:
    """
    Save benchmark results to a pickle file.
    
    Args:
        results: Results data to save
        output_file: Path where results should be saved
    """
    ensure_dir_exists(os.path.dirname(output_file))
    with open(output_file, 'wb') as f:
        pickle.dump(results, f)

def compute_statistics(data: List[float]) -> Dict[str, float]:
    """
    Compute statistical metrics for a data series.
    
    Args:
        data: List of numeric values
        
    Returns:
        Dictionary with statistical metrics: mean, std, min, max, etc.
    """
    data_array = np.array(data)
    return {
        'mean': np.mean(data_array),
        'std': np.std(data_array),
        'min': np.min(data_array),
        'max': np.max(data_array),
        'median': np.median(data_array),
        'q25': np.percentile(data_array, 25),
        'q75': np.percentile(data_array, 75),
        'ci95_low': np.mean(data_array) - 1.96 * np.std(data_array) / np.sqrt(len(data_array)),
        'ci95_high': np.mean(data_array) + 1.96 * np.std(data_array) / np.sqrt(len(data_array)),
    }

def detect_outliers(data: List[float], method: str = 'iqr') -> List[bool]:
    """
    Detect outliers in a data series.
    
    Args:
        data: List of numeric values
        method: Method to use for outlier detection ('iqr' or 'zscore')
        
    Returns:
        List of boolean values indicating whether each value is an outlier
    """
    data_array = np.array(data)
    
    if method == 'iqr':
        q25 = np.percentile(data_array, 25)
        q75 = np.percentile(data_array, 75)
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        return [(x < lower_bound or x > upper_bound) for x in data_array]
    
    elif method == 'zscore':
        mean = np.mean(data_array)
        std = np.std(data_array)
        zscores = [(x - mean) / std for x in data_array]
        return [abs(z) > 3 for z in zscores]
    
    else:
        raise ValueError(f"Unknown outlier detection method: {method}")

def format_time(seconds: float) -> str:
    """
    Format a time duration in seconds to a human-readable string.
    
    Args:
        seconds: Time duration in seconds
        
    Returns:
        Formatted time string (e.g., "1h 2m 3.45s")
    """
    if seconds < 60:
        return f"{seconds:.2f}s"
    
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {seconds:.2f}s"
    
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}h {int(minutes)}m {seconds:.2f}s"

def create_clean_environment() -> Dict[str, str]:
    """
    Create a clean environment for running benchmarks.
    
    This removes potentially interfering environment variables.
    
    Returns:
        Clean environment dictionary
    """
    env = os.environ.copy()
    
    # Remove potentially interfering variables
    keys_to_remove = [
        key for key in env 
        if key.startswith('PYTHON') or key.startswith('LD_') or key.startswith('LC_')
    ]
    
    for key in keys_to_remove:
        if key in env:
            del env[key]
    
    return env

def compare_output_files(file1: str, file2: str) -> bool:
    """
    Compare two output files to check if they are identical.
    
    Args:
        file1: Path to first file
        file2: Path to second file
        
    Returns:
        True if files are identical, False otherwise
    """
    # For text files, read line by line to handle potential line ending differences
    try:
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()
            
            if len(lines1) != len(lines2):
                return False
            
            for l1, l2 in zip(lines1, lines2):
                if l1.strip() != l2.strip():
                    return False
            
            return True
    except UnicodeDecodeError:
        # For binary files, compare byte by byte
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            chunk_size = 8192
            
            while True:
                chunk1 = f1.read(chunk_size)
                chunk2 = f2.read(chunk_size)
                
                if chunk1 != chunk2:
                    return False
                
                if not chunk1:  # End of both files
                    return True

def import_module_from_path(module_path: str, module_name: Optional[str] = None) -> Any:
    """
    Import a Python module from a file path.
    
    Args:
        module_path: Path to the Python module file
        module_name: Optional name for the imported module
        
    Returns:
        Imported module object
    """
    if module_name is None:
        module_name = os.path.splitext(os.path.basename(module_path))[0]
    
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module

def run_with_timeout(func, args=(), kwargs={}, timeout_sec=60):
    """
    Run a function with a timeout.
    
    Args:
        func: Function to run
        args: Arguments to pass to the function
        kwargs: Keyword arguments to pass to the function
        timeout_sec: Timeout in seconds
        
    Returns:
        Result of the function if it completes within the timeout
        
    Raises:
        TimeoutError: If the function does not complete within the timeout
    """
    import multiprocessing
    
    result_queue = multiprocessing.Queue()
    
    def wrapper():
        try:
            result = func(*args, **kwargs)
            result_queue.put(('result', result))
        except Exception as e:
            result_queue.put(('error', e))
    
    process = multiprocessing.Process(target=wrapper)
    process.start()
    process.join(timeout_sec)
    
    if process.is_alive():
        process.terminate()
        process.join()
        raise TimeoutError(f"Function {func.__name__} timed out after {timeout_sec} seconds")
    
    if not result_queue.empty():
        status, result = result_queue.get()
        if status == 'result':
            return result
        else:
            raise result
    
    raise RuntimeError("Function finished but no result was returned")