#!/usr/bin/env python3
"""
Check the training_clients database to see how Jordan's ID mapping works
"""

import sqlite3
import sys
import os

print("=== DATABASE ID MAPPING INVESTIGATION ===")

# Connect to the database
db_path = "gym_bot.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"🔍 Checking training_clients table...")

# Check what's in the training_clients table
cursor.execute("SELECT id, clubos_member_id, member_name, first_name, last_name FROM training_clients")
rows = cursor.fetchall()

print(f"📊 Found {len(rows)} training clients in database:")
print()

for row in rows:
    id_val, clubos_id, name, first, last = row
    print(f"ID: {id_val}")
    print(f"  ClubOS Member ID: {clubos_id}")
    print(f"  Member Name: {name}")
    print(f"  First: {first}, Last: {last}")
    print()

# Now check if we can find Jordan specifically
print("🔍 Looking for Jordan Krueger specifically...")
cursor.execute("SELECT * FROM training_clients WHERE member_name LIKE '%Jordan%' OR first_name LIKE '%Jordan%'")
jordan_rows = cursor.fetchall()

if jordan_rows:
    print(f"✅ Found Jordan in training_clients:")
    for row in jordan_rows:
        print(f"  Full row: {row}")
else:
    print("❌ Jordan not found in training_clients table")

# Check if Dennis is there
print("\n🔍 Looking for Dennis Rost...")
cursor.execute("SELECT * FROM training_clients WHERE member_name LIKE '%Dennis%' OR first_name LIKE '%Dennis%'")
dennis_rows = cursor.fetchall()

if dennis_rows:
    print(f"✅ Found Dennis in training_clients:")
    for row in dennis_rows:
        print(f"  Full row: {row}")
else:
    print("❌ Dennis not found in training_clients table")

# Also check the members table for comparison
print(f"\n=== MEMBERS TABLE COMPARISON ===")
cursor.execute("SELECT id, first_name, last_name FROM members WHERE first_name LIKE '%Jordan%' OR first_name LIKE '%Dennis%'")
member_rows = cursor.fetchall()

print(f"Members table entries:")
for row in member_rows:
    print(f"  ClubHub ID: {row[0]}, Name: {row[1]} {row[2]}")

conn.close()
print(f"\n✅ Database investigation complete")
