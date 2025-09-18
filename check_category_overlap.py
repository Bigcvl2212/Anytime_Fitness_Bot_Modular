#!/usr/bin/env python3
"""
Check for overlapping members between categories to identify duplication
"""

import sqlite3
from typing import Set, Dict, List

def get_members_by_category(db_path: str) -> Dict[str, Set[str]]:
    """Get member IDs by category"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    categories = {}
    
    # Green
    cursor = conn.execute("""
        SELECT prospect_id FROM members 
        WHERE status_message IN ('Member is in good standing', 'In good standing')
    """)
    categories['green'] = set(row[0] for row in cursor.fetchall())
    
    # Past Due (money owed)
    cursor = conn.execute("""
        SELECT prospect_id FROM members 
        WHERE status_message IN ('Past Due 6-30 days', 'Past Due more than 30 days.')
    """)
    categories['past_due'] = set(row[0] for row in cursor.fetchall())
    
    # Yellow (account issues - not cancelled)
    cursor = conn.execute("""
        SELECT prospect_id FROM members 
        WHERE status_message IN (
            'Invalid Billing Information.',
            'Invalid/Bad Address information.',
            'Member is pending cancel',
            'Member will expire within 30 days.'
        )
    """)
    categories['yellow'] = set(row[0] for row in cursor.fetchall())
    
    # Comp
    cursor = conn.execute("""
        SELECT prospect_id FROM members 
        WHERE status_message = 'Comp Member'
    """)
    categories['comp'] = set(row[0] for row in cursor.fetchall())
    
    # PPV
    cursor = conn.execute("""
        SELECT prospect_id FROM members 
        WHERE status_message = 'Pay Per Visit Member'
    """)
    categories['ppv'] = set(row[0] for row in cursor.fetchall())
    
    # Staff (real staff only)
    cursor = conn.execute("""
        SELECT prospect_id FROM members
        WHERE prospect_id IN ('191003722', '189425730', '191210406', '191015549', '191201279')
    """)
    categories['staff'] = set(row[0] for row in cursor.fetchall())
    
    # Collections
    cursor = conn.execute("""
        SELECT prospect_id FROM members 
        WHERE agreement_id IS NULL
        AND status_message NOT IN ('Member is in good standing', 'In good standing')
    """)
    categories['collections'] = set(row[0] for row in cursor.fetchall())
    
    # Inactive (including fake staff members and cancelled accounts, excluding collections)
    cursor = conn.execute("""
        SELECT prospect_id FROM members 
        WHERE (
            status_message IN ('Expired', 'Account has been cancelled.', 'Inactive', 'inactive')
            OR status_message IS NULL
            OR (
                status_message IN ('Staff Member', 'Staff member', '') 
                AND prospect_id NOT IN ('191003722', '189425730', '191210406', '191015549', '191201279')
            )
        )
        AND agreement_id IS NOT NULL  -- Exclude collections members (NULL agreement_id)
        AND status_message != 'Sent to Collections'  -- Explicitly exclude sent to collections
    """)
    categories['inactive'] = set(row[0] for row in cursor.fetchall())
    
    conn.close()
    return categories

def check_overlaps(categories: Dict[str, Set[str]]) -> None:
    """Check for overlapping members between categories"""
    category_names = list(categories.keys())
    
    print("=== CHECKING FOR OVERLAPS ===")
    for i, cat1 in enumerate(category_names):
        for cat2 in category_names[i+1:]:
            overlap = categories[cat1] & categories[cat2]
            if overlap:
                print(f"OVERLAP between {cat1} and {cat2}: {len(overlap)} members")
                for member_id in sorted(overlap):
                    print(f"  - {member_id}")
            else:
                print(f"No overlap between {cat1} and {cat2}")

def main():
    db_path = "gym_bot.db"
    
    # Get all members by category
    categories = get_members_by_category(db_path)
    
    # Print counts
    print("=== CATEGORY COUNTS ===")
    total = 0
    for cat, members in categories.items():
        count = len(members)
        total += count
        print(f"{cat}: {count}")
    
    print(f"\nTotal categorized: {total}")
    
    # Check database total
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT COUNT(*) FROM members")
    db_total = cursor.fetchone()[0]
    conn.close()
    
    print(f"Database total: {db_total}")
    print(f"Difference: {total - db_total}")
    
    # Check overlaps
    check_overlaps(categories)
    
    # Find all unique members
    all_categorized = set()
    for members in categories.values():
        all_categorized.update(members)
    
    print(f"\nUnique members categorized: {len(all_categorized)}")
    
    # Find uncategorized members
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT prospect_id FROM members")
    all_members = set(row[0] for row in cursor.fetchall())
    conn.close()
    
    uncategorized = all_members - all_categorized
    if uncategorized:
        print(f"\nUNCATEGORIZED MEMBERS ({len(uncategorized)}):")
        conn2 = sqlite3.connect(db_path)
        for member_id in sorted(uncategorized):
            cursor = conn2.execute("SELECT first_name, last_name, status_message FROM members WHERE prospect_id = ?", (member_id,))
            row = cursor.fetchone()
            if row:
                print(f"  {member_id}: {row[0]} {row[1]} - '{row[2]}'")
        conn2.close()

if __name__ == "__main__":
    main()