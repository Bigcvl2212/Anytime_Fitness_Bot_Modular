#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check members table schema to find correct column for ClubOS numeric member ID
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

print(f"Checking database: {db_path}")
print("=" * 80)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get members table schema
print("\nMEMBERS TABLE SCHEMA:")
print("-" * 80)
cursor.execute("PRAGMA table_info(members)")
columns = cursor.fetchall()

for col in columns:
    col_id, name, col_type, not_null, default_val, pk = col
    print(f"  {col_id:2d}. {name:30s} {col_type:15s} {'NOT NULL' if not_null else ''} {'PRIMARY KEY' if pk else ''}")

# Check if there are any members with data to see column values
print("\n\nSAMPLE MEMBER DATA (First 3 rows):")
print("-" * 80)
cursor.execute("SELECT * FROM members LIMIT 3")
sample_rows = cursor.fetchall()

if sample_rows:
    # Get column names
    col_names = [desc[0] for desc in cursor.description]

    for i, row in enumerate(sample_rows, 1):
        print(f"\nMember {i}:")
        for col_name, value in zip(col_names, row):
            # Only show key identification columns
            if col_name in ['id', 'guid', 'name', 'first_name', 'last_name', 'member_id', 'clubos_id', 'prospect_id', 'email']:
                print(f"  {col_name:20s} = {value}")
else:
    print("  (No members found in database)")

# Specifically look for Mark Benzinger
print("\n\nSEARCHING FOR MARK BENZINGER:")
print("-" * 80)
cursor.execute("""
    SELECT * FROM members
    WHERE guid = 'd74366d2-497a-4c11-a45a-3bf4b73a26a4'
       OR full_name LIKE '%Mark%Benzinger%'
       OR first_name LIKE '%Mark%'
    LIMIT 1
""")
mark_row = cursor.fetchone()

if mark_row:
    col_names = [desc[0] for desc in cursor.description]
    print("\nFound Mark Benzinger! All columns:")
    for col_name, value in zip(col_names, mark_row):
        print(f"  {col_name:30s} = {value}")
else:
    print("  Mark Benzinger not found in members table")

    # Check prospects table as fallback
    print("\n  Checking prospects table...")
    try:
        cursor.execute("""
            SELECT * FROM prospects
            WHERE guid = 'd74366d2-497a-4c11-a45a-3bf4b73a26a4'
               OR full_name LIKE '%Mark%Benzinger%'
            LIMIT 1
        """)
    except sqlite3.OperationalError as e:
        print(f"    Error querying prospects: {e}")
        cursor.execute("""
            SELECT * FROM prospects
            WHERE guid = 'd74366d2-497a-4c11-a45a-3bf4b73a26a4'
            LIMIT 1
        """)
    prospect_row = cursor.fetchone()

    if prospect_row:
        col_names = [desc[0] for desc in cursor.description]
        print("\n  Found in prospects table! All columns:")
        for col_name, value in zip(col_names, prospect_row):
            print(f"    {col_name:30s} = {value}")

conn.close()

print("\n" + "=" * 80)
print("OK: Schema check complete")
