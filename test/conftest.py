#!/usr/bin/env python3
"""
conftest.py

Configuration file for pytest to share fixtures across all test modules.
This file imports and reexports the fixtures from test_fixtures.py to make
them available to all test modules without explicit imports.

Author: s2659865
Date: April 2025
"""

import os
import sys

# Add the current directory to the path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import fixtures to make them available globally
from test.utils.test_fixtures import available_refactorings, all_animal_files