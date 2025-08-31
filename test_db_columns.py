#!/usr/bin/env python3
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.database_manager import DatabaseManager

def test_database_columns():
    """Test if database columns are accessible by DatabaseManager"""
    try:
        # Initialize database manager the same way the app does
        db_manager = DatabaseManager()
        
        print(f"Database path: {os.path.abspath(db_manager.db_path)}")
        
        # Test direct SQL query
        import sqlite3
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(training_clients)")
        columns = cursor.fetchall()
        
        print(f"Total columns found: {len(columns)}")
        
        # Check for problematic columns
        problem_columns = ['full_name', 'first_name', 'last_name']
        for col_name in problem_columns:
            found = [col for col in columns if col[1] == col_name]
            if found:
                print(f"✅ Column '{col_name}' found: {found[0]}")
            else:
                print(f"❌ Column '{col_name}' NOT found")
        
        # Test insertion with simple data
        test_data = {
            'member_id': '12345',
            'clubos_member_id': '12345', 
            'full_name': 'Test User',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com'
        }
        
        print(f"\\n🧪 Testing insertion with data: {test_data}")
        
        # Try to insert test data
        try:
            cursor.execute("""
                INSERT INTO training_clients (
                    member_id, clubos_member_id, full_name, first_name, last_name, email
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                test_data['member_id'],
                test_data['clubos_member_id'], 
                test_data['full_name'],
                test_data['first_name'],
                test_data['last_name'],
                test_data['email']
            ))
            
            conn.commit()
            print("✅ Test insertion successful!")
            
            # Clean up test data
            cursor.execute("DELETE FROM training_clients WHERE member_id = ?", (test_data['member_id'],))
            conn.commit()
            print("✅ Test cleanup successful!")
            
        except Exception as e:
            print(f"❌ Test insertion failed: {e}")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    test_database_columns()
