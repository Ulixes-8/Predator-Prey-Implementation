# #!/usr/bin/env python3
# """
# test_refactoring.py

# Comprehensive pytest-based unit and regression tests for refactoring the predator-prey simulation.
# This module ensures that all refactored versions (refactor_1.py, refactor_2.py, etc.) produce
# exactly the same outputs as the original simulate_predator_prey.py when given the same inputs.

# These tests focus on verifying output equivalence rather than program correctness,
# since the original program is already considered correct.

# Author: s2659865
# Date: April 2025
# """

# import os
# import sys
# import pytest
# import filecmp
# import tempfile
# import shutil
# import importlib.util
# import hashlib
# from io import StringIO
# from contextlib import contextmanager
# from typing import Dict, List, Tuple, Generator, Any, Callable

# # Define paths
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
# ANIMALS_DIR = os.path.join(PROJECT_ROOT, "animals")
# PERF_DIR = os.path.join(PROJECT_ROOT, "performance_experiment")

# # Import the original simulation
# sys.path.append(PROJECT_ROOT)
# from performance_experiment.baseline import sim as original_sim


# # ─── Test Utilities ────────────────────────────────────────────────────────────
# @contextmanager
# def captured_output() -> Generator[Tuple[StringIO, StringIO], None, None]:
#     """Capture stdout and stderr for testing."""
#     new_out, new_err = StringIO(), StringIO()
#     old_out, old_err = sys.stdout, sys.stderr
#     try:
#         sys.stdout, sys.stderr = new_out, new_err
#         yield new_out, new_err
#     finally:
#         sys.stdout, sys.stderr = old_out, old_err


# @contextmanager
# def temporary_directory() -> Generator[str, None, None]:
#     """Create a temporary directory for test outputs."""
#     temp_dir = tempfile.mkdtemp()
#     prev_dir = os.getcwd()
#     try:
#         os.chdir(temp_dir)
#         yield temp_dir
#     finally:
#         os.chdir(prev_dir)
#         shutil.rmtree(temp_dir)


# def load_refactored_implementation(refactor_name: str) -> Callable:
#     """Dynamically load a refactored implementation."""
#     refactor_path = os.path.join(PERF_DIR, f"{refactor_name}.py")
    
#     if not os.path.exists(refactor_path):
#         raise ImportError(f"Refactored implementation {refactor_name} not found at {refactor_path}")
    
#     spec = importlib.util.spec_from_file_location(refactor_name, refactor_path)
#     if spec is None or spec.loader is None:
#         raise ImportError(f"Failed to create module spec for {refactor_name}")
        
#     module = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(module)
    
#     # Check if the module has a sim function
#     if hasattr(module, 'sim'):
#         return module.sim
#     else:
#         raise ImportError(f"Module {refactor_name} does not have a sim function")


# def filter_stdout(stdout: str) -> List[str]:
#     """Filter stdout content to ignore lines that might legitimately differ."""
#     return [
#         line for line in stdout.strip().split('\n')
#         if "Predator-prey simulation" not in line  # Ignore version line
#         and "Averages. Timestep:" not in line  # Ignore timestamp lines
#     ]


# def compare_output_files(dir1: str, dir2: str) -> Dict[str, bool]:
#     """Compare output files between two directories."""
#     results = {
#         "csv_match": False,
#         "ppm_match": True  # Will be set to False if any PPM doesn't match
#     }
    
#     # Compare CSV files
#     if os.path.exists(os.path.join(dir1, "averages.csv")) and os.path.exists(os.path.join(dir2, "averages.csv")):
#         results["csv_match"] = filecmp.cmp(
#             os.path.join(dir1, "averages.csv"),
#             os.path.join(dir2, "averages.csv"),
#             shallow=False
#         )
    
#     # Find all PPM files in dir1
#     ppm_files = [f for f in os.listdir(dir1) if f.endswith(".ppm")]
    
#     # Compare each PPM file
#     for ppm_file in ppm_files:
#         if not os.path.exists(os.path.join(dir2, ppm_file)):
#             results["ppm_match"] = False
#             break
            
#         if not filecmp.cmp(
#             os.path.join(dir1, ppm_file),
#             os.path.join(dir2, ppm_file),
#             shallow=False
#         ):
#             results["ppm_match"] = False
#             break
    
#     return results


