#!/usr/bin/env python3

"""
Find Missing PPV Members
======================

This script searches for all possible PPV member patterns to find the missing 20 PPV members.
"""

import sqlite3

def find_missing_ppv_members():
    """Find all possible PPV member patterns"""
    
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    print("=== All unique status_message values ===")
    cursor.execute("SELECT status_message, COUNT(*) FROM members GROUP BY status_message ORDER BY COUNT(*) DESC")
    all_status = cursor.fetchall()
    for status_msg, count in all_status:
        print(f"  '{status_msg}': {count}")
    
    print("\n=== Looking for PPV variations ===")
    cursor.execute("""
        SELECT status_message, status, COUNT(*) as count,
               GROUP_CONCAT(full_name, ', ') as names
        FROM members 
        WHERE LOWER(status_message) LIKE '%visit%' 
           OR LOWER(status_message) LIKE '%ppv%'
           OR LOWER(status_message) LIKE '%day%'
           OR LOWER(status_message) LIKE '%guest%'
           OR LOWER(status_message) LIKE '%drop%'
           OR LOWER(status_message) LIKE '%single%'
        GROUP BY status_message, status
        ORDER BY count DESC
    """)
    
    variations = cursor.fetchall()
    total_ppv_variations = 0
    if variations:
        print("Found PPV-like patterns:")
        for status_msg, status, count, names in variations:
            sample_names = names.split(', ')[:3] if names else ['None']
            print(f"  Status '{status}' + '{status_msg}': {count} members")
            print(f"    Samples: {', '.join(sample_names)}")
            total_ppv_variations += count
    
    print(f"\nTotal PPV-like members found: {total_ppv_variations}")
    
    print("\n=== Checking members with empty status_message ===")
    cursor.execute("SELECT COUNT(*) FROM members WHERE status_message IS NULL OR status_message = ''")
    empty_status = cursor.fetchone()[0]
    print(f"Members with empty status_message: {empty_status}")
    
    if empty_status > 0:
        cursor.execute("""
            SELECT status, COUNT(*), GROUP_CONCAT(full_name, ', ') as names
            FROM members 
            WHERE status_message IS NULL OR status_message = ''
            GROUP BY status
        """)
        empty_breakdown = cursor.fetchall()
        print("Breakdown of empty status_message by status:")
        for status, count, names in empty_breakdown:
            sample_names = names.split(', ')[:5] if names else ['None']
            print(f"  Status '{status}': {count} members")
            print(f"    Samples: {', '.join(sample_names)}")
    
    print("\n=== Checking agreement_type patterns ===")
    cursor.execute("""
        SELECT agreement_type, COUNT(*), 
               GROUP_CONCAT(DISTINCT status_message) as status_messages
        FROM members 
        WHERE agreement_type IS NOT NULL AND agreement_type != ''
        GROUP BY agreement_type
        ORDER BY COUNT(*) DESC
    """)
    agreement_patterns = cursor.fetchall()
    if agreement_patterns:
        print("Agreement type patterns:")
        for agreement_type, count, status_messages in agreement_patterns:
            print(f"  '{agreement_type}': {count} members (status: {status_messages})")
    else:
        print("No agreement_type data found")
    
    print(f"\n=== SUMMARY ===")
    print(f"Known PPV members ('Pay Per Visit Member'): 97")
    print(f"ClubHub expected PPV members: 117")
    print(f"Missing PPV members: 20")
    print(f"Members with empty status_message: {empty_status}")
    
    # Check if the missing 20 might be in the empty status group
    if empty_status >= 20:
        print(f"\n💡 HYPOTHESIS: The missing 20 PPV members might be among the {empty_status} members with empty status_message")
        
        # Let's check some of these members more closely
        cursor.execute("""
            SELECT full_name, status, amount_past_due, join_date, agreement_recurring_cost
            FROM members 
            WHERE status_message IS NULL OR status_message = ''
            ORDER BY id
            LIMIT 20
        """)
        empty_samples = cursor.fetchall()
        print("\nFirst 20 members with empty status_message:")
        for name, status, past_due, join_date, recurring_cost in empty_samples:
            print(f"  {name}: status='{status}', past_due=${past_due}, join={join_date}, recurring=${recurring_cost}")
    
    conn.close()

if __name__ == "__main__":
    find_missing_ppv_members()