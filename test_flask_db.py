#!/usr/bin/env python3
"""
Test script to debug why Flask API is returning empty data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager

def test_flask_database_connection():
    """Test what the Flask app sees in the database"""
    try:
        # Test the same way the Flask route does it
        db = DatabaseManager()
        
        # Check if db_path is being set correctly
        print(f"DatabaseManager db_path: {getattr(db, 'db_path', 'Not set')}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Database file exists: {os.path.exists('gym_bot.db')}")
        print(f"Absolute path exists: {os.path.exists(os.path.abspath('gym_bot.db'))}")
        
        # Test database connection
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check training clients (like the API route does)
        cursor.execute("SELECT COUNT(*) FROM training_clients")
        training_count = cursor.fetchone()[0]
        print(f"Training clients count: {training_count}")
        
        # Check members
        cursor.execute("SELECT COUNT(*) FROM members")
        members_count = cursor.fetchone()[0]
        print(f"Members count: {members_count}")
        
        # Check prospects
        cursor.execute("SELECT COUNT(*) FROM prospects")
        prospects_count = cursor.fetchone()[0]
        print(f"Prospects count: {prospects_count}")
        
        # Show a sample training client record
        if training_count > 0:
            cursor.execute("SELECT member_name, payment_status, total_past_due FROM training_clients LIMIT 3")
            sample_clients = cursor.fetchall()
            print(f"Sample training clients: {sample_clients}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing database connection: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_flask_database_connection()