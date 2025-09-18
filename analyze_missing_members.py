#!/usr/bin/env python3
"""
Analyze why 53 members were missing from bulk check-in
Compare the database query used in bulk check-in vs actual database contents
"""

import sqlite3
import json
from datetime import datetime

def analyze_missing_members():
    conn = sqlite3.connect('gym_bot.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print('🔍 === Analyzing Member Selection Logic ===')
    
    # This is the EXACT query used in bulk check-in (from perform_bulk_checkin_background)
    bulk_checkin_query = """
        SELECT prospect_id, first_name, last_name, full_name, status_message, 
               user_type, member_type, agreement_type, status
        FROM members 
        WHERE status_message IS NOT NULL 
        AND status_message != ''
        AND status_message NOT LIKE 'Pay Per Visit%'
    """
    
    print(f'📋 Bulk check-in query:\n{bulk_checkin_query}\n')
    
    # Execute the exact query used by bulk check-in
    cursor.execute(bulk_checkin_query)
    bulk_checkin_members = cursor.fetchall()
    
    print(f'✅ Members found by bulk check-in query: {len(bulk_checkin_members)}')
    
    # Now let's see what the total count should be
    cursor.execute('SELECT COUNT(*) as total FROM members')
    total_members = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as ppv_count FROM members WHERE status_message LIKE "%Pay Per Visit%"')
    ppv_members = cursor.fetchone()['ppv_count']
    
    print(f'📊 Total members in database: {total_members}')
    print(f'📊 PPV members (should be excluded): {ppv_members}')
    print(f'📊 Expected eligible members: {total_members - ppv_members}')
    print(f'📊 Actually selected by query: {len(bulk_checkin_members)}')
    
    # Find the discrepancy
    expected = total_members - ppv_members
    actual = len(bulk_checkin_members)
    missing = expected - actual
    
    print(f'\n⚠️  DISCREPANCY: {missing} members missing from bulk check-in selection!')
    
    # Let's find which members are missing by looking at members NOT selected by the query
    print(f'\n🔍 === Finding Missing Members ===')
    
    # Get all non-PPV members
    cursor.execute("""
        SELECT prospect_id, first_name, last_name, full_name, status_message, 
               user_type, member_type, agreement_type, status
        FROM members 
        WHERE status_message NOT LIKE 'Pay Per Visit%'
        ORDER BY prospect_id
    """)
    all_non_ppv_members = cursor.fetchall()
    
    # Get members selected by bulk check-in query
    bulk_checkin_ids = set(str(m['prospect_id']) for m in bulk_checkin_members if m['prospect_id'])
    
    # Find missing members
    missing_members = []
    for member in all_non_ppv_members:
        if str(member['prospect_id']) not in bulk_checkin_ids:
            missing_members.append(member)
    
    print(f'📋 Missing members found: {len(missing_members)}')
    
    if missing_members:
        print(f'\n❌ === Members NOT Selected by Bulk Check-in Query ===')
        for i, member in enumerate(missing_members[:20]):  # Show first 20
            name = member['full_name'] or f"{member['first_name']} {member['last_name']}"
            status_msg = member['status_message'] or 'NULL'
            print(f'  {i+1:2}. ID: {member["prospect_id"]:8} | {name:30} | Status: {status_msg}')
        
        if len(missing_members) > 20:
            print(f'     ... and {len(missing_members) - 20} more')
    
    # Analyze the status_message patterns in missing members
    print(f'\n🔍 === Status Message Analysis for Missing Members ===')
    missing_status_patterns = {}
    for member in missing_members:
        status = member['status_message']
        if status is None:
            pattern = 'NULL'
        elif status == '':
            pattern = 'EMPTY_STRING'
        else:
            pattern = status
        
        if pattern not in missing_status_patterns:
            missing_status_patterns[pattern] = 0
        missing_status_patterns[pattern] += 1
    
    for pattern, count in sorted(missing_status_patterns.items(), key=lambda x: x[1], reverse=True):
        print(f'  {pattern:40} : {count:3} members')
    
    # Check if the issue is NULL vs empty string handling
    print(f'\n🔍 === NULL/Empty String Analysis ===')
    
    cursor.execute("SELECT COUNT(*) as count FROM members WHERE status_message IS NULL")
    null_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM members WHERE status_message = ''")
    empty_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM members WHERE status_message IS NOT NULL AND status_message != ''")
    has_content_count = cursor.fetchone()['count']
    
    print(f'  Members with NULL status_message: {null_count}')
    print(f'  Members with empty status_message: {empty_count}')  
    print(f'  Members with content in status_message: {has_content_count}')
    print(f'  Total: {null_count + empty_count + has_content_count} (should equal {total_members})')
    
    # Test alternative queries
    print(f'\n🧪 === Testing Alternative Queries ===')
    
    # Query 1: Include NULL and empty
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM members 
        WHERE (status_message IS NULL 
               OR status_message = ''
               OR (status_message IS NOT NULL 
                   AND status_message != ''
                   AND status_message NOT LIKE 'Pay Per Visit%'))
    """)
    alt_query1_count = cursor.fetchone()['count']
    
    # Query 2: Only exclude PPV, include everything else
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM members 
        WHERE status_message NOT LIKE 'Pay Per Visit%'
           OR status_message IS NULL
           OR status_message = ''
    """)
    alt_query2_count = cursor.fetchone()['count']
    
    print(f'  Alternative Query 1 (include NULL/empty): {alt_query1_count} members')
    print(f'  Alternative Query 2 (only exclude PPV): {alt_query2_count} members')
    print(f'  Expected total eligible: {total_members - ppv_members}')
    
    print(f'\n💡 === Root Cause Analysis ===')
    
    if null_count > 0 or empty_count > 0:
        print(f'  🎯 FOUND THE ISSUE!')
        print(f'     The bulk check-in query excludes members with NULL or empty status_message')
        print(f'     Current query requires: status_message IS NOT NULL AND status_message != \'\'')
        print(f'     This excludes {null_count + empty_count} members who should be included!')
        print(f'     Expected missing: {null_count + empty_count}')
        print(f'     Actual missing: {missing}')
        
        if (null_count + empty_count) == missing:
            print(f'     ✅ Perfect match! This explains the discrepancy.')
        else:
            print(f'     ⚠️  Numbers don\'t match perfectly, may be additional factors.')
    
    conn.close()

if __name__ == "__main__":
    analyze_missing_members()