#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check if columns exist
cursor.execute("PRAGMA table_info(members)")
columns = [col[1] for col in cursor.fetchall()]
print("Available columns:", columns)

# Check for calculated fields
if 'base_amount_past_due' in columns and 'late_fees' in columns and 'missed_payments' in columns:
    print("\n✅ Calculated fields exist in database")
    
    # Check a sample member
    cursor.execute("SELECT full_name, amount_past_due, base_amount_past_due, late_fees, missed_payments FROM members WHERE full_name LIKE '%MICHAEL BURNETT%' LIMIT 1")
    result = cursor.fetchone()
    if result:
        print(f"Sample member: {result}")
    else:
        print("No members found with 'MICHAEL BURNETT' in name")
        
    # Check how many members have non-zero calculated fields
    cursor.execute("SELECT COUNT(*) FROM members WHERE base_amount_past_due > 0 OR late_fees > 0 OR missed_payments > 0")
    count = cursor.fetchone()[0]
    print(f"Members with calculated data: {count}")
    
else:
    print("\n❌ Calculated fields missing from database")
    missing = []
    for field in ['base_amount_past_due', 'late_fees', 'missed_payments']:
        if field not in columns:
            missing.append(field)
    print(f"Missing fields: {missing}")

conn.close()
