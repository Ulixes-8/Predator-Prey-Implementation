# Predator-Prey Simulation Test Suite

## Overview

This directory contains comprehensive tests for verifying the correctness of the predator-prey simulation and its refactored implementations. The tests ensure that all implementations produce identical results and maintain interface compatibility.

## Directory Structure

```
test/
├── __init__.py                  # Package initialization
├── test_example.py              # Simple example test (required by instructor)
├── conftest.py                  # Test configuration and shared fixtures
├── test_runner.py               # Main script to run all tests
├── core/                        # Tests for core functionality
│   ├── test_core.py             # Tests for basic interfaces and functionality
├── implementations/             # Tests for implementation correctness
│   ├── test_parameters.py       # Tests with various parameter combinations
│   ├── test_landscape.py        # Tests for landscape parameters
│   └── test_edge_cases.py       # Tests for extreme parameters and edge cases
├── io/                          # Tests for input/output
│   └── test_input_files.py      # Tests with different input files
└── utils/                       # Test utilities
    ├── test_utilities.py        # Shared test utilities
    └── test_fixtures.py         # Shared pytest fixtures
```

## Running Tests

### Running All Tests

To run all tests:

```bash
pytest
```

or use the test runner script:

```bash
python -m test.test_runner
```

### Running the Simple Example Test

To run just the example test (as required by the instructor):

```bash
pytest test/test_example.py
```

### Running Specific Test Categories

To run tests in a specific category:

```bash
pytest test/core/
pytest test/implementations/
pytest test/io/
```

### Running a Specific Test File

To run a specific test file:

```bash
pytest test/core/test_core.py
```

### Running a Specific Test

To run a specific test function or class:

```bash
pytest test/core/test_core.py::TestRefactoringCore
pytest test/core/test_core.py::TestRefactoringCore::test_version_consistency
```

## Test Categories

| Category | Description |
|----------|-------------|
| `core` | Verifies basic interfaces and functionality across implementations |
| `implementations` | Tests different parameter combinations and edge cases |
| `io` | Tests with various input files and output verification |

## Key Features

- **Automated Output Comparison**: Tests automatically compare outputs between the original and refactored implementations
- **Comprehensive Parameter Testing**: Tests various parameter combinations to ensure full compatibility
- **Edge Case Handling**: Tests extreme parameters and edge cases
- **Input File Compatibility**: Tests with different animal density files
- **Determinism Verification**: Ensures that implementations produce consistent results across multiple runs

## Adding New Tests

To add a new test:

1. Determine the appropriate category (core, implementations, io)
2. Create a new test file or add to an existing one
3. Use utilities from `test.utils.test_utilities` for consistent testing
4. Import fixtures from `conftest.py` or `test.utils.test_fixtures`

## Utilities and Fixtures

- `test_utilities.py`: Provides functions for capturing output, comparing results, and loading implementations
- `test_fixtures.py`: Provides pytest fixtures like `available_refactorings` and `all_animal_files`
- `conftest.py`: Makes fixtures globally available to all test modules

## Author

s2659865  
April 2025