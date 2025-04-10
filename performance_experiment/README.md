# Predator-Prey Performance Experiment Framework

## Overview

This framework provides a comprehensive suite for benchmarking and analyzing the performance of predator-prey simulation refactorings/implementations. The code has been structured to follow software engineering best practices including modularity, reusability, proper documentation, and type annotations.

## Structure

The performance experiment framework is organized into modular components:

```
performance_experiment/
├── performance_experiment.py      # Main entry point
├── performance_core.py            # Core configuration and utilities
├── performance_runner.py          # Simulation execution utilities
├── performance_reporting.py       # Results handling and output
├── experiment_grid.py             # Grid scaling experiment
├── experiment_landscape.py        # Landscape proportion experiment
├── experiment_cpu.py              # CPU scaling experiment
├── experiment_matrix.py           # Full matrix experiment
├── baseline.py                    # Original simulation implementation
├── refactor_1.py                  # First refactored implementation
├── refactor_2.py                  # Second refactored implementation
├── . . . 
├── refactor_n.py                  # N'th refactored implementation
└── performance_results/           # Generated results directory
    ├── grid_scaling/              # Grid scaling experiment results
    ├── landscape_prop/            # Landscape proportion experiment results
    ├── cpu_scaling/               # CPU scaling experiment results
    └── full_matrix/               # Full matrix experiment results
```
## Dependencies

The framework requires:
- Python 3.8+
- NumPy
- psutil (for CPU monitoring)

## How to Use

### Basic Usage

Run all experiments using the baseline implementation:

```bash
python performance_experiment.py
```

Run all experiments using a specific refactored implementation:

```bash
python performance_experiment.py --implementation refactor_1
```

### Running Specific Experiments

You can choose to run only specific experiments:

```bash
# Run only grid scaling experiment with refactor_2
python performance_experiment.py --implementation refactor_2 --experiments grid

# Run landscape and CPU experiments with baseline
python performance_experiment.py --experiments landscape cpu

# Run full matrix experiment with refactor_3
python performance_experiment.py --implementation refactor_3 --experiments matrix
```

### Available Experiments

- `grid`: Grid size scaling experiment
- `landscape`: Landscape proportion experiment
- `cpu`: CPU scaling experiment
- `matrix`: Full matrix experiment
- `all`: Run all experiments (default)

### Available Implementations

The framework automatically detects available implementations in the current directory:

- `baseline`: Original implementation
- `refactor_1`, `refactor_2`, etc.: Refactored implementations

## Result Files

Results will be saved in the `performance_results/` directory with filenames reflecting the implementation used:

- `BASELINE_grid_scaling.json`
- `REFACTOR_1_grid_scaling.json`
- `REFACTOR_2_landscape_prop.json` 
- etc.

## Example Usage Sequence

To benchmark all implementations:

```bash
# Run baseline
python performance_experiment.py --implementation baseline

# Run first refactored implementation
python performance_experiment.py --implementation refactor_1

# Run second refactored implementation
python performance_experiment.py --implementation refactor_2

# Run third refactored implementation
python performance_experiment.py --implementation refactor_3
```

You can then compare the JSON result files to evaluate the performance improvements between implementations.

## Author

s2659865
April 2025