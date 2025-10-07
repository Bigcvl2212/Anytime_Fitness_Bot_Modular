#!/usr/bin/env python3
"""Quick verification that addresses are in database"""

import sqlite3

# Connect to database
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check address status
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN address IS NOT NULL AND address != '' THEN 1 END) as with_address,
        COUNT(CASE WHEN status_message LIKE '%Past Due%' THEN 1 END) as past_due
    FROM members
""")

total, with_address, past_due = cursor.fetchone()

print(f"Total members: {total}")
print(f"With addresses: {with_address} ({100*with_address/total if total > 0 else 0:.1f}%)")
print(f"Past due members: {past_due}")

# Show sample past due members with addresses
cursor.execute("""
    SELECT full_name, address, city, state, zip_code, amount_past_due
    FROM members
    WHERE status_message LIKE '%Past Due%'
    ORDER BY amount_past_due DESC
    LIMIT 5
""")

print("\n🔍 Sample past due members:")
for row in cursor.fetchall():
    name, addr, city, state, zip_code, amount = row
    print(f"  {name}: ${amount:.2f}")
    if addr:
        print(f"    {addr}, {city}, {state} {zip_code}")
    else:
        print(f"    ⚠️ NO ADDRESS - only city: {city}")

conn.close()
