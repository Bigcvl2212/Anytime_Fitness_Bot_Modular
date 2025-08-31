#!/usr/bin/env python3
"""Check members table schema to see what columns exist"""

import sqlite3
import json

def check_members_schema():
    """Check the current schema of the members table"""
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(members)")
        columns = cursor.fetchall()
        
        print("Current members table schema:")
        print("=" * 50)
        for col in columns:
            print(f"Column {col[1]}: {col[2]} (Default: {col[4]})")
        
        # Check if specific columns exist
        column_names = [col[1] for col in columns]
        required_columns = [
            'agreement_recurring_cost', 'agreement_status', 'agreement_type', 
            'agreement_start_date', 'agreement_end_date', 'agreement_billing_frequency',
            'agreement_name', 'agreement_description', 'base_amount_past_due',
            'late_fees', 'missed_payments'
        ]
        
        print("\nNew agreement columns:")
        print("=" * 50)
        for col in required_columns:
            if col not in column_names:
                print(f"❌ {col}")
            else:
                print(f"✅ {col}")
        
        # Check sample data
        cursor.execute("SELECT * FROM members LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print(f"\nSample row has {len(sample)} columns")
            
            # Get column names for sample data
            cursor.execute("SELECT * FROM members LIMIT 1")
            column_names = [description[0] for description in cursor.description]
            print(f"Column names: {column_names}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_members_schema()
