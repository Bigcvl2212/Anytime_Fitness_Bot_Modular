#!/usr/bin/env python3
"""Check database state right now"""

import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check past due with addresses
cursor.execute("""
    SELECT full_name, address, city, state, zip_code, 
           amount_past_due, status_message
    FROM members
    WHERE amount_past_due > 0
    ORDER BY amount_past_due DESC
    LIMIT 10
""")

print("🔍 Top 10 Past Due Members WITH ADDRESSES:\n")
for row in cursor.fetchall():
    name, addr, city, state, zip_code, amount, status = row
    print(f"💰 {name}: ${amount:.2f}")
    print(f"   Status: {status}")
    if addr:
        print(f"   📍 {addr}, {city}, {state} {zip_code}")
    else:
        print(f"   ⚠️ NO ADDRESS (only city: {city})")
    print()

# Summary
cursor.execute("SELECT COUNT(*) FROM members WHERE amount_past_due > 0")
past_due_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM members WHERE amount_past_due > 0 AND address IS NOT NULL AND address != ''")
past_due_with_address = cursor.fetchone()[0]

print(f"\n📊 SUMMARY:")
print(f"   Past due members: {past_due_count}")
print(f"   Past due WITH addresses: {past_due_with_address} ({100*past_due_with_address/past_due_count if past_due_count > 0 else 0:.1f}%)")

conn.close()
