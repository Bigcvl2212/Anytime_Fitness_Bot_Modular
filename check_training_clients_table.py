#!/usr/bin/env python3
"""
Check training_clients table structure and past due clients
"""

import sqlite3
import json

def main():
    print("🔍 INVESTIGATING: Training Clients Table for Campaign Integration")
    print("=" * 70)
    
    try:
        # Connect to database
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Check if training_clients table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='training_clients'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ training_clients table does NOT exist")
            print("\n📋 Available tables:")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                print(f"   - {table[0]}")
            conn.close()
            return
        
        print("✅ training_clients table exists")
        
        # Get table schema
        cursor.execute("PRAGMA table_info(training_clients)")
        schema = cursor.fetchall()
        print(f"\n📊 Training Clients Table Schema:")
        for column in schema:
            print(f"   - {column[1]} ({column[2]})")
        
        # Get sample data
        cursor.execute("SELECT * FROM training_clients LIMIT 5")
        sample_data = cursor.fetchall()
        
        if not sample_data:
            print("\n❌ No data in training_clients table")
        else:
            print(f"\n📋 Sample Training Clients Data ({len(sample_data)} rows):")
            columns = [col[1] for col in schema]
            for i, row in enumerate(sample_data):
                print(f"\n   Client {i+1}:")
                for j, value in enumerate(row):
                    print(f"     {columns[j]}: {value}")
        
        # Check for past due clients specifically
        cursor.execute("SELECT COUNT(*) FROM training_clients")
        total_clients = cursor.fetchone()[0]
        print(f"\n📊 Total training clients: {total_clients}")
        
        # Look for payment status patterns
        print(f"\n🔍 Checking for payment status patterns...")
        
        # Check different possible status fields
        status_fields = ['agreement_status', 'payment_status']
        for field in status_fields:
            try:
                cursor.execute(f"SELECT DISTINCT {field} FROM training_clients WHERE {field} IS NOT NULL")
                distinct_values = cursor.fetchall()
                if distinct_values:
                    print(f"\n   📋 Distinct values in {field}:")
                    for value in distinct_values:
                        cursor.execute(f"SELECT COUNT(*) FROM training_clients WHERE {field} = ?", (value[0],))
                        count = cursor.fetchone()[0]
                        print(f"     - '{value[0]}': {count} clients")
            except sqlite3.OperationalError:
                print(f"   ⚪ Field '{field}' does not exist in training_clients table")
        
        # Look for any text fields that might contain "past due" or similar
        text_fields = ['member_name', 'package_name', 'raw_data']
        for field in text_fields:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM training_clients WHERE LOWER({field}) LIKE '%past%' OR LOWER({field}) LIKE '%due%' OR LOWER({field}) LIKE '%overdue%'")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"\n   🔍 Found {count} clients with 'past/due/overdue' in {field}")
                    cursor.execute(f"SELECT {field} FROM training_clients WHERE LOWER({field}) LIKE '%past%' OR LOWER({field}) LIKE '%due%' OR LOWER({field}) LIKE '%overdue%' LIMIT 3")
                    examples = cursor.fetchall()
                    for example in examples:
                        print(f"     Example: {example[0]}")
            except sqlite3.OperationalError:
                print(f"   ⚪ Field '{field}' does not exist in training_clients table")
        
        # Check members table status messages for comparison
        print(f"\n📋 For comparison, checking members table status messages:")
        try:
            cursor.execute("SELECT DISTINCT status_message FROM members WHERE status_message LIKE '%past%' OR status_message LIKE '%due%' ORDER BY status_message")
            past_due_statuses = cursor.fetchall()
            if past_due_statuses:
                print(f"   Members table has {len(past_due_statuses)} past due status types:")
                for status in past_due_statuses:
                    cursor.execute("SELECT COUNT(*) FROM members WHERE status_message = ?", (status[0],))
                    count = cursor.fetchone()[0]
                    print(f"     - '{status[0]}': {count} members")
            else:
                print("   No past due status messages found in members table")
        except sqlite3.OperationalError:
            print("   ⚪ members table doesn't exist or status_message field missing")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error investigating training clients: {e}")

if __name__ == "__main__":
    main()