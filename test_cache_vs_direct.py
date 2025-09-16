#!/usr/bin/env python3
"""
Test if the cache is causing the 0 records issue
"""

import sys
sys.path.append('.')

from src.services.database_manager import DatabaseManager
from flask import Flask

def test_cache_vs_direct():
    """Test if Flask app cache is interfering with database results"""
    
    print("🔍 Testing cache vs direct database access...")
    
    # Test 1: Direct database manager
    print("\n1. Direct database manager:")
    try:
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        cursor = db_manager.get_cursor(conn)
        
        cursor.execute("SELECT COUNT(*) FROM members")
        count = cursor.fetchone()[0]
        print(f"   Total members: {count}")
        
        if count > 0:
            cursor.execute("""
                SELECT prospect_id, first_name, last_name, status_message
                FROM members 
                ORDER BY full_name
                LIMIT 3
            """)
            
            members = [dict(row) for row in cursor.fetchall()]
            print(f"   Sample members: {len(members)}")
            for member in members:
                print(f"     - {member['first_name']} {member['last_name']} ({member['status_message']})")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Direct test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Flask app simulation with cache check
    print("\n2. Flask app with cache simulation:")
    try:
        app = Flask(__name__)
        app.db_manager = DatabaseManager()
        
        # Simulate the cache check from the route
        with app.app_context():
            # Check if cache exists (like the route does)
            cache_exists = hasattr(app, 'data_cache') and app.data_cache and app.data_cache.get('members')
            print(f"   Cache exists: {cache_exists}")
            
            if cache_exists:
                cached_members = app.data_cache['members']
                print(f"   Cached members: {len(cached_members)}")
                return
            
            # If no cache, go to database (same logic as route)
            conn = app.db_manager.get_connection()
            cursor = app.db_manager.get_cursor(conn)
            
            cursor.execute("""
                SELECT 
                    prospect_id,
                    id,
                    guid,
                    first_name,
                    last_name,
                    full_name,
                    email,
                    mobile_phone,
                    status,
                    status_message,
                    amount_past_due,
                    date_of_next_payment
                FROM members 
                ORDER BY full_name
                LIMIT 5
            """)
            
            members = [dict(row) for row in cursor.fetchall()]
            print(f"   Flask query returned: {len(members)} members")
            
            if members:
                for i, member in enumerate(members[:3], 1):
                    print(f"     {i}. {member['first_name']} {member['last_name']} - {member['status_message']}")
            else:
                print("   ❌ Flask query returned 0 members!")
                
                # Debug: check if the table actually has data
                cursor.execute("SELECT COUNT(*) FROM members")
                db_count = cursor.fetchone()[0]
                print(f"   Debug: Database actually has {db_count} members")
                
                # Check if the complex SELECT is the issue
                cursor.execute("SELECT first_name, last_name FROM members LIMIT 3")
                simple_members = cursor.fetchall()
                print(f"   Debug: Simple query returned {len(simple_members)} members")
            
            conn.close()
        
    except Exception as e:
        print(f"   ❌ Flask simulation failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Cache vs direct testing complete")

if __name__ == "__main__":
    test_cache_vs_direct()