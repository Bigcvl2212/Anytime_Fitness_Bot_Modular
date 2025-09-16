#!/usr/bin/env python3
"""
Fix PostgreSQL schema by adding missing full_name column to member_categories table
"""

import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    host='34.31.91.96',
    port=5432,
    database='gym_bot',
    user='postgres',
    password='GymBot2025!',
    sslmode='require'
)

try:
    cur = conn.cursor()
    
    # Check if full_name column exists
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'member_categories' AND column_name = 'full_name'
    """)
    
    result = cur.fetchone()
    if result:
        print("✅ full_name column already exists in member_categories table")
    else:
        print("🔧 Adding missing full_name column to member_categories table...")
        cur.execute("ALTER TABLE member_categories ADD COLUMN full_name TEXT")
        conn.commit()
        print("✅ Successfully added full_name column")
    
    # Also add created_at and updated_at columns if missing
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'member_categories' AND column_name IN ('created_at', 'updated_at')
    """)
    
    existing_cols = [row[0] for row in cur.fetchall()]
    
    if 'created_at' not in existing_cols:
        print("🔧 Adding created_at column...")
        cur.execute("ALTER TABLE member_categories ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
    if 'updated_at' not in existing_cols:
        print("🔧 Adding updated_at column...")
        cur.execute("ALTER TABLE member_categories ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    
    conn.commit()
    
    # Show current table structure
    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'member_categories'
        ORDER BY ordinal_position
    """)
    
    columns = cur.fetchall()
    print("\n📋 Current member_categories table structure:")
    for col in columns:
        print(f"  {col[0]} ({col[1]}) - nullable: {col[2]}, default: {col[3]}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()

print("✅ Schema fix complete!")