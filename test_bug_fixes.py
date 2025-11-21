#!/usr/bin/env python3
"""Test the bug fixes for Phase 2 tools"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.ai.agent_tools.collections_tools import get_past_due_members, get_past_due_training_clients
from src.services.ai.agent_tools.campaign_tools import get_ppv_members

print("=" * 70)
print("TESTING BUG FIXES")
print("=" * 70)

# Test 1: get_past_due_members (sqlite3.Row .get() error)
print("\n1. Testing get_past_due_members (sqlite3.Row fix)...")
try:
    result = get_past_due_members()
    print(f"   ✅ Success: {result['success']}")
    print(f"   Count: {result['count']}")
    print(f"   Total amount: ${result.get('total_amount', 0):.2f}")
    if result.get('error'):
        print(f"   ⚠️ Error: {result['error']}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Test 2: get_past_due_training_clients (column name fix)
print("\n2. Testing get_past_due_training_clients (column name fix)...")
try:
    result = get_past_due_training_clients()
    print(f"   ✅ Success: {result['success']}")
    print(f"   Count: {result['count']}")
    print(f"   Total amount: ${result.get('total_amount', 0):.2f}")
    if result.get('error'):
        print(f"   ⚠️ Error: {result['error']}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Test 3: get_ppv_members (missing filters parameter)
print("\n3. Testing get_ppv_members with filters parameter...")
try:
    result = get_ppv_members(filters={'test': 'value'})
    print(f"   ✅ Success: {result['success']}")
    print(f"   Count: {result['count']}")
    if result.get('error'):
        print(f"   ⚠️ Error: {result['error']}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETE")
print("=" * 70)
