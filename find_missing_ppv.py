#!/usr/bin/env python3
"""
Find Missing PPV Members
Look for the 20 additional PPV members (117 - 97 = 20)
"""

import sqlite3
import os

def find_missing_ppv():
    """Find the missing 20 PPV members"""
    db_path = os.path.join(os.getcwd(), 'gym_bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        print("🔍 Looking for missing PPV members...")
        
        # First, let's check total member count
        cursor.execute("SELECT COUNT(*) as total FROM members")
        total = cursor.fetchone()['total']
        print(f"Total members in database: {total}")
        
        # Check members with NULL or empty status_message
        cursor.execute("""
            SELECT COUNT(*) as null_status_count 
            FROM members 
            WHERE status_message IS NULL OR status_message = ''
        """)
        null_status = cursor.fetchone()['null_status_count']
        print(f"Members with NULL/empty status_message: {null_status}")
        
        if null_status > 0:
            print(f"\n🔍 Examining members with NULL/empty status_message:")
            cursor.execute("""
                SELECT prospect_id, full_name, user_type, member_type, agreement_type, status
                FROM members 
                WHERE status_message IS NULL OR status_message = ''
                LIMIT 25
            """)
            
            null_members = cursor.fetchall()
            for member in null_members:
                print(f"  ID: {member['prospect_id']}, Name: {member['full_name']}")
                print(f"    user_type: {member['user_type']}, member_type: {member['member_type']}")
                print(f"    agreement_type: {member['agreement_type']}, status: {member['status']}")
                print()
        
        # Check if there are exactly 20 members with NULL status that could be PPV
        if null_status == 20:
            print("🎯 POTENTIAL MATCH: Found exactly 20 members with NULL status_message!")
            print("These could be the missing PPV members.")
        
        # Look for specific user_type, member_type, or agreement_type patterns
        print(f"\n🔍 Checking for other identifying patterns...")
        
        # Check all possible user_type values
        cursor.execute("""
            SELECT user_type, COUNT(*) as count 
            FROM members 
            GROUP BY user_type 
            ORDER BY count DESC
        """)
        user_type_counts = cursor.fetchall()
        print(f"All user_type values:")
        for ut in user_type_counts:
            print(f"  user_type {ut['user_type']}: {ut['count']} members")
        
        # Check for specific numeric patterns that might indicate PPV
        for ut in user_type_counts:
            if ut['count'] == 20:  # Looking for the missing 20
                print(f"🎯 POTENTIAL MATCH: user_type {ut['user_type']} has exactly 20 members!")
            elif ut['count'] == 117:  # Or the full 117
                print(f"🎯 POTENTIAL MATCH: user_type {ut['user_type']} has exactly 117 members!")
        
        # Check agreement_type for PPV patterns
        cursor.execute("""
            SELECT agreement_type, COUNT(*) as count 
            FROM members 
            WHERE agreement_type IS NOT NULL
            GROUP BY agreement_type 
            ORDER BY count DESC
        """)
        agreement_counts = cursor.fetchall()
        print(f"\nAgreement type counts:")
        for ag in agreement_counts:
            if ag['agreement_type']:
                print(f"  '{ag['agreement_type']}': {ag['count']} members")
                if ag['count'] == 20 or ag['count'] == 117:
                    print(f"    🎯 POTENTIAL MATCH: This could be PPV!")
        
        # Final calculation: what gives us exactly 117?
        known_ppv = 97  # "Pay Per Visit Member" status
        needed = 117 - known_ppv  # 20 more needed
        
        print(f"\n📊 Summary:")
        print(f"Known PPV (status='Pay Per Visit Member'): {known_ppv}")
        print(f"Additional PPV needed: {needed}")
        print(f"Members with NULL status_message: {null_status}")
        
        if null_status == needed:
            print("✅ CONCLUSION: The 20 members with NULL status_message are likely the missing PPV members!")
            return 'null_status'
        else:
            # Look for other combinations
            print("🔍 Checking other field combinations...")
            
            # Maybe it's a specific user_type + the known PPV
            for ut in user_type_counts:
                if ut['user_type'] is not None and ut['count'] == needed:
                    print(f"✅ POSSIBLE: user_type {ut['user_type']} ({ut['count']}) + known PPV ({known_ppv}) = {ut['count'] + known_ppv}")
                    if ut['count'] + known_ppv == 117:
                        return f"user_type_{ut['user_type']}"
        
        return None
        
    except Exception as e:
        print(f"❌ Error finding missing PPV: {e}")
        return None
    
    finally:
        conn.close()

if __name__ == "__main__":
    result = find_missing_ppv()
    print(f"\n🎯 Result: {result}")