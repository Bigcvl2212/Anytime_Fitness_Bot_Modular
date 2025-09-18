#!/usr/bin/env python3
"""
Test the fixed bulk check-in query to verify it includes all eligible members
"""

import sqlite3
from datetime import datetime

def test_fixed_query():
    conn = sqlite3.connect('gym_bot.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print('🧪 === Testing Fixed Bulk Check-in Query ===')
    
    # NEW FIXED QUERY (includes green members with empty status)
    fixed_query = """
        SELECT prospect_id, first_name, last_name, full_name, status_message, 
               user_type, member_type, agreement_type, status
        FROM members 
        WHERE (status_message IS NULL 
               OR status_message = ''
               OR (status_message IS NOT NULL 
                   AND status_message != ''
                   AND status_message NOT LIKE 'Pay Per Visit%'))
    """
    
    print('📋 Fixed query:')
    print(fixed_query)
    print()
    
    # Execute fixed query
    cursor.execute(fixed_query)
    fixed_results = cursor.fetchall()
    
    # Get baseline counts
    cursor.execute('SELECT COUNT(*) as total FROM members')
    total_members = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as ppv_count FROM members WHERE status_message LIKE "%Pay Per Visit%"')
    ppv_members = cursor.fetchone()['ppv_count']
    
    expected_eligible = total_members - ppv_members
    
    print(f'✅ Results:')
    print(f'  Total members in database: {total_members}')
    print(f'  PPV members (should exclude): {ppv_members}') 
    print(f'  Expected eligible members: {expected_eligible}')
    print(f'  Members selected by fixed query: {len(fixed_results)}')
    
    if len(fixed_results) == expected_eligible:
        print(f'\n🎉 SUCCESS! Fixed query selects exactly the right number of members!')
        print(f'   Fixed query will now include all {len(fixed_results)} eligible members')
        print(f'   This means 53 additional green members will now be checked in')
    else:
        print(f'\n⚠️  Issue: Expected {expected_eligible} but got {len(fixed_results)}')
        difference = expected_eligible - len(fixed_results)
        print(f'   Still missing: {difference} members')
    
    # Show breakdown by status message patterns
    print(f'\n📊 === Status Message Breakdown in Fixed Query ===')
    status_patterns = {}
    
    for member in fixed_results:
        status = member['status_message']
        if status is None:
            pattern = 'NULL'
        elif status == '':
            pattern = 'EMPTY (Green Members)'
        elif 'Good Standing' in status:
            pattern = 'Good Standing'
        elif 'Past Due' in status:
            pattern = 'Past Due'
        elif 'Staff' in status:
            pattern = 'Staff'
        elif 'Comp' in status or 'complimentary' in status.lower():
            pattern = 'Complimentary'
        elif 'Frozen' in status:
            pattern = 'Frozen'
        else:
            pattern = f'Other: {status[:30]}'
            
        if pattern not in status_patterns:
            status_patterns[pattern] = 0
        status_patterns[pattern] += 1
    
    for pattern, count in sorted(status_patterns.items(), key=lambda x: x[1], reverse=True):
        print(f'  {pattern:30} : {count:3} members')
        
    # Verify PPV exclusion still works
    print(f'\n🔍 === PPV Exclusion Verification ===')
    cursor.execute('SELECT COUNT(*) as count FROM members WHERE status_message LIKE "%Pay Per Visit%"')
    total_ppv = cursor.fetchone()['count']
    
    ppv_in_results = 0
    for member in fixed_results:
        if member['status_message'] and 'Pay Per Visit' in member['status_message']:
            ppv_in_results += 1
    
    print(f'  Total PPV members in database: {total_ppv}')
    print(f'  PPV members in fixed query results: {ppv_in_results}')
    
    if ppv_in_results == 0:
        print(f'  ✅ PPV exclusion working correctly!')
    else:
        print(f'  ❌ PPV exclusion failed - {ppv_in_results} PPV members included!')

    conn.close()

if __name__ == "__main__":
    test_fixed_query()