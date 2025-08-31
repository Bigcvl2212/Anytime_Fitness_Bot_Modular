#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check past due members
cursor.execute("""
    SELECT full_name, amount_past_due, base_amount_past_due, missed_payments, late_fees, status_message 
    FROM members 
    WHERE status_message LIKE '%Past Due%' 
    LIMIT 10
""")

results = cursor.fetchall()
print("Past due members:")
for row in results:
    print(f"{row[0]}: ${row[1]:.2f}, Base: ${row[2]:.2f}, Missed: {row[3]}, Late: ${row[4]:.2f}, Status: {row[5]}")

# Check total count
cursor.execute("SELECT COUNT(*) FROM members WHERE status_message LIKE '%Past Due%'")
count = cursor.fetchone()[0]
print(f"\nTotal past due members: {count}")

conn.close()
