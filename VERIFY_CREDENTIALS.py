#!/usr/bin/env python3
"""
Verification Script: Check where Flask is actually getting credentials from
Run this to confirm the fix worked
"""

import os
import sys
from pathlib import Path

# Check current environment
print("=" * 80)
print("CREDENTIAL VERIFICATION SCRIPT")
print("=" * 80)
print()

# 1. Check what's in the .env file
print("1. CHECKING .env FILE")
print("-" * 80)
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            if 'CLUBOS_PASSWORD' in line:
                print("Line {}: {}".format(i, line.strip()))
else:
    print("NOT FOUND: .env file not found!")
print()

# 2. Check what's in os.environ (BEFORE loading .env)
print("2. SYSTEM ENVIRONMENT (before loading .env)")
print("-" * 80)
env_password = os.environ.get('CLUBOS_PASSWORD', 'NOT SET')
print("os.environ['CLUBOS_PASSWORD'] = {}".format(env_password))
print()

# 3. Try to load .env using python-dotenv
print("3. LOADING .env FILE")
print("-" * 80)
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print("OK: Successfully loaded {}".format(env_file))
    else:
        print("NOT FOUND: .env file not found at {}".format(env_file))
except ImportError:
    print("ERROR: python-dotenv not installed!")
print()

# 4. Check what's in os.environ (AFTER loading .env)
print("4. SYSTEM ENVIRONMENT (after loading .env)")
print("-" * 80)
env_password = os.environ.get('CLUBOS_PASSWORD', 'NOT SET')
print("os.environ['CLUBOS_PASSWORD'] = {}".format(env_password))
print()

# 5. Check secrets_local.py
print("5. CHECKING secrets_local.py")
print("-" * 80)
try:
    sys.path.insert(0, str(Path(__file__).parent / 'config'))
    from secrets_local import get_secret
    local_password = get_secret('clubos-password')
    print("secrets_local.py['clubos-password'] = {}".format(local_password))
except ImportError as e:
    print("ERROR: Could not import secrets_local.py: {}".format(e))
print()

# 7. Verify correct password
print("6. CREDENTIAL VERIFICATION")
print("-" * 80)
correct_password = "Ls$gpZ98L!hht.G"
wrong_password = "W-!R6Bv9FgPnuB4"

print("Expected password: {}".format(correct_password))
print("Wrong password:    {}".format(wrong_password))
print()

env_password = os.environ.get('CLUBOS_PASSWORD', 'NOT SET')
if env_password == correct_password:
    print("OK: Environment has the correct password")
elif env_password == wrong_password:
    print("ERROR: Environment has the WRONG password from .env file")
else:
    print("WARNING: Environment has unexpected password: {}".format(env_password))
print()

# 8. Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("Current .env password: {}".format(env_password))
print()
if env_password == correct_password:
    print("FIX STATUS: WORKING - .env file has correct password")
elif env_password == wrong_password:
    print("FIX STATUS: NEEDED - .env file still has old password")
    print()
    print("TO FIX:")
    print("1. Edit .env file")
    print("2. Find line: CLUBOS_PASSWORD=W-!R6Bv9FgPnuB4")
    print("3. Change to: CLUBOS_PASSWORD=Ls$gpZ98L!hht.G")
    print("4. Save file and restart Flask")
else:
    print("FIX STATUS: UNKNOWN")
print()

