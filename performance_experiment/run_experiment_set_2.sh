#!/bin/bash
# run_experiment_set_2.sh
# Runs selected experiments for specified implementations

# First: Run grid for refactor_2 and refactor_3
implementations_grid=("refactor_2" "refactor_3")
experiment_grid="grid"

for impl in "${implementations_grid[@]}"; do
  echo "====================================================="
  echo "Running '$experiment_grid' experiment using '$impl' implementation..."
  echo "====================================================="
  python performance_experiment.py --implementation "$impl" --experiments "$experiment_grid"
  echo ""
done

# Then: Run cpu for refactor_3 only
impl_cpu="refactor_3"
experiment_cpu="cpu"

echo "====================================================="
echo "Running '$experiment_cpu' experiment using '$impl_cpu' implementation..."
echo "====================================================="
python performance_experiment.py --implementation "$impl_cpu" --experiments "$experiment_cpu"
echo ""

echo "====================================================="
echo "All experiments completed."
echo "====================================================="
# End of script
