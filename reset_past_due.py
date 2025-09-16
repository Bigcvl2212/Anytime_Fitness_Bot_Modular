#!/usr/bin/env python3

from src.services.database_manager import DatabaseManager

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()

# Reset all people marked as past due back to current
cursor.execute('UPDATE training_clients SET payment_status = "Current", past_due_amount = 0.0, total_past_due = 0.0, financial_summary = "Current" WHERE payment_status = "Past Due"')

affected = cursor.rowcount
conn.commit()

print(f'Reset {affected} training clients from Past Due back to Current')

conn.close()
