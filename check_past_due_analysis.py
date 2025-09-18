#!/usr/bin/env python3
"""
Analyze what members are being counted as past due
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager

def analyze_past_due():
    """Analyze past due member counts"""
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        print('=== PAST DUE ANALYSIS ===')
        
        # Check members with past due status messages (main criteria)
        cursor.execute("""
            SELECT COUNT(*) as count, 
                   COALESCE(SUM(amount_past_due), 0) as total_amount
            FROM members 
            WHERE status_message LIKE '%Past Due 6-30 days%' 
               OR status_message LIKE '%Past Due more than 30 days%'
        """)
        result = cursor.fetchone()
        print(f'Members with past due status messages: {result[0]} (${result[1]:.2f} total)')
        
        # Check members with amount_past_due > 0 but no past due status message
        cursor.execute("""
            SELECT COUNT(*) as count,
                   COALESCE(SUM(amount_past_due), 0) as total_amount
            FROM members 
            WHERE amount_past_due > 0 
              AND status_message NOT LIKE '%Past Due%'
        """)
        result = cursor.fetchone()
        print(f'Members with amount > 0 but no past due status: {result[0]} (${result[1]:.2f} total)')
        
        # Show the actual past due status messages
        cursor.execute("""
            SELECT status_message, COUNT(*) 
            FROM members 
            WHERE status_message LIKE '%Past Due%' 
            GROUP BY status_message
        """)
        past_due_statuses = cursor.fetchall()
        print(f'\nPast due status breakdown:')
        for status, count in past_due_statuses:
            print(f'  "{status}": {count}')
        
        # Show some examples of members counted as past due
        cursor.execute("""
            SELECT first_name, last_name, status_message, amount_past_due
            FROM members 
            WHERE status_message LIKE '%Past Due 6-30 days%' 
               OR status_message LIKE '%Past Due more than 30 days%'
            ORDER BY amount_past_due DESC
            LIMIT 10
        """)
        examples = cursor.fetchall()
        print(f'\nTop 10 past due members:')
        for first, last, status, amount in examples:
            print(f'  {first} {last}: "{status}" - ${amount:.2f}')
        
        # Check the database_manager logic
        print(f'\n=== DATABASE MANAGER LOGIC CHECK ===')
        counts = db.get_category_counts()
        print(f'Past due count from get_category_counts(): {counts.get("past_due", 0)}')
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_past_due()