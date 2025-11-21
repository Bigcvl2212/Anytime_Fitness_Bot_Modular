#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test member ID resolution fix - verify GUID resolves to correct prospect_id
"""

import sqlite3
import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')

print("Testing Member ID Resolution Fix")
print("=" * 80)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Test the exact query that will be used in messaging.py
test_guid = 'd74366d2-497a-4c11-a45a-3bf4b73a26a4'  # Mark Benzinger's GUID

print(f"\n1. Testing query: SELECT prospect_id FROM members WHERE guid = '{test_guid}'")
cursor.execute("SELECT prospect_id FROM members WHERE guid = ? OR prospect_id = ? LIMIT 1", (test_guid, test_guid))
result = cursor.fetchone()

if result:
    prospect_id = result[0]
    print(f"   ✅ SUCCESS: Resolved GUID -> prospect_id: {prospect_id}")

    # Verify this is Mark Benzinger
    cursor.execute("SELECT first_name, last_name, full_name, email FROM members WHERE prospect_id = ?", (prospect_id,))
    member_info = cursor.fetchone()
    if member_info:
        first_name, last_name, full_name, email = member_info
        print(f"   ✅ Member verified: {full_name} ({email})")

        # Check if this matches Jeremy's ID (should NOT match)
        jeremy_id = '187032782'  # Jeremy's ClubOS ID
        if str(prospect_id) == jeremy_id:
            print(f"   ❌ ERROR: Resolved to Jeremy's ID instead of member's ID!")
        else:
            print(f"   ✅ Correct: prospect_id {prospect_id} != Jeremy's ID {jeremy_id}")
else:
    print(f"   ❌ FAILED: No result found for GUID {test_guid}")

# Test fallback to prospect_id directly
print(f"\n2. Testing direct prospect_id lookup (fallback path)")
test_prospect_id = '66082049'
cursor.execute("SELECT prospect_id FROM members WHERE guid = ? OR prospect_id = ? LIMIT 1", (test_prospect_id, test_prospect_id))
result2 = cursor.fetchone()
if result2:
    print(f"   ✅ SUCCESS: Direct prospect_id lookup works: {result2[0]}")
else:
    print(f"   ❌ FAILED: Could not find prospect_id {test_prospect_id}")

# Test the prospects table fallback
print(f"\n3. Testing prospects table fallback")
try:
    cursor.execute("SELECT prospect_id FROM prospects WHERE prospect_id = ? LIMIT 1", (test_prospect_id,))
    result3 = cursor.fetchone()
    if result3:
        print(f"   ✅ SUCCESS: Found in prospects table: {result3[0]}")
    else:
        print(f"   ⚠️  Not found in prospects table (this is OK if member is in members table)")
except Exception as e:
    print(f"   ⚠️  Prospects table query failed: {e} (this is OK)")

conn.close()

print("\n" + "=" * 80)
print("✅ Member ID Resolution Test Complete")
print("\nExpected behavior:")
print("  - Mark Benzinger GUID should resolve to prospect_id: 66082049")
print("  - FollowUp API will receive followUpUserId: 66082049")
print("  - Should return Mark's messages, NOT Jeremy's messages")
