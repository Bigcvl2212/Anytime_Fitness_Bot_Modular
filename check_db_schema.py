#!/usr/bin/env python3
"""Check database schema to see what columns exist"""

import sqlite3
import json

def check_training_clients_schema():
    """Check the current schema of the training_clients table"""
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(training_clients)")
        columns = cursor.fetchall()
        
        print("Current training_clients table schema:")
        print("=" * 50)
        for col in columns:
            print(f"Column {col[1]}: {col[2]} (Default: {col[4]})")
        
        # Check if specific columns exist
        column_names = [col[1] for col in columns]
        required_columns = [
            'clubos_member_id', 'member_name', 'first_name', 'last_name', 
            'trainer_name', 'active_packages', 'past_due_amount', 'total_past_due', 
            'payment_status', 'sessions_remaining', 'last_session', 'last_updated'
        ]
        
        print("\nMissing columns:")
        print("=" * 50)
        for col in required_columns:
            if col not in column_names:
                print(f"❌ {col}")
            else:
                print(f"✅ {col}")
        
        # Check sample data
        cursor.execute("SELECT * FROM training_clients LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print(f"\nSample row has {len(sample)} columns")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_training_clients_schema()
