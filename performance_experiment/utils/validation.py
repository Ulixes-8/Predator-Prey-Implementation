"""
Input validation utilities for the predator-prey simulation.

This module provides functions for validating simulation parameters
and input files to ensure they are within acceptable ranges.
"""
from typing import Optional, Dict, Any, Union, List, Tuple
import os
import numpy as np


def validate_file_exists(file_path: str) -> None:
    """
    Validate that a file exists and is readable.
    
    Args:
        file_path: Path to the file to check
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file cannot be read
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Animal file not found: {file_path}")
    if not os.path.isfile(file_path):
        raise ValueError(f"Path is not a file: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read file: {file_path}")


def validate_positive_float(value: float, name: str) -> None:
    """
    Validate that a value is a positive float.
    
    Args:
        value: Value to check
        name: Name of the parameter (for error messages)
        
    Raises:
        ValueError: If the value is not a positive float
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")


def validate_positive_int(value: int, name: str) -> None:
    """
    Validate that a value is a positive integer.
    
    Args:
        value: Value to check
        name: Name of the parameter (for error messages)
        
    Raises:
        ValueError: If the value is not a positive integer
    """
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")


def validate_proportion(value: float, name: str) -> None:
    """
    Validate that a value is a proportion between 0 and 1.
    
    Args:
        value: Value to check
        name: Name of the parameter (for error messages)
        
    Raises:
        ValueError: If the value is not between 0 and 1
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number, got {type(value).__name__}")
    if value < 0 or value > 1:
        raise ValueError(f"{name} must be between 0 and 1, got {value}")


def validate_simulation_parameters(
    r: float, a: float, k: float, b: float, m: float, l: float,
    dt: float, t: int, d: int, lseed: int, lp: float, lsm: int
) -> None:
    """
    Validate all simulation parameters.
    
    Args:
        r: Birth rate of mice
        a: Rate at which foxes eat mice
        k: Diffusion rate of mice
        b: Birth rate of foxes
        m: Rate at which foxes starve
        l: Diffusion rate of foxes
        dt: Time step size
        t: Number of time steps between outputs
        d: Total simulation duration
        lseed: Random seed for landscape generation
        lp: Proportion of landscape that is land
        lsm: Number of smoothing passes
        
    Raises:
        ValueError: If any parameters are invalid
    """
    # Validate rates
    validate_positive_float(r, "mice birth rate (r)")
    validate_positive_float(a, "mice death rate (a)")
    validate_positive_float(k, "mice diffusion rate (k)")
    validate_positive_float(b, "foxes birth rate (b)")
    validate_positive_float(m, "foxes death rate (m)")
    validate_positive_float(l, "foxes diffusion rate (l)")
    
    # Validate simulation control parameters
    validate_positive_float(dt, "time step size (dt)")
    validate_positive_int(t, "output time step (t)")
    validate_positive_int(d, "simulation duration (d)")
    
    # Validate landscape parameters
    if not isinstance(lseed, int):
        raise TypeError(f"landscape seed must be an integer, got {type(lseed).__name__}")
    validate_proportion(lp, "landscape proportion (lp)")
    if not isinstance(lsm, int):
        raise TypeError(f"landscape smoothing passes must be an integer, got {type(lsm).__name__}")
    if lsm < 0:
        raise ValueError(f"landscape smoothing passes must be non-negative, got {lsm}")