# def run_output_comparison(
#     original_sim_func: Callable, 
#     refactored_sim_func: Callable, 
#     args: Tuple
# ) -> Dict[str, Any]:
#     """Compare outputs from original and refactored simulations."""
#     # Run original implementation
#     with temporary_directory() as original_dir:
#         with captured_output() as (original_out, original_err):
#             original_sim_func(*args)
        
#         original_stdout = original_out.getvalue()
#         original_filtered_stdout = filter_stdout(original_stdout)
        
#         # Run refactored implementation
#         with temporary_directory() as refactored_dir:
#             with captured_output() as (refactored_out, refactored_err):
#                 refactored_sim_func(*args)
            
#             refactored_stdout = refactored_out.getvalue()
#             refactored_filtered_stdout = filter_stdout(refactored_stdout)
            
#             # Compare standard output
#             stdout_match = original_filtered_stdout == refactored_filtered_stdout
            
#             # Compare output files
#             file_comparison = compare_output_files(original_dir, refactored_dir)
            
#             # Determine overall match
#             all_match = stdout_match and file_comparison["csv_match"] and file_comparison["ppm_match"]
    
#     return {
#         "stdout_match": stdout_match,
#         "csv_match": file_comparison["csv_match"],
#         "ppm_match": file_comparison["ppm_match"],
#         "all_match": all_match
#     }


# def get_file_hash(file_path: str) -> str:
#     """Compute a hash of a file's contents."""
#     hasher = hashlib.md5()
#     with open(file_path, 'rb') as f:
#         buf = f.read()
#         hasher.update(buf)
#     return hasher.hexdigest()


# # ─── Test Fixtures ────────────────────────────────────────────────────────────
# @pytest.fixture
# def available_refactorings() -> List[str]:
#     """Return a list of available refactored implementations."""
#     refactorings = []
#     for i in range(1, 4):  # Check refactor_1, refactor_2, refactor_3
#         refactor_path = os.path.join(PERF_DIR, f"refactor_{i}.py")
#         if os.path.exists(refactor_path):
#             refactorings.append(f"refactor_{i}")
#     return refactorings


# @pytest.fixture
# def all_animal_files() -> List[str]:
#     """Return a list of all animal density files in the animals directory."""
#     files = []
#     for filename in os.listdir(ANIMALS_DIR):
#         if filename.endswith(".dat"):
#             files.append(os.path.join(ANIMALS_DIR, filename))
#     return files


# # ─── Core Tests ────────────────────────────────────────────────────────────
# class TestRefactoringCore:
#     """Core tests for all refactored implementations."""
    
#     def test_version_consistency(self, available_refactorings):
#         """Test that all implementations report the same version."""
#         from predator_prey.simulate_predator_prey import getVersion as original_get_version
        
#         # Check original version
#         assert original_get_version() == 4.0
        
#         # Check each refactored implementation
#         for refactor_name in available_refactorings:
#             # Import the module
#             spec = importlib.util.spec_from_file_location(
#                 refactor_name, 
#                 os.path.join(PERF_DIR, f"{refactor_name}.py")
#             )
#             assert spec is not None, f"Could not create spec for {refactor_name}"
#             assert spec.loader is not None, f"Could not create loader for {refactor_name}"
                
#             module = importlib.util.module_from_spec(spec)
#             spec.loader.exec_module(module)
            
#             # Test getVersion if it exists
#             assert hasattr(module, 'getVersion'), f"{refactor_name} is missing getVersion function"
#             assert module.getVersion() == 4.0, f"{refactor_name} reports incorrect version"
    
#     def test_cli_existence(self, available_refactorings):
#         """Test that all implementations maintain the command line interface."""
#         for refactor_name in available_refactorings:
#             # Import the module
#             spec = importlib.util.spec_from_file_location(
#                 refactor_name, 
#                 os.path.join(PERF_DIR, f"{refactor_name}.py")
#             )
#             assert spec is not None, f"Could not create spec for {refactor_name}"
#             assert spec.loader is not None, f"Could not create loader for {refactor_name}"
                
#             module = importlib.util.module_from_spec(spec)
#             spec.loader.exec_module(module)
            
#             # Test simCommLineIntf if it exists
#             assert hasattr(module, 'simCommLineIntf'), f"{refactor_name} is missing simCommLineIntf function"
#             assert callable(module.simCommLineIntf), f"{refactor_name} has non-callable simCommLineIntf"


