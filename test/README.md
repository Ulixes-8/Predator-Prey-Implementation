# Predator-Prey Simulation Refactoring Tests

This directory contains comprehensive tests for verifying that refactored versions of the predator-prey simulation produce identical outputs to the original implementation.

## Test Structure

The test suite is organized in multiple modules:

- `test_utilities.py`: Utility functions for capturing output, loading modules, etc.
- `test_fixtures.py`: Common pytest fixtures and parameter sets
- `test_core.py`: Tests for basic interfaces and functionality
- `test_parameters.py`: Tests for simulation parameters
- `test_landscape.py`: Tests for landscape parameters
- `test_edge_cases.py`: Tests for edge cases and extreme parameters
- `test_input_files.py`: Tests for processing different input files
- `conftest.py`: Makes fixtures available to all test modules
- `test_runner.py`: Main script to run all tests

## Running Tests

To run all tests:

```bash
python test_runner.py
```

To run a specific test module:

```bash
python -m pytest test_core.py -v
```

To run tests for a specific refactored implementation:

```bash
python -m pytest -k "refactor_1" -v
```

## Test Coverage

These tests verify:

1. **Interface Consistency**: Ensuring all refactored versions maintain the same API
2. **Functional Correctness**: Confirming output equivalence with the original implementation
3. **Parameter Space**: Testing across a wide range of parameter combinations
4. **Landscape Settings**: Validating land proportions and smoothing passes
5. **Edge Cases**: Testing extreme parameter values
6. **Determinism**: Verifying consistent results given the same inputs
7. **Input Variation**: Testing with different animal density files

## Author

s2659865
April 2025