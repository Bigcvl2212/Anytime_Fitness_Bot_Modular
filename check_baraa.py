#!/usr/bin/env python3

from src.services.database_manager import DatabaseManager

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()

# Get Baraa's data from the database
cursor.execute('SELECT * FROM training_clients WHERE member_name LIKE "%Baraa%"')

result = cursor.fetchone()
if result:
    # Get column names
    cursor.execute('PRAGMA table_info(training_clients)')
    columns = [row[1] for row in cursor.fetchall()]
    
    # Create dictionary
    baraa_data = dict(zip(columns, result))
    
    print('BARAA\'S TRAINING CLIENT DATA:')
    print(f'  Name: {baraa_data.get("member_name")}')
    print(f'  Past Due Amount: ${baraa_data.get("past_due_amount")}')
    print(f'  Total Past Due: ${baraa_data.get("total_past_due")}')
    print(f'  Payment Status: {baraa_data.get("payment_status")}')
    print(f'  Active Packages: {baraa_data.get("active_packages")}')
    print(f'  Package Details: {baraa_data.get("package_details")}')
    print(f'  Financial Summary: {baraa_data.get("financial_summary")}')
    print(f'  Last Updated: {baraa_data.get("last_updated")}')
    print(f'  ClubOS Member ID: {baraa_data.get("clubos_member_id")}')
else:
    print('Baraa not found in database')

conn.close()
