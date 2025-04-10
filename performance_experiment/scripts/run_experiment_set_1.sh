#!/bin/bash
# run_experiment_set_1.sh
# Runs grid, landscape, and matrix experiments for selected implementations

# Change to the project root directory
cd "$(dirname "$0")/.."

# List of implementations
implementations=("baseline" "refactor_1" "refactor_2" "refactor_3")

# List of experiments to run
experiments=("grid" "landscape" "matrix")

# Run each experiment for each implementation
for impl in "${implementations[@]}"; do
  for exp in "${experiments[@]}"; do
    echo "====================================================="
    echo "Running '$exp' experiment using '$impl' implementation..."
    echo "====================================================="
    python -m performance_experiment.performance_experiment --implementation "$impl" --experiments "$exp"
    echo ""
  done
done
echo "====================================================="
echo "All experiments completed."
echo "====================================================="
# End of script