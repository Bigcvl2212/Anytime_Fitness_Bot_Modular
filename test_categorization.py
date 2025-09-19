#!/usr/bin/env python3

import sqlite3
import sys
sys.path.append('.')
from src.services.database_manager import DatabaseManager

def test_categorization_logic():
    """Test the updated categorization logic with some real member data"""
    
    db_path = "gym_bot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== TESTING CATEGORIZATION LOGIC ===")
        
        # Get some sample members to test categorization
        cursor.execute("""
            SELECT id, full_name, agreement_type, amount_past_due, status_message, status
            FROM members 
            WHERE full_name IN ('ANTHONY JORDAN', 'Miguel Belmontes', 'JOSEPH JONES')
            OR agreement_type = 'Collections'
            OR amount_past_due > 300
            LIMIT 10
        """)
        
        test_members = cursor.fetchall()
        
        print(f"Found {len(test_members)} test members:")
        for member in test_members:
            id, full_name, agreement_type, amount_past_due, status_message, status = member
            print(f"  {full_name}: {agreement_type}, ${amount_past_due}, {status_message}")
        
        print(f"\n=== TESTING UPDATED CATEGORIZATION ===")
        
        # Initialize DatabaseManager and test categorization
        db_manager = DatabaseManager()
        
        # Simulate member data for categorization test
        test_member_data = []
        for member in test_members:
            id, full_name, agreement_type, amount_past_due, status_message, status = member
            
            member_dict = {
                'prospect_id': str(id),
                'full_name': full_name,
                'agreement_type': agreement_type,
                'amount_past_due': amount_past_due,
                'status_message': status_message,
                'status': status,
                'phone': '555-0000',  # Dummy data for required fields
                'email': f'{full_name.lower().replace(" ", ".")}@test.com',
                'member_since': '2023-01-01',
                'last_checkin': '2024-01-01',
                'agreement_id': 'test_123' if agreement_type != 'Collections' else None,
                'agreement_guid': 'test-guid'
            }
            test_member_data.append(member_dict)
        
        # Test the categorization by running save_members_to_db
        print(f"Running categorization test with {len(test_member_data)} members...")
        result = db_manager.save_members_to_db(test_member_data)
        
        if result:
            print("✅ Categorization test completed successfully!")
            
            # Check the results
            print(f"\n=== CATEGORIZATION RESULTS ===")
            for member_dict in test_member_data:
                member_id = member_dict['prospect_id']
                full_name = member_dict['full_name']
                agreement_type = member_dict['agreement_type']
                amount_past_due = member_dict['amount_past_due']
                
                cursor.execute("""
                    SELECT category, status_message, classified_at
                    FROM member_categories 
                    WHERE member_id = ?
                """, (member_id,))
                
                category_result = cursor.fetchone()
                if category_result:
                    category, status_msg, classified_at = category_result
                    print(f"  {full_name}:")
                    print(f"    Agreement: {agreement_type}")
                    print(f"    Past Due: ${amount_past_due}")
                    print(f"    Category: {category}")
                    print(f"    Status: {status_msg}")
                    print(f"    Updated: {classified_at}")
                    print()
        else:
            print("❌ Categorization test failed!")
        
        # Show current category counts
        print(f"\n=== CURRENT CATEGORY COUNTS ===")
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM member_categories 
            GROUP BY category 
            ORDER BY count DESC
        """)
        
        categories = cursor.fetchall()
        total = sum(count for _, count in categories)
        
        for category, count in categories:
            print(f"  {category}: {count}")
        
        print(f"Total: {total}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing categorization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_categorization_logic()