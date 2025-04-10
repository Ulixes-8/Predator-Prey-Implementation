# Predator-Prey Performance Experiment Framework

## Overview

This framework provides a comprehensive suite for benchmarking and analyzing the performance of predator-prey simulation refactorings/implementations. The code has been structured to follow software engineering best practices including modularity, reusability, proper documentation, and type annotations.

## Directory Structure

```
performance_experiment/
├── performance_experiment.py      # Main entry point
├── src/                           # Core source code
│   ├── performance_core.py        # Core configuration and utilities
│   ├── performance_runner.py      # Simulation execution utilities
│   └── performance_reporting.py   # Results handling and output
├── experiments/                   # Experiment implementations
│   ├── experiment_grid.py         # Grid scaling experiment
│   ├── experiment_landscape.py    # Landscape proportion experiment
│   ├── experiment_cpu.py          # CPU scaling experiment
│   └── experiment_matrix.py       # Full matrix experiment
├── implementations/               # Simulation implementations
│   ├── baseline.py                # Original simulation implementation
│   ├── refactor_1.py              # First refactored implementation
│   ├── refactor_2.py              # Second refactored implementation
│   ├── refactor_3.py              # Third refactored implementation
│   └── simulate_predator_prey_wrapper.py  # Wrapper for main implementation
├── utils/                         # Utility scripts
│   └── create_dats.py             # Data file generator
└── scripts/                       # Shell scripts
    ├── run_experiment_set_1.sh    # Batch execution script #1
    └── run_experiment_set_2.sh    # Batch execution script #2
```

## Quick Start

Run all experiments with the baseline implementation:

```bash
python -m performance_experiment.performance_experiment
```

Run a specific experiment with a particular implementation:

```bash
python -m performance_experiment.performance_experiment --implementation refactor_2 --experiments grid
```

## Command-Line Arguments

- `--implementation` or `-i`: Implementation to use (baseline, refactor_1, refactor_2, etc.)
- `--experiments` or `-e`: Experiments to run (grid, landscape, cpu, matrix, or all)

## Available Experiments

| Experiment | Description | Flag |
|------------|-------------|------|
| Grid Scaling | Tests how performance scales with increasing grid sizes | `grid` |
| Landscape Proportion | Tests performance with different land vs. water proportions | `landscape` |
| CPU Scaling | Tests performance with varying numbers of CPU cores | `cpu` |
| Full Matrix | Comprehensive test of all grid sizes and land proportions | `matrix` |

## Adding New Implementations

To add a new implementation for testing:

1. Create a new file `implementations/refactor_X.py` (where X is the next number)
2. Ensure it has the same interface as baseline.py (functions `getVersion()`, `simCommLineIntf()`, and `sim()`)
3. Run your experiments with `--implementation refactor_X`

## Utility Scripts

- `utils/create_dats.py`: Generate .dat landscape files for experiments
- `scripts/run_experiment_set_1.sh`: Run grid, landscape, and matrix experiments for all implementations
- `scripts/run_experiment_set_2.sh`: Run grid experiments for refactor_2 and refactor_3, and cpu experiments for refactor_3

## Results

Results are saved in the `performance_results/` directory with JSON files named according to the experiment type and implementation used (e.g., `BASELINE_grid_scaling.json`).

Each JSON file contains metadata about the experiment conditions and detailed performance results.

## Visualization

Results can be visualized using the Jupyter notebook in `performance_results/plot_performance_results.ipynb`.

## Author

s2659865  
April 2025