#!/usr/bin/env python3
"""Find all revenue-related columns in the database"""

import sqlite3

def analyze_revenue_columns():
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()

    print("=== MEMBERS TABLE REVENUE COLUMNS ===")
    cursor.execute('PRAGMA table_info(members)')
    members_columns = cursor.fetchall()
    
    # Look for columns that might contain payment/revenue data
    revenue_related = []
    for col in members_columns:
        col_name = col[1].lower()
        if any(keyword in col_name for keyword in ['cost', 'amount', 'payment', 'fee', 'price', 'revenue', 'recurring', 'monthly', 'billing']):
            revenue_related.append(col)
    
    print("Revenue-related columns in members table:")
    for col in revenue_related:
        print(f"  {col[1]} ({col[2]}) - {col}")
    
    # Sample the actual data for agreement_recurring_cost
    if 'agreement_recurring_cost' in [c[1] for c in members_columns]:
        cursor.execute('''
            SELECT first_name, last_name, agreement_recurring_cost, status_message, amount_past_due
            FROM members 
            WHERE agreement_recurring_cost IS NOT NULL AND agreement_recurring_cost > 0
            ORDER BY agreement_recurring_cost DESC
            LIMIT 10
        ''')
        print(f"\nSample members with agreement_recurring_cost:")
        for row in cursor.fetchall():
            print(f"  {row[0]} {row[1]}: ${row[2]} - {row[3]}")
    
    print(f"\n=== TRAINING CLIENTS TABLE REVENUE COLUMNS ===")
    cursor.execute('PRAGMA table_info(training_clients)')
    training_columns = cursor.fetchall()
    
    # Look for revenue-related columns in training clients
    training_revenue_cols = []
    for col in training_columns:
        col_name = col[1].lower()
        if any(keyword in col_name for keyword in ['cost', 'amount', 'payment', 'fee', 'price', 'revenue', 'recurring', 'monthly', 'billing', 'invoice', 'package']):
            training_revenue_cols.append(col)
    
    print("Revenue-related columns in training_clients table:")
    for col in training_revenue_cols:
        print(f"  {col[1]} ({col[2]}) - {col}")
    
    # Sample training client financial data
    cursor.execute('''
        SELECT member_name, package_details, financial_summary, past_due_amount, payment_status
        FROM training_clients 
        WHERE package_details IS NOT NULL OR financial_summary IS NOT NULL
        LIMIT 10
    ''')
    print(f"\nSample training client financial data:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: Package={row[1][:50] if row[1] else 'None'}... Financial={row[2]} Past_Due=${row[3]} Status={row[4]}")
    
    # Look for invoice or payment amount patterns in package_details
    cursor.execute('''
        SELECT member_name, package_details
        FROM training_clients 
        WHERE package_details LIKE '%$%' OR package_details LIKE '%amount%' OR package_details LIKE '%payment%'
        LIMIT 5
    ''')
    print(f"\nTraining clients with payment info in package_details:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()

if __name__ == "__main__":
    analyze_revenue_columns()