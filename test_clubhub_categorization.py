#!/usr/bin/env python3
"""
Test ClubHub-matched categorization
"""

import sqlite3

def test_clubhub_categorization():
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()

    print('=== CLUBHUB CATEGORIZATION VERIFICATION ===')

    # Green members: "Member is in good standing" (Expected: 308, ClubHub says 308)
    cursor.execute("SELECT COUNT(*) FROM members WHERE status_message = 'Member is in good standing'")
    green_count = cursor.fetchone()[0]
    print(f'🟢 Green (Good Standing): {green_count} members (ClubHub: 308)')

    # Yellow/Past Due: Multiple status messages (Expected: 22, ClubHub says 22)
    cursor.execute("""
        SELECT COUNT(*) FROM members
        WHERE status_message IN (
            'Past Due 6-30 days',
            'Invalid Billing Information.',
            'Invalid/Bad Address information.',
            'Member is pending cancel',
            'Member will expire within 30 days.'
        )
    """)
    yellow_count = cursor.fetchone()[0]
    print(f'🟡 Yellow/Past Due: {yellow_count} members (ClubHub: 22)')

    # Red members: Past due more than 30 days, cancelled (Expected: 17, ClubHub says 17)
    cursor.execute("""
        SELECT COUNT(*) FROM members
        WHERE status_message IN (
            'Past Due more than 30 days.',
            'Account has been cancelled.'
        )
    """)
    red_count = cursor.fetchone()[0]
    print(f'🔴 Red: {red_count} members (ClubHub: 17)')

    # Frozen members (Expected: 3, ClubHub says 3)
    cursor.execute("SELECT COUNT(*) FROM members WHERE status_message LIKE '%frozen%' OR status_message LIKE '%Frozen%'")
    frozen_count = cursor.fetchone()[0]
    print(f'🧊 Frozen: {frozen_count} members (ClubHub: 3)')

    # Comp members: "Comp Member" (Expected: 31, ClubHub says 31, we have 32)
    cursor.execute("SELECT COUNT(*) FROM members WHERE status_message = 'Comp Member'")
    comp_count = cursor.fetchone()[0]
    print(f'🎫 Comp: {comp_count} members (ClubHub: 31)')

    # PPV members: "Pay Per Visit Member" (Expected: 116, ClubHub says 116)
    cursor.execute("SELECT COUNT(*) FROM members WHERE status_message = 'Pay Per Visit Member'")
    ppv_count = cursor.fetchone()[0]
    print(f'💰 PPV: {ppv_count} members (ClubHub: 116)')

    # Staff members: Only the 5 specific accounts by prospect ID (Expected: 5, ClubHub says 5)
    cursor.execute("SELECT COUNT(*) FROM members WHERE prospect_id IN ('64309309', '55867562', '50909888', '62716557', '52750389')")
    staff_count = cursor.fetchone()[0]
    print(f'👥 Staff: {staff_count} members (ClubHub: 5)')

    # Other/Inactive (Expired, NULL)
    cursor.execute("SELECT COUNT(*) FROM members WHERE status_message IN ('Expired') OR status_message IS NULL")
    inactive_count = cursor.fetchone()[0]
    print(f'❌ Other/Inactive: {inactive_count} members')

    print('\n=== BREAKDOWN BY INDIVIDUAL STATUS MESSAGES ===')
    cursor.execute("""
        SELECT status_message, COUNT(*) as count
        FROM members
        GROUP BY status_message
        ORDER BY count DESC
    """)

    for row in cursor.fetchall():
        status_msg = row[0] or 'NULL'
        count = row[1]
        print(f'{status_msg}: {count}')

    total = green_count + yellow_count + red_count + frozen_count + comp_count + ppv_count + staff_count + inactive_count
    print(f'\n🔢 Total categorized: {total} members')
    
    cursor.execute("SELECT COUNT(*) FROM members")
    db_total = cursor.fetchone()[0]
    print(f'📊 Database total: {db_total} members')

    conn.close()

if __name__ == "__main__":
    test_clubhub_categorization()