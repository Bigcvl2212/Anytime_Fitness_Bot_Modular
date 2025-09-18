#!/usr/bin/env python3
"""
Check what exact status messages are counted for past_due category
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager

def check_past_due_breakdown():
    """Check what status messages are being counted in past_due category"""
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        print('=== PAST DUE CATEGORY BREAKDOWN ===')
        
        # Check each status message that counts toward past_due
        past_due_statuses = [
            'Past Due 6-30 days',
            'Past Due more than 30 days.',
            'Invalid Billing Information.',
            'Invalid/Bad Address information.',
            'Member is pending cancel',
            'Member will expire within 30 days.'
        ]
        
        total_past_due = 0
        for status in past_due_statuses:
            cursor.execute("""
                SELECT COUNT(*) FROM members WHERE status_message = ?
            """, (status,))
            count = cursor.fetchone()[0]
            total_past_due += count
            print(f'"{status}": {count}')
        
        print(f'\nTotal past_due category count: {total_past_due}')
        
        # Check what we actually have in database
        cursor.execute("""
            SELECT status_message, COUNT(*) 
            FROM members 
            WHERE status_message IN (
                'Past Due 6-30 days',
                'Past Due more than 30 days.',
                'Invalid Billing Information.',
                'Invalid/Bad Address information.',
                'Member is pending cancel',
                'Member will expire within 30 days.'
            )
            GROUP BY status_message
            ORDER BY COUNT(*) DESC
        """)
        
        actual_counts = cursor.fetchall()
        print(f'\nActual status message breakdown:')
        actual_total = 0
        for status, count in actual_counts:
            actual_total += count
            print(f'  "{status}": {count}')
        
        print(f'\nActual total: {actual_total}')
        
        # Get the database manager's count for comparison
        counts = db.get_category_counts()
        print(f'Database manager past_due count: {counts.get("past_due", 0)}')
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_past_due_breakdown()