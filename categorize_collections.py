import sys
sys.path.append('.')
from src.services.database_manager import DatabaseManager

def categorize_collections_members():
    """Update members with NULL agreement_id to Collections status"""
    db = DatabaseManager()
    
    print('🔄 Categorizing members already sent to collections...')
    
    # Find members with past due amounts but NULL agreement_id (already in collections)
    collections_members = db.execute_query("""
        SELECT id, full_name, amount_past_due, status_message, agreement_id
        FROM members 
        WHERE amount_past_due > 0 
          AND agreement_id IS NULL
        ORDER BY amount_past_due DESC
    """)
    
    print(f'📋 Found {len(collections_members)} members already in collections:')
    for member in collections_members:
        print(f'  - {member["full_name"]}: ${member["amount_past_due"]} - Status: {member["status_message"]}')
    
    if collections_members:
        # Update their status to reflect collections
        for member in collections_members:
            db.execute_query("""
                UPDATE members 
                SET status_message = 'Sent to Collections',
                    agreement_type = 'Collections'
                WHERE id = ?
            """, (member['id'],))
        
        print(f'\n✅ Updated {len(collections_members)} members to Collections status')
        
        # Show summary stats
        remaining_past_due = db.execute_query("""
            SELECT COUNT(*) as count, SUM(amount_past_due) as total_amount
            FROM members 
            WHERE (status_message LIKE '%Past Due 6-30 days%' 
                   OR status_message LIKE '%Past Due more than 30 days%')
              AND agreement_id IS NOT NULL
        """)[0]
        
        collections_summary = db.execute_query("""
            SELECT COUNT(*) as count, SUM(amount_past_due) as total_amount
            FROM members 
            WHERE status_message = 'Sent to Collections'
        """)[0]
        
        print(f'\n📊 Updated Status Summary:')
        print(f'  - Active Past Due (with agreements): {remaining_past_due["count"]} members, ${remaining_past_due["total_amount"]:.2f}')
        print(f'  - Already in Collections: {collections_summary["count"]} members, ${collections_summary["total_amount"]:.2f}')
        
        # Test the collections API query
        print(f'\n🧪 Testing collections query...')
        test_collections = db.execute_query("""
            SELECT full_name, agreement_id, amount_past_due, status_message
            FROM members 
            WHERE status_message LIKE '%Past Due 6-30 days%' 
               OR status_message LIKE '%Past Due more than 30 days%'
            ORDER BY amount_past_due DESC
            LIMIT 5
        """)
        
        print(f'📋 Active Collections Candidates (should all have agreement IDs):')
        for member in test_collections:
            print(f'  - {member["full_name"]}: Agreement {member["agreement_id"]} - ${member["amount_past_due"]}')
        
    else:
        print('✅ No members found that need collections categorization')

if __name__ == "__main__":
    categorize_collections_members()