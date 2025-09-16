#!/usr/bin/env python3
"""Check revenue calculation issues"""

import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("=== REVENUE CALCULATION ANALYSIS ===")

# Check if agreement_recurring_cost column exists
cursor.execute('PRAGMA table_info(members)')
columns = [row[1] for row in cursor.fetchall()]
print(f"agreement_recurring_cost column exists: {'agreement_recurring_cost' in columns}")

# Check how many members have agreement_recurring_cost populated
if 'agreement_recurring_cost' in columns:
    cursor.execute('SELECT COUNT(*) FROM members WHERE agreement_recurring_cost IS NOT NULL AND agreement_recurring_cost > 0')
    with_cost = cursor.fetchone()[0]
    print(f"Members with agreement_recurring_cost > 0: {with_cost}")
    
    # Sample values
    cursor.execute('SELECT first_name, last_name, agreement_recurring_cost FROM members WHERE agreement_recurring_cost IS NOT NULL AND agreement_recurring_cost > 0 LIMIT 5')
    sample_costs = cursor.fetchall()
    print(f"Sample agreement costs: {sample_costs}")
else:
    print("agreement_recurring_cost column does not exist!")

# Check members in good standing
cursor.execute('SELECT COUNT(*) FROM members WHERE status_message = "Member is in good standing"')
good_standing = cursor.fetchone()[0]
print(f"Members in good standing: {good_standing}")

# Check training clients and their revenue potential
print(f"\n=== TRAINING CLIENT REVENUE ANALYSIS ===")
cursor.execute('PRAGMA table_info(training_clients)')
training_columns = [row[1] for row in cursor.fetchall()]
print(f"Training client columns: {training_columns}")

cursor.execute('SELECT COUNT(*) FROM training_clients')
total_training_clients = cursor.fetchone()[0]
print(f"Total training clients: {total_training_clients}")

if 'past_due_amount' in training_columns:
    cursor.execute('SELECT COUNT(*) FROM training_clients WHERE past_due_amount > 0')
    past_due_clients = cursor.fetchone()[0]
    print(f"Training clients with past_due_amount > 0: {past_due_clients}")
    
    # Sample past due amounts (which are being incorrectly used as revenue)
    cursor.execute('SELECT member_name, past_due_amount FROM training_clients WHERE past_due_amount > 0 LIMIT 5')
    sample_past_due = cursor.fetchall()
    print(f"Sample past due amounts: {sample_past_due}")

conn.close()