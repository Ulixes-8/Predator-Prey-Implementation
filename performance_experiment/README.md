# Predator-Prey Performance Experiment Framework

## Overview

This framework provides a comprehensive suite for benchmarking and analyzing the performance of predator-prey simulation implementations. The code has been structured to follow software engineering best practices including modularity, reusability, proper documentation, and type annotations.

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
├── refactor_3.py                  # Third refactored implementation
└── performance_results/           # Generated results directory
    ├── grid_scaling/              # Grid scaling experiment results
    ├── landscape_prop/            # Landscape proportion experiment results
    ├── cpu_scaling/               # CPU scaling experiment results
    └── full_matrix/               # Full matrix experiment results
```

## Experiments

The framework includes four main experiments:

1. **Grid Scaling**: Tests how simulation performance scales with increasing grid sizes while keeping other parameters constant.

2. **Landscape Proportion**: Tests how the proportion of land vs. water affects simulation performance.

3. **CPU Scaling**: Tests how the simulation utilizes different numbers of CPU cores and how performance scales with increasing core counts.

4. **Full Matrix**: Runs a comprehensive matrix of grid sizes and land proportions to provide a complete performance profile.

## Usage

To run all experiments:

```bash
python performance_experiment.py
```

To run individual experiments:

```bash
python experiment_grid.py        # Run only grid scaling experiment
python experiment_landscape.py   # Run only landscape proportion experiment
python experiment_cpu.py         # Run only CPU scaling experiment
python experiment_matrix.py      # Run only full matrix experiment
```

## Refactoring Strategy

The performance experiment framework allows you to test and compare multiple implementations of the predator-prey simulation:

1. **baseline.py**: The original implementation (unchanged)
2. **refactor_1.py**, **refactor_2.py**, etc.: Incrementally improved versions

This approach enables precise attribution of performance gains to specific refactoring changes.

## Results

Results are stored in JSON format in the `performance_results/` directory, organized by experiment type. Each JSON file includes:

- Comprehensive metadata (system information, experiment parameters, timestamp)
- Raw timing results for each tested configuration
- Statistical data (means, standard deviations)

For CPU scaling experiments, additional metrics are recorded:
- CPU utilization percentages
- Number of active cores
- Core utilization efficiency

## Dependencies

The framework requires:
- Python 3.8+
- NumPy
- psutil (for CPU monitoring)

## Author

s2659865
April 2025