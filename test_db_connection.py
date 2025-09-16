#!/usr/bin/env python3
"""
Quick database connection test to diagnose the members API issue
"""

import sys
sys.path.append('.')

from src.services.database_manager import DatabaseManager

def test_database_queries():
    """Test the exact queries used by the API endpoints"""
    try:
        print("🔍 Testing database queries...")
        
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Test the exact query from /api/members/all
        print("\n1. Testing /api/members/all query:")
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
        
        members = cursor.fetchall()
        print(f"   Query returned {len(members)} rows")
        
        if members:
            print("   Sample data:")
            for i, member in enumerate(members[:3], 1):
                print(f"   {i}. Name: {member[4]} {member[5]} | Status: '{member[9]}'")
        
        # Test prospects query
        print("\n2. Testing prospects query:")
        cursor.execute("SELECT COUNT(*) FROM prospects")
        prospect_count = cursor.fetchone()[0]
        print(f"   Prospects count: {prospect_count}")
        
        # Test training clients query
        print("\n3. Testing training clients query:")
        cursor.execute("SELECT COUNT(*) FROM training_clients")
        training_count = cursor.fetchone()[0]
        print(f"   Training clients count: {training_count}")
        
        # Check if there's a cache/connection issue
        print("\n4. Testing status message distribution:")
        cursor.execute("""
            SELECT status_message, COUNT(*) as count 
            FROM members 
            WHERE status_message IS NOT NULL 
            GROUP BY status_message 
            ORDER BY count DESC 
            LIMIT 5
        """)
        
        status_counts = cursor.fetchall()
        print("   Status message distribution:")
        for status, count in status_counts:
            print(f"   - '{status}': {count} members")
        
        conn.close()
        print("\n✅ Database queries completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database query test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database_queries()