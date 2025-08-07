#!/usr/bin/env python3
"""
Check database tables and Jordan's cached data
"""

import sqlite3

print("=== DATABASE INVESTIGATION ===")

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print(f"📊 All tables: {tables}")
print()

# Check training_package_cache table specifically
if 'training_package_cache' in tables:
    print("🔍 Checking training_package_cache table...")
    cursor.execute("SELECT * FROM training_package_cache WHERE participant_name LIKE '%Jordan%'")
    jordan_cache = cursor.fetchall()
    
    if jordan_cache:
        print(f"✅ Found Jordan's cached data:")
        for row in jordan_cache:
            print(f"  {row}")
    else:
        print("❌ No Jordan data in training_package_cache")
        
    # Check schema
    cursor.execute("PRAGMA table_info(training_package_cache)")
    schema = cursor.fetchall()
    print(f"\nTraining package cache schema:")
    for col in schema:
        print(f"  {col}")

# Look for any Jordan entries across all tables
print(f"\n🔍 Searching for Jordan across all tables...")
for table in tables:
    try:
        cursor.execute(f"SELECT * FROM {table} WHERE 1=0")  # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Look for text columns that might contain "Jordan"
        text_cols = []
        for col in columns:
            if any(keyword in col.lower() for keyword in ['name', 'participant', 'member', 'client']):
                text_cols.append(col)
        
        if text_cols:
            for col in text_cols:
                cursor.execute(f"SELECT * FROM {table} WHERE {col} LIKE '%Jordan%'")
                results = cursor.fetchall()
                if results:
                    print(f"✅ Found Jordan in table '{table}', column '{col}':")
                    for row in results:
                        print(f"  {row}")
                    
    except Exception as e:
        print(f"⚠️ Error checking table {table}: {e}")

conn.close()
print(f"\n✅ Investigation complete")
