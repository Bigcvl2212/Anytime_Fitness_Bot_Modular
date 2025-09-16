#!/usr/bin/env python3

from src.services.database_manager import DatabaseManager

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()

# Check what's actually in the database right now
cursor.execute('SELECT member_name, past_due_amount, total_past_due, payment_status FROM training_clients WHERE payment_status = "Past Due" LIMIT 10')

results = cursor.fetchall()
print('Training clients marked as Past Due in database:')
for row in results:
    print(f'  {row[0]}: past_due={row[1]}, total={row[2]}, status={row[3]}')

# Check if any have actual past due amounts
cursor.execute('SELECT COUNT(*) FROM training_clients WHERE past_due_amount > 0 OR total_past_due > 0')
actual_count = cursor.fetchone()[0]
print(f'\nTraining clients with actual past due amounts > 0: {actual_count}')

# Check all training clients to see the data
cursor.execute('SELECT member_name, past_due_amount, total_past_due, payment_status FROM training_clients LIMIT 5')
all_results = cursor.fetchall()
print('\nSample of all training clients:')
for row in all_results:
    print(f'  {row[0]}: past_due={row[1]}, total={row[2]}, status={row[3]}')

conn.close()