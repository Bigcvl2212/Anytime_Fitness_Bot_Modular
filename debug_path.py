#!/usr/bin/env python3
"""
Debug path calculation issue
"""

import os
import sys

# Test our path calculation from staff_designations.py
test_file = r"c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\src\utils\staff_designations.py"

print(f"Test file: {test_file}")
print(f"dirname(test_file): {os.path.dirname(test_file)}")
print(f"dirname(dirname(test_file)): {os.path.dirname(os.path.dirname(test_file))}")

# This is what the function does:
project_root = os.path.dirname(os.path.dirname(test_file))
expected_db = os.path.join(project_root, 'gym_bot.db')
print(f"Expected DB path: {expected_db}")
print(f"DB exists at that path: {os.path.exists(expected_db)}")

# What we actually need:
actual_project_root = r"c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular"
actual_db = os.path.join(actual_project_root, 'gym_bot.db')
print(f"Actual project root: {actual_project_root}")
print(f"Actual DB path: {actual_db}")
print(f"DB exists at actual path: {os.path.exists(actual_db)}")

# Show directory structure
print(f"\nDirectory structure check:")
print(f"src dir exists: {os.path.exists(os.path.join(actual_project_root, 'src'))}")
print(f"utils dir exists: {os.path.exists(os.path.join(actual_project_root, 'src', 'utils'))}")
print(f"staff_designations.py exists: {os.path.exists(os.path.join(actual_project_root, 'src', 'utils', 'staff_designations.py'))}")