# # ─── Refactoring Implementation Tests ─────────────────────────────────────────
# @pytest.mark.parametrize("refactor_name", ["refactor_1", "refactor_2", "refactor_3"])
# class TestRefactoringImplementation:
#     """Tests for individual refactored implementations."""
    
#     def test_implementation_exists(self, refactor_name):
#         """Test that the refactored implementation exists."""
#         refactor_path = os.path.join(PERF_DIR, f"{refactor_name}.py")
#         if not os.path.exists(refactor_path):
#             pytest.skip(f"Refactored implementation {refactor_name} not found")
    
#     def test_implementation_loadable(self, refactor_name):
#         """Test that the refactored implementation can be loaded."""
#         try:
#             refactored_sim = load_refactored_implementation(refactor_name)
#             assert callable(refactored_sim), f"{refactor_name}.sim is not callable"
#         except ImportError as e:
#             pytest.skip(f"Could not load {refactor_name}: {str(e)}")
    
#     def test_basic_execution(self, refactor_name):
#         """Test basic execution without errors."""
#         try:
#             refactored_sim = load_refactored_implementation(refactor_name)
#         except ImportError:
#             pytest.skip(f"Could not load {refactor_name}")
        
#         # Use a simple test case - hardcoded instead of using basic_parameters
#         args = (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50,
#                 os.path.join(ANIMALS_DIR, "3x3.dat"), 
#                 1, 0.75, 2)
        
#         with temporary_directory():
#             with captured_output():
#                 # This should not raise an exception
#                 refactored_sim(*args)


# # ─── Parameter Tests ────────────────────────────────────────────────────────
# @pytest.mark.parametrize("refactor_name", ["refactor_1", "refactor_2", "refactor_3"])
# @pytest.mark.parametrize("test_case", [
#     ("small_basic", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
#     ("medium_grid", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "performance_experiment_40x40.dat", 1, 0.75, 2),
#     ("large_grid", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "performance_experiment_80x80.dat", 1, 0.75, 2),
#     ("high_birth", 0.2, 0.05, 0.2, 0.1, 0.09, 0.2, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
#     ("zero_birth", 0.0, 0.05, 0.2, 0.0, 0.09, 0.2, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
#     ("high_predation", 0.1, 0.2, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
#     ("high_diffusion", 0.1, 0.05, 0.5, 0.03, 0.09, 0.5, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
#     ("zero_diffusion", 0.1, 0.05, 0.0, 0.03, 0.09, 0.0, 0.5, 10, 50, "3x3.dat", 1, 0.75, 2),
#     ("small_timestep", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.1, 10, 50, "3x3.dat", 1, 0.75, 2),
#     ("large_timestep", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 1.0, 10, 50, "3x3.dat", 1, 0.75, 2),
#     ("frequent_output", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 5, 50, "3x3.dat", 1, 0.75, 2),
#     ("single_cell", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "1x1.dat", 1, 0.75, 2),
#     ("only_mice", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "1x1prey.dat", 1, 0.75, 2),
#     ("only_foxes", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "1x1pred.dat", 1, 0.75, 2),
#     ("logo_pattern", 0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 50, "40x20ps.dat", 1, 0.75, 2),
# ])
# class TestParameterVariations:
#     """Tests for different parameter variations."""
    
#     def test_parameter_equivalence(self, refactor_name, test_case):
#         """Test that refactored implementations produce identical outputs with various parameters."""
#         refactor_path = os.path.join(PERF_DIR, f"{refactor_name}.py")
#         if not os.path.exists(refactor_path):
#             pytest.skip(f"Refactored implementation {refactor_name} not found")
        
#         name = test_case[0]
#         params = list(test_case[1:])
        
#         # Convert animal file path
#         params[9] = os.path.join(ANIMALS_DIR, params[9])
        
#         try:
#             refactored_sim = load_refactored_implementation(refactor_name)
#         except ImportError as e:
#             pytest.skip(f"Could not load {refactor_name}: {str(e)}")
        
#         # Run the comparison
#         results = run_output_comparison(original_sim, refactored_sim, tuple(params))
        
#         # Check results
#         assert results["stdout_match"], f"{refactor_name} produces different stdout for {name}"
#         assert results["csv_match"], f"{refactor_name} produces different CSV output for {name}"
#         assert results["ppm_match"], f"{refactor_name} produces different PPM output for {name}"


