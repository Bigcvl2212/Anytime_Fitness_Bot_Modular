#!/usr/bin/env python3
import sqlite3

# Connect to database
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Search for Alexander by email since names appear to be None
email_queries = [
    "SELECT id, first_name, last_name, email FROM members WHERE email LIKE '%alex%'",
    "SELECT id, first_name, last_name, email FROM members WHERE email LIKE '%ovan%'", 
    "SELECT id, first_name, last_name, email FROM members WHERE email LIKE '%alexander%'"
]

print("🔍 Searching for Alexander Ovanin by email patterns...")
found_any = False

for i, query in enumerate(email_queries):
    print(f"\nEmail Query {i+1}: {query}")
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        found_any = True
        print(f"✅ Found {len(results)} results:")
        for r in results:
            print(f"  ID: {r[0]} | Name: {r[1]} {r[2]} | Email: {r[3]}")
    else:
        print("❌ No results")

# Also check if we have any CSV data with actual names
print("\n🔍 Checking CSV imports for name data...")
try:
    import pandas as pd
    import glob
    
    csv_files = glob.glob("data/csv_exports/*.csv")
    print(f"Found {len(csv_files)} CSV files")
    
    for csv_file in csv_files:
        if "master_contact" in csv_file:
            print(f"\n📁 Checking {csv_file}...")
            df = pd.read_csv(csv_file)
            
            # Look for Alexander in any name columns
            if 'first_name' in df.columns or 'First Name' in df.columns:
                name_col = 'first_name' if 'first_name' in df.columns else 'First Name'
                alex_rows = df[df[name_col].str.contains('Alex', case=False, na=False)]
                if not alex_rows.empty:
                    print(f"✅ Found Alexander in {csv_file}:")
                    print(alex_rows.to_string())
                    
except Exception as e:
    print(f"❌ Error checking CSV files: {e}")

conn.close()
