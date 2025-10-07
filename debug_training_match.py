#!/usr/bin/env python3
"""Check why training clients aren't matching members"""

import sqlite3

conn = sqlite3.connect('gym_bot.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get training clients with past due
cursor.execute("""
    SELECT prospect_id, clubos_member_id, member_name, email, phone, address
    FROM training_clients 
    WHERE total_past_due > 0 
    LIMIT 5
""")
training = cursor.fetchall()

print("🔍 TRAINING CLIENTS (past due):")
for t in training:
    print(f"\n  Name: {t['member_name']}")
    print(f"  prospect_id: {t['prospect_id']}")
    print(f"  clubos_member_id: {t['clubos_member_id']}")
    print(f"  email in tc: {t['email']}")
    print(f"  phone in tc: {t['phone']}")
    print(f"  address in tc: {t['address']}")
    
    # Try to find matching member
    cursor.execute("""
        SELECT prospect_id, guid, full_name, email, phone, mobile_phone, address
        FROM members
        WHERE prospect_id = ? OR guid = ?
    """, (t['prospect_id'], t['clubos_member_id']))
    
    match = cursor.fetchone()
    if match:
        print(f"  ✅ FOUND MEMBER MATCH:")
        print(f"     Member name: {match['full_name']}")
        print(f"     Member email: {match['email']}")
        print(f"     Member phone: {match['phone'] or match['mobile_phone']}")
        print(f"     Member address: {match['address']}")
    else:
        print(f"  ❌ NO MEMBER MATCH FOUND")
        
        # Try fuzzy name match
        name = t['member_name']
        cursor.execute("""
            SELECT prospect_id, guid, full_name, email, phone, mobile_phone, address
            FROM members
            WHERE LOWER(full_name) = LOWER(?)
            LIMIT 1
        """, (name,))
        
        fuzzy = cursor.fetchone()
        if fuzzy:
            print(f"  💡 FOUND BY NAME MATCH:")
            print(f"     Member prospect_id: {fuzzy['prospect_id']}")
            print(f"     Member guid: {fuzzy['guid']}")
            print(f"     Member email: {fuzzy['email']}")
            print(f"     Member address: {fuzzy['address']}")

conn.close()
