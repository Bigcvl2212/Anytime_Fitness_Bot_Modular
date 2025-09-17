#!/usr/bin/env python3
"""
Quick test script to check member status categories for messaging page
"""
import sys
sys.path.append('.')
from src.services.database_manager import DatabaseManager

def test_member_categories():
    db_manager = DatabaseManager()
    
    try:
        conn = db_manager.get_connection()
        cursor = db_manager.get_cursor(conn)
        
        # Get member status message counts
        cursor.execute("""
            SELECT status_message, COUNT(*) as count
            FROM members 
            WHERE status_message IS NOT NULL AND status_message != ''
            GROUP BY status_message
            ORDER BY count DESC
        """)
        
        print("Member Status Messages:")
        status_counts = {}
        for row in cursor.fetchall():
            status_msg = row[0]
            count = row[1]
            status_counts[status_msg] = count
            print(f"  '{status_msg}': {count} members")
        
        # Test the specific categories the messaging page is looking for
        print("\nExpected Categories for Messaging:")
        expected_categories = [
            'Member is in good standing',
            'Pay Per Visit Member',
            'Past Due 6-30 days',
            'Past Due more than 30 days.',
            'Member will expire within 30 days.',
            'Comp Member',
            'Staff Member'
        ]
        
        for category in expected_categories:
            count = status_counts.get(category, 0)
            print(f"  '{category}': {count} members")
        
        # Check total members
        cursor.execute("SELECT COUNT(*) FROM members")
        total = cursor.fetchone()[0]
        print(f"\nTotal members in database: {total}")
        
        # Check if training_clients table exists and has data
        cursor.execute("SELECT COUNT(*) FROM training_clients")
        training_count = cursor.fetchone()[0]
        print(f"Training clients in database: {training_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_member_categories()