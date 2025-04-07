#!/usr/bin/env python3
"""
Script: run_experiment.py
Description:
    This script provides a convenient way to run performance experiments on
    the predator-prey simulation code. It executes the performance_experiment.py
    script with appropriate arguments.
    
    It can run tests for a specific version, analyze results from multiple versions,
    and generate progressive comparison charts.
"""

import os
import argparse
import subprocess
import sys
from typing import List, Optional

def run_command(cmd: List[str], desc: str) -> bool:
    """
    Run a command and handle errors.
    
    Args:
        cmd: Command to run as a list of strings
        desc: Description of the command for logging
        
    Returns:
        True if command succeeded, False otherwise
    """
    print(f"\n{'-'*80}")
    print(f"Running: {desc}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'-'*80}\n")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n{'-'*80}")
        print(f"{desc} completed successfully")
        print(f"{'-'*80}\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{'-'*80}")
        print(f"Error executing {desc}: {e}")
        print(f"{'-'*80}\n")
        return False

def test_version(version: str, test_set: str, repetitions: int) -> bool:
    """
    Run performance tests for a specific version.
    
    Args:
        version: Version name (e.g., 'original', 'refactor_1')
        test_set: Test set to use ('quick', 'medium', 'comprehensive')
        repetitions: Number of repetitions for each test
        
    Returns:
        True if tests succeeded, False otherwise
    """
    cmd = [
        "python", "performance_experiment.py",
        "--version", version,
        "--test-set", test_set,
        "--repetitions", str(repetitions)
    ]
    
    return run_command(cmd, f"Performance tests for version '{version}'")

def analyze_results(versions: List[str], progressive: bool = False) -> bool:
    """
    Analyze results from multiple versions.
    
    Args:
        versions: List of version names to analyze
        progressive: Whether to create progressive comparison charts
        
    Returns:
        True if analysis succeeded, False otherwise
    """
    cmd = [
        "python", "performance_experiment.py",
        "--analyze",
        "--versions", *versions
    ]
    
    if progressive:
        cmd.append("--progressive")
    
    return run_command(cmd, "Results analysis")

def main() -> None:
    """
    Main function to parse arguments and run the appropriate command.
    """
    parser = argparse.ArgumentParser(description="Run performance experiments for predator-prey simulation")
    
    # Action to perform
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--test", action="store_true", help="Run tests for a specific version")
    action_group.add_argument("--analyze", action="store_true", help="Analyze results from multiple versions")
    
    # Test arguments
    parser.add_argument("--version", type=str, default="original", help="Version to test")
    parser.add_argument("--test-set", type=str, default="quick", 
                       choices=["quick", "medium", "comprehensive"], 
                       help="Test set to use")
    parser.add_argument("--repetitions", type=int, default=3, help="Number of repetitions for each test")
    
    # Analysis arguments
    parser.add_argument("--versions", type=str, nargs="+", help="Versions to include in analysis")
    parser.add_argument("--progressive", action="store_true", help="Create progressive comparison charts")
    
    args = parser.parse_args()
    
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    
    # Perform the requested action
    if args.test:
        success = test_version(args.version, args.test_set, args.repetitions)
    elif args.analyze:
        if not args.versions:
            print("Error: --analyze requires --versions")
            sys.exit(1)
        
        success = analyze_results(args.versions, args.progressive)
    else:
        print("Error: No action specified")
        parser.print_help()
        sys.exit(1)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()