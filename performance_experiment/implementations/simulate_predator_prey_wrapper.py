"""
Wrapper module for running performance experiments on the main predator-prey simulation.

This module provides a compatibility layer between the performance experiment
framework and the main simulate_predator_prey.py implementation.

Author: s2659865
Date: April 2025
"""

import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

# Import the main implementation
from predator_prey.simulate_predator_prey import getVersion, simCommLineIntf, sim

# This module wraps the main simulate_predator_prey.py implementation
# to allow it to be used in the performance experiment framework
# alongside the refactored implementations (refactor_1.py, refactor_2.py, etc.)

# All functions are directly re-exported from the main implementation
# No modifications are made to ensure accurate performance measurements