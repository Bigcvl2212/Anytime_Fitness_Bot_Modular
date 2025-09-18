#!/usr/bin/env python3
"""
Find the unaccounted 16 members and their status messages
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager

def find_unaccounted_members():
    """Find the members not counted in any category"""
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        print('=== FINDING UNACCOUNTED MEMBERS ===')
        
        # Get all members NOT in any current category
        cursor.execute("""
            SELECT status_message, COUNT(*) as count
            FROM members 
            WHERE status_message NOT IN (
                -- Green
                'Member is in good standing', 'In good standing',
                -- Past Due
                'Past Due 6-30 days', 'Past Due more than 30 days.',
                -- Yellow
                'Invalid Billing Information.', 'Invalid/Bad Address information.',
                'Member is pending cancel', 'Member will expire within 30 days.',
                'Account has been cancelled.',
                -- Comp
                'Comp Member',
                -- PPV
                'Pay Per Visit Member'
            )
            AND status_message NOT LIKE '%frozen%' 
            AND status_message NOT LIKE '%Frozen%'
            AND status_message NOT IN ('Expired', 'Sent to Collections')
            AND status_message IS NOT NULL
            AND prospect_id NOT IN ('64309309', '55867562', '50909888', '62716557', '52750389') -- Staff
            AND (agreement_id IS NOT NULL OR amount_past_due = 0) -- Not collections
            GROUP BY status_message
            ORDER BY count DESC
        """)
        
        unaccounted = cursor.fetchall()
        total_unaccounted = sum(row[1] for row in unaccounted)
        
        print(f'Unaccounted members by status message:')
        for status, count in unaccounted:
            print(f'  "{status}": {count}')
        
        print(f'\nTotal unaccounted: {total_unaccounted}')
        
        # Also check for NULL status messages
        cursor.execute("""
            SELECT COUNT(*) FROM members 
            WHERE status_message IS NULL
            AND prospect_id NOT IN ('64309309', '55867562', '50909888', '62716557', '52750389')
            AND (agreement_id IS NOT NULL OR amount_past_due = 0)
        """)
        null_count = cursor.fetchone()[0]
        print(f'Members with NULL status_message: {null_count}')
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_unaccounted_members()