#!/usr/bin/env python3
"""
Find Jordan's full member record and look for ClubOS ID
"""

import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("=== JORDAN'S FULL MEMBER RECORD ===")

# Get Jordan's full record
cursor.execute("SELECT * FROM members WHERE first_name='Jordan' AND last_name='Krueger'")
jordan_row = cursor.fetchone()

if jordan_row:
    # Get column names
    cursor.execute("PRAGMA table_info(members)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"Jordan Krueger's full member record:")
    for i, value in enumerate(jordan_row):
        if value:  # Only show non-empty values
            print(f"  {columns[i]}: {value}")
    
    # Check if 160402199 appears anywhere
    print(f"\n🔍 Looking for ClubOS ID 160402199 in Jordan's record...")
    clubos_id = "160402199"
    found = False
    for i, value in enumerate(jordan_row):
        if value and str(value) == clubos_id:
            print(f"✅ FOUND ClubOS ID in column '{columns[i]}': {value}")
            found = True
    
    if not found:
        print("❌ ClubOS ID 160402199 not found in Jordan's member record")
        
    # Show Jordan's ClubHub ID for comparison
    print(f"\nJordan's ClubHub ID: {jordan_row[0]}")  # id column
    print(f"Jordan's ClubOS ID (from cache): 160402199")

else:
    print("❌ Jordan not found in members table")

# Also check Dennis
print(f"\n=== DENNIS'S MEMBER RECORD ===")
cursor.execute("SELECT id, first_name, last_name, guid, agreement_id FROM members WHERE first_name='DENNIS' AND last_name='ROST'")
dennis_row = cursor.fetchone()

if dennis_row:
    print(f"Dennis Rost:")
    print(f"  ClubHub ID: {dennis_row[0]}")
    print(f"  Name: {dennis_row[1]} {dennis_row[2]}")
    print(f"  GUID: {dennis_row[3]}")
    print(f"  Agreement ID: {dennis_row[4]}")
else:
    print("❌ Dennis not found in members table")

conn.close()
