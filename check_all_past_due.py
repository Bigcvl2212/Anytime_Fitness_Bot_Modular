#!/usr/bin/env python3

from src.services.database_manager import DatabaseManager

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()

# Get all people marked as past due
cursor.execute('SELECT member_name, past_due_amount, total_past_due, payment_status, financial_summary, package_details FROM training_clients WHERE payment_status = "Past Due"')

results = cursor.fetchall()
print('ALL PEOPLE MARKED AS PAST DUE:')
for row in results:
    print(f'  {row[0]}: ${row[1]} past due, status={row[2]}, summary={row[3]}, details={row[4][:50]}...')

conn.close()
