#!/usr/bin/env python3

"""
Check Training Clients Table Schema
=================================

This script checks the actual training_clients table schema to understand the column mismatch.
"""

import sqlite3

def check_training_clients_schema():
    """Check the training_clients table schema and identify the issue"""
    
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(training_clients)")
        columns = cursor.fetchall()
        
        print("🔍 Full training_clients table schema:")
        print(f"Total columns: {len(columns)}")
        print()
        
        for i, col in enumerate(columns, 1):
            col_id, name, data_type, not_null, default_value, primary_key = col
            null_info = "NOT NULL" if not_null else "NULL"
            default_info = f"DEFAULT: {default_value}" if default_value else "No default"
            pk_info = " [PRIMARY KEY]" if primary_key else ""
            
            print(f"{i:2d}. {name} ({data_type}) - {null_info} - {default_info}{pk_info}")
        
        # Now check which columns we're trying to insert into
        insert_columns = [
            "member_id", "clubos_member_id", "first_name", "last_name", "member_name",
            "email", "phone", "trainer_name", "membership_type", "source",
            "active_packages", "package_summary", "package_details",
            "past_due_amount", "total_past_due", "payment_status",
            "sessions_remaining", "last_session", "financial_summary",
            "last_updated", "created_at"
        ]
        
        print(f"\n📊 Columns we're trying to insert into: {len(insert_columns)}")
        for i, col in enumerate(insert_columns, 1):
            print(f"  {i:2d}. {col}")
        
        # Check if all our columns exist in the table
        table_columns = [col[1] for col in columns]
        missing_columns = [col for col in insert_columns if col not in table_columns]
        extra_columns = [col for col in table_columns if col not in insert_columns]
        
        if missing_columns:
            print(f"\n❌ Missing columns in table: {missing_columns}")
        
        if extra_columns:
            print(f"\n📋 Extra columns in table (not in INSERT): {extra_columns}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")

if __name__ == "__main__":
    check_training_clients_schema()