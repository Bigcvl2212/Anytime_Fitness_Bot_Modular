#!/usr/bin/env python3
"""
Quick script to check member revenue field population
"""
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

# Check members with green status vs those with agreement_recurring_cost
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Count all green members
cursor.execute("SELECT COUNT(*) FROM members WHERE status_message = 'Member is in good standing'")
total_green = cursor.fetchone()[0]

# Count green members with agreement_recurring_cost > 0
cursor.execute("SELECT COUNT(*) FROM members WHERE status_message = 'Member is in good standing' AND COALESCE(agreement_recurring_cost, 0) > 0")
green_with_cost = cursor.fetchone()[0]

# Count green members with NULL or 0 agreement_recurring_cost  
cursor.execute("SELECT COUNT(*) FROM members WHERE status_message = 'Member is in good standing' AND (agreement_recurring_cost IS NULL OR agreement_recurring_cost = 0)")
green_without_cost = cursor.fetchone()[0]

print(f'Total green members: {total_green}')
print(f'Green members with recurring cost > 0: {green_with_cost}')  
print(f'Green members missing recurring cost: {green_without_cost}')

# Sample a few members without recurring cost
cursor.execute("SELECT first_name, last_name, prospect_id, agreement_recurring_cost FROM members WHERE status_message = 'Member is in good standing' AND (agreement_recurring_cost IS NULL OR agreement_recurring_cost = 0) LIMIT 5")
missing_cost_samples = cursor.fetchall()
print(f'\nSample members missing recurring cost:')
for member in missing_cost_samples:
    print(f'  {member[0]} {member[1]} (ID: {member[2]}) - recurring_cost: {member[3]}')

# Check if agreement_recurring_cost field exists
cursor.execute("PRAGMA table_info(members)")
columns = [row[1] for row in cursor.fetchall()]
if 'agreement_recurring_cost' not in columns:
    print(f'\n❌ ERROR: agreement_recurring_cost field does not exist in members table!')
    print(f'Available columns: {", ".join(columns)}')
else:
    print(f'\n✅ agreement_recurring_cost field exists in members table')

conn.close()