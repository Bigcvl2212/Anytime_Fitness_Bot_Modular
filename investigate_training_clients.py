#!/usr/bin/env python3
"""Investigate training client payment data and find the correct revenue fields"""

import sqlite3
import json

def investigate_training_client_data():
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()

    print("=== TRAINING CLIENT DATA INVESTIGATION ===")
    
    # Get all columns and sample data
    cursor.execute('SELECT * FROM training_clients LIMIT 3')
    sample_data = cursor.fetchall()
    
    cursor.execute('PRAGMA table_info(training_clients)')
    columns = cursor.fetchall()
    
    print("All columns in training_clients:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    print(f"\n=== SAMPLE TRAINING CLIENT RECORDS ===")
    if sample_data:
        column_names = [col[1] for col in columns]
        for i, record in enumerate(sample_data):
            print(f"\nRecord {i+1}:")
            for j, value in enumerate(record):
                if value is not None and str(value).strip():
                    print(f"  {column_names[j]}: {value}")
    
    # Look specifically at package_details which might contain payment info
    print(f"\n=== PACKAGE DETAILS ANALYSIS ===")
    cursor.execute('''
        SELECT member_name, package_details, financial_summary, payment_status
        FROM training_clients 
        WHERE package_details IS NOT NULL AND package_details != '' AND package_details != '[]'
        LIMIT 10
    ''')
    
    package_details = cursor.fetchall()
    print(f"Found {len(package_details)} training clients with package details:")
    for record in package_details:
        print(f"\nClient: {record[0]}")
        print(f"  Package Details: {record[1]}")
        print(f"  Financial Summary: {record[2]}")
        print(f"  Payment Status: {record[3]}")
        
        # Try to parse package_details as JSON
        try:
            if record[1] and record[1].strip() and record[1] != '[]':
                parsed = json.loads(record[1])
                if parsed:
                    print(f"  Parsed Package Details: {parsed}")
        except:
            print(f"  Package Details (raw text): {record[1]}")
    
    # Check if any training clients actually have past_due_amount > 0
    cursor.execute('SELECT COUNT(*) FROM training_clients WHERE past_due_amount > 0')
    past_due_count = cursor.fetchone()[0]
    print(f"\n=== PAST DUE ANALYSIS ===")
    print(f"Training clients with past_due_amount > 0: {past_due_count}")
    
    cursor.execute('SELECT COUNT(*) FROM training_clients WHERE total_past_due > 0')
    total_past_due_count = cursor.fetchone()[0]
    print(f"Training clients with total_past_due > 0: {total_past_due_count}")
    
    # Check payment statuses
    cursor.execute('''
        SELECT payment_status, COUNT(*) as count 
        FROM training_clients 
        WHERE payment_status IS NOT NULL 
        GROUP BY payment_status
    ''')
    payment_statuses = cursor.fetchall()
    print(f"\nPayment status breakdown:")
    for status, count in payment_statuses:
        print(f"  {status}: {count} clients")
    
    # Look for any fields that might contain dollar amounts
    print(f"\n=== SEARCHING FOR DOLLAR AMOUNTS ===")
    cursor.execute('''
        SELECT member_name, package_details, financial_summary, active_packages
        FROM training_clients 
        WHERE package_details LIKE '%$%' 
           OR financial_summary LIKE '%$%' 
           OR active_packages LIKE '%$%'
        LIMIT 5
    ''')
    
    dollar_records = cursor.fetchall()
    print(f"Records containing dollar signs: {len(dollar_records)}")
    for record in dollar_records:
        print(f"\nClient: {record[0]}")
        if '$' in str(record[1]):
            print(f"  Package Details: {record[1]}")
        if '$' in str(record[2]):
            print(f"  Financial Summary: {record[2]}")
        if '$' in str(record[3]):
            print(f"  Active Packages: {record[3]}")

    conn.close()

if __name__ == "__main__":
    investigate_training_client_data()