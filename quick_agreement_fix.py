#!/usr/bin/env python3

"""
Quick Agreement ID Fix

Since some past due members are missing agreement IDs and the API session needs to be active,
this script provides options to fix the issue:

1. Run full member refresh (recommended) - will authenticate and update all members
2. Manual database update for testing - sets placeholder agreement IDs for testing

Run this script then test the collections modal.
"""

import sys
sys.path.append('.')
from src.services.database_manager import DatabaseManager

def check_missing_agreement_ids():
    """Check which past due members are missing agreement IDs"""
    db = DatabaseManager()
    
    print('🔍 Checking past due members without agreement IDs...')
    
    missing_agreement_members = db.execute_query("""
        SELECT id, full_name, prospect_id, amount_past_due, status_message
        FROM members 
        WHERE (status_message LIKE '%Past Due 6-30 days%' 
               OR status_message LIKE '%Past Due more than 30 days%')
          AND agreement_id IS NULL
        ORDER BY amount_past_due DESC
    """)
    
    print(f'📋 Found {len(missing_agreement_members)} past due members without agreement IDs:')
    for member in missing_agreement_members:
        print(f'  - {member["full_name"]}: ${member["amount_past_due"]} (ID: {member["prospect_id"]})')
    
    return missing_agreement_members

def quick_test_fix():
    """Add placeholder agreement IDs for testing (NOT for production use)"""
    db = DatabaseManager()
    
    missing_members = check_missing_agreement_ids()
    
    if not missing_members:
        print('✅ All past due members already have agreement IDs!')
        return
    
    print(f'\n⚠️ WARNING: This will add PLACEHOLDER agreement IDs for testing only!')
    print('⚠️ For production use, run a full member refresh instead!')
    
    # Add placeholder agreement IDs for testing
    for i, member in enumerate(missing_members):
        placeholder_agreement_id = f"TEST_{member['prospect_id']}"
        
        db.execute_query("""
            UPDATE members 
            SET agreement_id = ?, agreement_type = 'Membership'
            WHERE id = ?
        """, (placeholder_agreement_id, member['id']))
        
        print(f'✅ Added placeholder agreement ID {placeholder_agreement_id} to {member["full_name"]}')
    
    print(f'\n✅ Added placeholder agreement IDs to {len(missing_members)} members')
    print('\n🧪 Now test the collections modal - it should show agreement IDs!')
    print('💡 Remember: Run full member refresh later to get real agreement IDs')

def main():
    print('🎯 Agreement ID Fix Options:')
    print()
    print('1. Check missing agreement IDs')
    print('2. Add placeholder agreement IDs for testing (quick fix)')
    print('3. Exit (run full member refresh instead)')
    print()
    
    choice = input('Enter your choice (1-3): ').strip()
    
    if choice == '1':
        check_missing_agreement_ids()
    elif choice == '2':
        quick_test_fix()
    elif choice == '3':
        print('💡 Run full member refresh in the dashboard to get real agreement IDs')
    else:
        print('❌ Invalid choice')

if __name__ == "__main__":
    main()