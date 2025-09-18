#!/usr/bin/env python3
"""
Debug script to test training clients saving functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager

def test_training_client_save():
    """Test saving training clients to debug the '0' error"""
    print("🔍 Testing training client save functionality...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Test data similar to what's causing the error
    test_member_data = [{
        'member_id': '192158842',
        'clubos_member_id': '192158842', 
        'first_name': 'Test',
        'last_name': 'User',
        'full_name': 'Test User',
        'member_name': 'Test User',
        'email': 'test@example.com',
        'phone': '555-1234',
        'status': 'Active',
        'trainer_name': 'Test Trainer',
        'membership_type': 'Monthly',
        'source': 'Test',
        'active_packages': [],
        'package_summary': 'None',
        'package_details': [],
        'past_due_amount': 0.0,
        'total_past_due': 0.0,
        'payment_status': 'Current',
        'sessions_remaining': 0,
        'last_session': None,
        'financial_summary': 'Current'
    }]
    
    try:
        print(f"� Database type: {db_manager.db_type}")
        print(f"📋 Test member data: {test_member_data[0]['member_id']}")
        
        # Test the save function
        result = db_manager.save_training_clients_to_db(test_member_data)
        print(f"✅ Save result: {result}")
        
        # Verify the data was saved
        saved_client = db_manager.execute_query(
            "SELECT * FROM training_clients WHERE member_id = ?", 
            ('192158842',),
            fetch_one=True
        )
        print(f"🔍 Saved client: {saved_client}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        print(f"❌ Error type: {type(e)}")
        print(f"❌ Error repr: {repr(e)}")
        import traceback
        traceback.print_exc()

def test_simple_query():
    """Test a simple query to verify database connection"""
    print("🔍 Testing simple database query...")
    
    db_manager = DatabaseManager()
    
    try:
        # Test a simple SELECT query
        result = db_manager.execute_query("SELECT 1 as test_value", fetch_one=True)
        print(f"✅ Simple query result: {result}")
        
        # Test parameter conversion
        result = db_manager.execute_query("SELECT ? as param_test", ('test_param',), fetch_one=True)
        print(f"✅ Parameter query result: {result}")
        
    except Exception as e:
        print(f"❌ Simple query error: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        traceback.print_exc()

def check_existing_training_clients():
    """Check existing training clients in database"""
    print("🔍 Checking existing training clients...")
    
    db_manager = DatabaseManager()
    
    try:
        # Get total count
        result = db_manager.execute_query("SELECT COUNT(*) as count FROM training_clients")
        if result:
            total_count = result[0]['count']
            print(f"📊 Total training clients: {total_count}")
            
            # Check for the specific member causing issues
            specific_member = db_manager.execute_query(
                "SELECT * FROM training_clients WHERE member_id = ? OR clubos_member_id = ?",
                ('192158842', '192158842'),
                fetch_one=True
            )
            
            if specific_member:
                print(f"🔍 Found member 192158842: {specific_member}")
            else:
                print("❌ Member 192158842 not found in database")
                
    except Exception as e:
        print(f"❌ Error checking existing clients: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_existing_training_clients()
    test_simple_query()
    test_training_client_save()
        if result:
            total_count = result[0]['count']
        print(f"📊 Total training clients in database: {total_count}")
    else:
        print("❌ No results from training_clients count query")
        
    # Get a few sample records
    sample_result = db_manager.execute_query("""
        SELECT member_name, first_name, last_name, member_id, created_at 
        FROM training_clients 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    if sample_result:
        print(f"\n📋 Sample training clients (showing {len(sample_result)}):")
        for i, client in enumerate(sample_result):
            print(f"  {i+1}. {client['member_name']} ({client['first_name']} {client['last_name']}) - ID: {client['member_id']}")
    else:
        print("❌ No sample training clients found")
        
    # Check for specific names from the error logs
    test_names = ['David Berendt', 'Alejandra Espinoza', 'Grace Sphatt', 'Dennis Rost']
    print(f"\n🔍 Checking for specific names that failed:")
    
    for name in test_names:
        result = db_manager.execute_query("""
            SELECT member_name, first_name, last_name 
            FROM training_clients 
            WHERE LOWER(member_name) LIKE LOWER(?) 
               OR LOWER(first_name || ' ' || last_name) LIKE LOWER(?)
            LIMIT 3
        """, (f'%{name}%', f'%{name}%'))
        
        if result:
            print(f"  ✅ Found matches for '{name}':")
            for match in result:
                print(f"    - {match['member_name']} ({match['first_name']} {match['last_name']})")
        else:
            print(f"  ❌ No matches found for '{name}'")

except Exception as e:
    print(f"❌ Error checking training clients: {e}")
    import traceback
    traceback.print_exc()