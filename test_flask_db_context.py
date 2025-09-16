#!/usr/bin/env python3
"""
Test if the Flask app database manager is using the same database as our direct connection
"""

import sys
sys.path.append('.')

from src.services.database_manager import DatabaseManager

def test_flask_db_context():
    """Compare direct database connection vs Flask database manager"""
    
    print("🔍 Comparing database connections...")
    
    # Test 1: Direct database manager (what our test used)
    print("\n1. Direct DatabaseManager connection:")
    try:
        db_manager = DatabaseManager()
        print(f"   Database type: {db_manager.db_type}")
        print(f"   Database file/host: {getattr(db_manager, 'db_path', getattr(db_manager, 'host', 'Unknown'))}")
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM members")
        count = cursor.fetchone()[0]
        print(f"   Members count: {count}")
        
        # Test a specific query to see if it returns data
        cursor.execute("SELECT first_name, last_name FROM members LIMIT 3")
        samples = cursor.fetchall()
        print(f"   Sample data: {len(samples)} rows")
        for i, row in enumerate(samples, 1):
            print(f"     {i}. {row[0]} {row[1]}")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Direct connection failed: {e}")
    
    # Test 2: Flask app style connection (simulate what the routes do)
    print("\n2. Flask-style database connection:")
    try:
        # This simulates what happens in Flask routes
        from flask import Flask
        
        app = Flask(__name__)
        app.db_manager = DatabaseManager()
        
        with app.app_context():
            conn = app.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Same query as the Flask route
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
            print(f"   Flask-style query returned: {len(members)} members")
            
            if members:
                print("   Sample Flask data:")
                for i, member in enumerate(members[:3], 1):
                    print(f"     {i}. {member.get('first_name')} {member.get('last_name')} - Status: '{member.get('status_message')}'")
            
            conn.close()
        
    except Exception as e:
        print(f"   ❌ Flask-style connection failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Database context comparison complete")

if __name__ == "__main__":
    test_flask_db_context()