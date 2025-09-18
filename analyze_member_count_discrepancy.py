#!/usr/bin/env python3
"""
Database vs ClubHub Member Count Analysis
Figure out why database has 520-526 members when ClubHub shows exactly 500
"""

import sqlite3
import os
from collections import Counter

def analyze_member_count_discrepancy():
    """Analyze why database has more members than ClubHub reports"""
    db_path = os.path.join(os.getcwd(), 'gym_bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        print("🔍 Analyzing member count discrepancy between database and ClubHub...")
        print("ClubHub reports exactly 500 members")
        print("Database shows 520-526 members")
        print("Need to find the 20-26 extra members\n")
        
        # Total members in database
        cursor.execute("SELECT COUNT(*) as total FROM members")
        db_total = cursor.fetchone()['total']
        print(f"📊 Database total members: {db_total}")
        
        # Check status field (numeric status indicators)
        print(f"\n🔍 Analyzing status field (numeric):")
        cursor.execute("SELECT status, COUNT(*) as count FROM members GROUP BY status ORDER BY count DESC")
        status_counts = cursor.fetchall()
        
        active_by_status = 0
        for row in status_counts:
            status = row['status']
            count = row['count']
            print(f"  Status {status}: {count} members")
            
            # Status 1 typically means active
            if status == 1 or status == '1':
                active_by_status = count
        
        print(f"\n📊 Status=1 (typically active): {active_by_status} members")
        
        # Check status_message field (text descriptions)
        print(f"\n🔍 Analyzing status_message field:")
        cursor.execute("""
            SELECT status_message, COUNT(*) as count 
            FROM members 
            WHERE status_message IS NOT NULL AND status_message != ''
            GROUP BY status_message 
            ORDER BY count DESC
        """)
        status_msg_counts = cursor.fetchall()
        
        total_with_status_msg = 0
        clubhub_categories = {
            'green': 0,      # Active members
            'yellow': 0,     # At risk
            'red': 0,        # Past due
            'frozen': 0,     # Frozen
            'comp': 0,       # Complimentary
            'ppv': 0,        # Pay per visit
            'staff': 0,      # Staff
            'other': 0       # Other statuses
        }
        
        for row in status_msg_counts:
            status_msg = row['status_message'] or 'NULL'
            count = row['count']
            total_with_status_msg += count
            
            print(f"  '{status_msg}': {count} members")
            
            # Categorize based on ClubHub categories
            status_lower = status_msg.lower()
            if 'good standing' in status_lower:
                clubhub_categories['green'] += count
            elif 'pay per visit' in status_lower or 'ppv' in status_lower:
                clubhub_categories['ppv'] += count
            elif 'comp' in status_lower or 'complimentary' in status_lower:
                clubhub_categories['comp'] += count
            elif 'staff' in status_lower:
                clubhub_categories['staff'] += count
            elif 'past due' in status_lower:
                clubhub_categories['red'] += count  # Past due = red
            elif 'frozen' in status_lower or 'hold' in status_lower:
                clubhub_categories['frozen'] += count
            elif 'expire' in status_lower or 'pending' in status_lower:
                clubhub_categories['yellow'] += count  # At risk = yellow
            elif 'cancel' in status_lower or 'inactive' in status_lower:
                clubhub_categories['other'] += count  # These might be the extra ones
            else:
                clubhub_categories['other'] += count
        
        # Check members with NULL/empty status_message
        cursor.execute("""
            SELECT COUNT(*) as null_count 
            FROM members 
            WHERE status_message IS NULL OR status_message = ''
        """)
        null_status_count = cursor.fetchone()['null_count']
        
        print(f"\n📊 Members with NULL/empty status_message: {null_status_count}")
        
        # Total accounted for
        total_accounted = total_with_status_msg + null_status_count
        print(f"📊 Total members accounted for: {total_accounted}")
        
        print(f"\n🎯 ClubHub Category Mapping (from database status_message):")
        print(f"  Green (active): {clubhub_categories['green']} (ClubHub says 304)")
        print(f"  Yellow (at risk): {clubhub_categories['yellow']} (ClubHub says 27)")
        print(f"  Red (past due): {clubhub_categories['red']} (ClubHub says 13)")
        print(f"  Frozen: {clubhub_categories['frozen']} (ClubHub says 3)")
        print(f"  Complimentary: {clubhub_categories['comp']} (ClubHub says 31)")
        print(f"  PPV: {clubhub_categories['ppv']} (ClubHub says 117)")
        print(f"  Staff: {clubhub_categories['staff']} (ClubHub says 5)")
        print(f"  Other/Cancelled: {clubhub_categories['other']} (ClubHub says 0)")
        print(f"  NULL status: {null_status_count}")
        
        database_sum = sum(clubhub_categories.values()) + null_status_count
        clubhub_expected = 304 + 27 + 13 + 3 + 31 + 117 + 5  # = 500
        
        print(f"\n📊 Summary:")
        print(f"  Database sum: {database_sum}")
        print(f"  ClubHub expected: {clubhub_expected}")
        print(f"  Difference: {database_sum - clubhub_expected}")
        
        # Find the specific extra members
        extra_count = clubhub_categories['other'] + null_status_count
        if extra_count > 0:
            print(f"\n🔍 The {extra_count} extra members are likely:")
            print(f"  - {clubhub_categories['other']} members with 'other' status (cancelled/inactive)")
            print(f"  - {null_status_count} members with NULL status_message")
        
        # Show some examples of the "other" category
        print(f"\n🔍 Sample members in 'other' category (likely inactive/cancelled):")
        cursor.execute("""
            SELECT prospect_id, full_name, status_message, status, created_at
            FROM members 
            WHERE LOWER(status_message) LIKE '%cancel%' 
               OR LOWER(status_message) LIKE '%inactive%'
               OR status_message IS NULL
               OR status_message = ''
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        extra_members = cursor.fetchall()
        for member in extra_members:
            print(f"  ID: {member['prospect_id']}, Name: {member['full_name']}")
            print(f"    Status: '{member['status_message']}', Numeric Status: {member['status']}")
            print(f"    Created: {member['created_at']}")
            print()
        
        # Recommendation
        print(f"💡 RECOMMENDATION:")
        print(f"For bulk check-in, we should:")
        print(f"1. Only process members from ClubHub API (fresh data) = 500 members")
        print(f"2. Exclude the 117 PPV members = 383 eligible for check-in")
        print(f"3. Ignore the extra {extra_count} inactive/cancelled members in the database")
        
        return {
            'db_total': db_total,
            'clubhub_expected': clubhub_expected,
            'extra_members': extra_count,
            'categories': clubhub_categories,
            'null_status': null_status_count
        }
        
    except Exception as e:
        print(f"❌ Error analyzing member count: {e}")
        return None
    
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_member_count_discrepancy()