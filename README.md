# Predator-Prey Simulation Project

## Overview

This repository contains a predator-prey simulation that models the interaction between foxes (predators) and mice (prey) in a two-dimensional landscape. The project includes the core simulation, multiple optimized implementations, a comprehensive test suite, and a performance benchmarking framework.

## Repository Structure

```
predator_prey/
├── predator_prey/                # Core simulation package
│   ├── __init__.py
│   ├── simulate_predator_prey.py # Main simulation implementation
│   ├── src/                      # Simulation source modules
│   └── utils/                    # Simulation utilities
├── performance_experiment/       # Performance benchmarking framework
│   ├── performance_experiment.py # Framework entry point
│   ├── experiments/              # Different experiment types
│   ├── implementations/          # Various implementations to compare
│   ├── src/                      # Framework core components
│   ├── utils/                    # Utility scripts
│   └── scripts/                  # Shell scripts for batch execution
├── test/                         # Comprehensive test suite
│   ├── test_example.py           # Simple example test
│   ├── core/                     # Core functionality tests
│   ├── implementations/          # Implementation tests
│   ├── io/                       # Input/output tests
│   └── utils/                    # Test utilities and fixtures
├── animals/                      # Input data files for animals
│   └── *.dat                     # Animal density grid files
└── requirements.txt              # Python dependencies
```

## Requirements

* Python 3.x
* [numpy](https://numpy.org/)
* [pytest](https://pytest.org/)

To install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Simulation

### Basic Usage

To run the simulation with default parameters:

```bash
python -m predator_prey.simulate_predator_prey -f animals/20x10.dat
```

### Command-line Arguments

| Flag | Parameter | Description | Default Value |
| ---- | --------- |------------ | ------------- |
| -h | --help | Show help message and exit | - |
| -r | --birth-mice | Birth rate of mice | 0.08 |
| -a | --death-mice | Rate at which foxes eat mice | 0.04 |
| -k | --diffusion-mice | Diffusion rate of mice | 0.2 |
| -b | --birth-foxes | Birth rate of foxes | 0.02 |
| -m | --death-foxes  | Rate at which foxes starve | 0.06 |
| -l | --diffusion-foxes | Diffusion rate of foxes | 0.2 |
| -dt | --delta-t | Time step size (seconds) | 0.4 |
| -t | --time_step | Number of time steps at which to output files | 10 |
| -d | --duration  | Time to run the simulation (seconds) | 500 |
| -ls | --landscape-seed | Random seed for initialising landscape | 1 |
| -lp | --landscape-prop | Average proportion of landscape that will initially be land | 0.75 |
| -lsm | --landscape-smooth | Number of smoothing passes after landscape initialization | 2 |
| -f | --animal-file | Input animal location file | - |

Example with custom parameters:

```bash
python -m predator_prey.simulate_predator_prey \
    -r 0.1 -a 0.05 -k 0.2 -b 0.03 \
    -m 0.09 -l 0.2 -dt 0.5 -t 10 \
    -d 500 -ls 1 -lp 0.75 -lsm 2 \
    -f animals/20x10.dat
```

### Input File Format

Animal location files are plain-text files with the following format:

* First line: `width height` (number of columns and rows)
* Subsequent lines: Grid of two-digit integers where the first digit represents the number of mice and the second digit represents the number of foxes

Example:
```
7 7
15 15 15 15 15 15 15
15 15 15 15 15 15 15
15 15 15 15 51 15 15
15 15 15 15 51 51 15
15 15 15 51 51 51 51
15 15 15 51 51 51 51
15 51 51 51 51 51 51
```

### Output Files

The simulation produces two types of output files:

1. **PPM Images** (`map_<NNNN>.ppm`): Visualizations of the animal densities at each output timestep
2. **CSV Data** (`averages.csv`): Statistical data showing the average animal densities over time

To view PPM files, you can use image viewing tools like ImageMagick:

```bash
display map_0010.ppm   # View a specific frame
animate map_*.ppm      # Animate all frames
```

## Performance Experiments

To run performance benchmarking experiments:

```bash
python -m performance_experiment.performance_experiment --help
```

See the [performance experiment README](performance_experiment/README.md) for detailed documentation.

## Running Tests

To run all tests:

```bash
pytest
```

To run a specific test:

```bash
pytest test/test_example.py
```

See the [test suite README](test/README.md) for more information.

## Author

s2659865  
April 2025