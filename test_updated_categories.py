#!/usr/bin/env python3
"""
Test the updated category counts with separated past due and yellow categories
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager

def test_updated_categories():
    """Test the new category separation"""
    try:
        db = DatabaseManager()
        counts = db.get_category_counts()

        print('=== UPDATED CATEGORY COUNTS ===')
        for category, count in counts.items():
            print(f'  {category}: {count}')

        total_categorized = sum(counts.values())
        print(f'\nTotal categorized: {total_categorized}')
        print(f'Database total: 531')
        print(f'Difference: {531 - total_categorized}')

        # Verify the separation
        print(f'\n=== VERIFICATION ===')
        past_due_count = counts.get('past_due', 0)
        yellow_count = counts.get('yellow', 0)
        combined_old = past_due_count + yellow_count
        
        print(f'Past Due (money owed): {past_due_count}')
        print(f'Yellow (account issues): {yellow_count}')
        print(f'Combined (old past_due total): {combined_old}')
        
        print(f'\n=== BREAKDOWN DETAILS ===')
        
        # Show past due details
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status_message, COUNT(*) FROM members 
            WHERE status_message IN ('Past Due 6-30 days', 'Past Due more than 30 days.')
            GROUP BY status_message
        """)
        past_due_breakdown = cursor.fetchall()
        print(f'Past Due Members:')
        for status, count in past_due_breakdown:
            print(f'  "{status}": {count}')
        
        cursor.execute("""
            SELECT status_message, COUNT(*) FROM members 
            WHERE status_message IN (
                'Invalid Billing Information.',
                'Invalid/Bad Address information.',
                'Member is pending cancel',
                'Member will expire within 30 days.'
            )
            GROUP BY status_message
        """)
        yellow_breakdown = cursor.fetchall()
        print(f'Yellow Members:')
        for status, count in yellow_breakdown:
            print(f'  "{status}": {count}')
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_updated_categories()