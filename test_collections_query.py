import sys
sys.path.append('.')
from src.services.database_manager import DatabaseManager

def test_collections_query():
    """Test the collections query to see if agreement IDs are being returned"""
    db = DatabaseManager()
    
    print("🔍 Testing Collections Query...")
    
    # Use the same query as the collections API
    result = db.execute_query("""
        SELECT 
            full_name as name,
            email,
            mobile_phone as phone,
            amount_past_due as past_due_amount,
            status,
            join_date,
            'member' as type,
            status_message,
            agreement_recurring_cost,
            agreement_id,
            agreement_guid,
            agreement_type
        FROM members 
        WHERE status_message LIKE '%Past Due 6-30 days%' 
           OR status_message LIKE '%Past Due more than 30 days%'
        ORDER BY amount_past_due DESC
        LIMIT 5
    """)
    
    print(f"\n📋 Found {len(result)} past due members:")
    for i, member in enumerate(result):
        print(f"{i+1}. {member['name']}")
        print(f"   Amount: ${member['past_due_amount']}")
        print(f"   Agreement ID: {member['agreement_id']}")
        print(f"   Agreement Type: {member['agreement_type']}")
        print(f"   Status Message: {member['status_message']}")
        print()
    
    # Also test tuple handling (simulating SQLite behavior)
    print("🧪 Testing tuple handling:")
    if result:
        member = result[0]
        # Convert to tuple like SQLite would return
        member_tuple = (
            member['name'], member['email'], member['phone'],
            member['past_due_amount'], member['status'], member['join_date'],
            member['type'], member['status_message'], member['agreement_recurring_cost'],
            member['agreement_id'], member['agreement_guid'], member['agreement_type']
        )
        
        print(f"Tuple length: {len(member_tuple)}")
        print(f"Agreement ID at index 9: {member_tuple[9]}")
        print(f"Agreement Type at index 11: {member_tuple[11]}")

if __name__ == "__main__":
    test_collections_query()