# # ─── Land and Landscape Tests ───────────────────────────────────────────────
# @pytest.mark.parametrize("refactor_name", ["refactor_1", "refactor_2", "refactor_3"])
# class TestLandscapeVariations:
#     """Tests for different landscape parameters."""
    
#     @pytest.mark.parametrize("land_prop", [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0])
#     def test_land_proportions(self, refactor_name, land_prop):
#         """Test a range of land proportions."""
#         refactor_path = os.path.join(PERF_DIR, f"{refactor_name}.py")
#         if not os.path.exists(refactor_path):
#             pytest.skip(f"Refactored implementation {refactor_name} not found")
            
#         try:
#             refactored_sim = load_refactored_implementation(refactor_name)
#         except ImportError as e:
#             pytest.skip(f"Could not load {refactor_name}: {str(e)}")
        
#         # Create args with the specified land proportion
#         args = (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 30,
#                os.path.join(ANIMALS_DIR, "3x3.dat"),
#                1, land_prop, 2)
        
#         # Run comparison
#         results = run_output_comparison(original_sim, refactored_sim, args)
        
#         # Check results
#         assert results["all_match"], (
#             f"{refactor_name} produces different output with land proportion {land_prop}")
    
#     @pytest.mark.parametrize("smoothing", [0, 1, 3, 5, 10])
#     def test_smoothing_passes(self, refactor_name, smoothing):
#         """Test a range of smoothing pass values."""
#         refactor_path = os.path.join(PERF_DIR, f"{refactor_name}.py")
#         if not os.path.exists(refactor_path):
#             pytest.skip(f"Refactored implementation {refactor_name} not found")
            
#         try:
#             refactored_sim = load_refactored_implementation(refactor_name)
#         except ImportError as e:
#             pytest.skip(f"Could not load {refactor_name}: {str(e)}")
        
#         # Create args with the specified smoothing passes
#         args = (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 30,
#                os.path.join(ANIMALS_DIR, "3x3.dat"),
#                1, 0.75, smoothing)
        
#         # Run comparison
#         results = run_output_comparison(original_sim, refactored_sim, args)
        
#         # Check results
#         assert results["all_match"], (
#             f"{refactor_name} produces different output with {smoothing} smoothing passes")


# # ─── Edge Cases and Stress Tests ─────────────────────────────────────────────
# @pytest.mark.parametrize("refactor_name", ["refactor_1", "refactor_2", "refactor_3"])
# class TestEdgeCases:
#     """Tests for edge cases and stress testing."""
    
#     @pytest.mark.parametrize("seed", [1, 42, 123, 456, 789, 999])
#     def test_random_seeds(self, refactor_name, seed):
#         """Test with multiple random seeds."""
#         refactor_path = os.path.join(PERF_DIR, f"{refactor_name}.py")
#         if not os.path.exists(refactor_path):
#             pytest.skip(f"Refactored implementation {refactor_name} not found")
            
#         try:
#             refactored_sim = load_refactored_implementation(refactor_name)
#         except ImportError as e:
#             pytest.skip(f"Could not load {refactor_name}: {str(e)}")
        
#         # Create args with the specified seed
#         args = (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 30,
#                os.path.join(ANIMALS_DIR, "3x3.dat"),
#                seed, 0.75, 2)
        
#         # Run comparison
#         results = run_output_comparison(original_sim, refactored_sim, args)
        
#         # Check results
#         assert results["all_match"], f"{refactor_name} produces different output with seed {seed}"
    
# @pytest.mark.parametrize("refactor_name", ["refactor_1", "refactor_2", "refactor_3"])
# @pytest.mark.parametrize("test_case,args", [
#     ("explosive_growth", (0.5, 0.01, 0.2, 0.5, 0.01, 0.2, 0.5, 10, 30,
#                           "3x3.dat", 1, 0.75, 2)),
#     ("population_crash", (0.01, 0.5, 0.2, 0.01, 0.5, 0.2, 0.5, 10, 30,
#                           "3x3.dat", 1, 0.75, 2)),
#     ("rapid_diffusion", (0.1, 0.05, 0.9, 0.03, 0.09, 0.9, 0.5, 10, 30,
#                          "3x3.dat", 1, 0.75, 2)),
#     ("tiny_timestep", (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.01, 10, 30,
#                        "3x3.dat", 1, 0.75, 2)),
#     ("sparse_landscape", (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 30,
#                           "performance_experiment_20x20.dat", 1, 0.1, 2))
# ])
# class TestExtremeParameters:
#     """Tests for extreme parameter combinations."""
    
#     def test_extreme_cases(self, refactor_name, test_case, args):
#         """Test extreme parameter combinations."""
#         refactor_path = os.path.join(PERF_DIR, f"{refactor_name}.py")
#         if not os.path.exists(refactor_path):
#             pytest.skip(f"Refactored implementation {refactor_name} not found")
            
#         try:
#             refactored_sim = load_refactored_implementation(refactor_name)
#         except ImportError as e:
#             pytest.skip(f"Could not load {refactor_name}: {str(e)}")
        
#         # Convert animal file path
#         args_list = list(args)
#         args_list[9] = os.path.join(ANIMALS_DIR, args_list[9])
#         updated_args = tuple(args_list)
        
#         # Run comparison
#         results = run_output_comparison(original_sim, refactored_sim, updated_args)
        
#         # Check results
#         assert results["all_match"], (
#             f"{refactor_name} produces different output for extreme case {test_case}")
    
# @pytest.mark.parametrize("refactor_name", ["refactor_1", "refactor_2", "refactor_3"])
# class TestDeterminism:
#     """Tests for simulation determinism."""
    
#     def test_determinism(self, refactor_name):
#         """Test determinism with the same inputs."""
#         refactor_path = os.path.join(PERF_DIR, f"{refactor_name}.py")
#         if not os.path.exists(refactor_path):
#             pytest.skip(f"Refactored implementation {refactor_name} not found")
            
#         try:
#             refactored_sim = load_refactored_implementation(refactor_name)
#         except ImportError as e:
#             pytest.skip(f"Could not load {refactor_name}: {str(e)}")
        
#         # Simple test case
#         test_args = (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 30,
#                      os.path.join(ANIMALS_DIR, "3x3.dat"),
#                      1, 0.75, 2)
        
#         # Run the original simulation once
#         with temporary_directory() as dir1:
#             with captured_output():
#                 original_sim(*test_args)
            
#             # Save the CSV hash
#             original_csv_hash = get_file_hash(os.path.join(dir1, "averages.csv"))
            
#             # Run the refactored simulation twice
#             with temporary_directory() as dir2:
#                 with captured_output():
#                     refactored_sim(*test_args)
                
#                 refactored_csv_hash1 = get_file_hash(os.path.join(dir2, "averages.csv"))
                
#                 with temporary_directory() as dir3:
#                     with captured_output():
#                         refactored_sim(*test_args)
                    
#                     refactored_csv_hash2 = get_file_hash(os.path.join(dir3, "averages.csv"))
        
#         # All hashes should match, confirming determinism
#         assert original_csv_hash == refactored_csv_hash1, (
#             f"{refactor_name} doesn't match original simulation")
        
#         assert refactored_csv_hash1 == refactored_csv_hash2, (
#             f"{refactor_name} is not deterministic with the same inputs")


# # ─── File Tests ────────────────────────────────────────────────────────────
# class TestInputFiles:
#     """Tests for different input files."""
    
#     def test_all_animal_files(self, available_refactorings, all_animal_files):
#         """Test all available animal files with default parameters."""
#         if not available_refactorings:
#             pytest.skip("No refactored implementations available")
        
#         # Pick the first available refactored implementation
#         refactor_name = available_refactorings[0]
#         refactored_sim = load_refactored_implementation(refactor_name)
        
#         # Default parameters excluding the animal file
#         default_args_prefix = (0.1, 0.05, 0.2, 0.03, 0.09, 0.2, 0.5, 10, 30)
#         default_args_suffix = (1, 0.75, 2)
        
#         # Test each animal file
#         for animal_file in all_animal_files:
#             # Skip very large files to keep test duration reasonable
#             file_size = os.path.getsize(animal_file)
#             if file_size > 10000*100:  # Skip files larger than ~1000KB
#                 continue
                
#             # Create full args tuple with this animal file
#             args = default_args_prefix + (animal_file,) + default_args_suffix
            
#             # Run comparison
#             print(f"Testing file: {os.path.basename(animal_file)}")
#             results = run_output_comparison(original_sim, refactored_sim, args)
            
#             # Check results
#             file_name = os.path.basename(animal_file)
#             assert results["stdout_match"], f"Different stdout for {file_name}"
#             assert results["csv_match"], f"Different CSV output for {file_name}"
#             assert results["ppm_match"], f"Different PPM output for {file_name}"