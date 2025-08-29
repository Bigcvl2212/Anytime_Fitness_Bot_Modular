#!/usr/bin/env python3
"""
Quick database check for past due members without Flask startup
"""

import sqlite3
import os

# Direct database access
db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=== DATABASE PAST DUE ANALYSIS ===')

# Check if we have any past due patterns
cursor.execute("SELECT status_message, COUNT(*) FROM members WHERE status_message LIKE 'Past Due%' GROUP BY status_message")
past_due_results = cursor.fetchall()

if past_due_results:
    print('Past Due patterns found:')
    total_past_due = 0
    for row in past_due_results:
        print(f'  "{row[0]}": {row[1]} members')
        total_past_due += row[1]
    print(f'Total Past Due: {total_past_due}')
    
    # Show sample members
    print('\n=== SAMPLE PAST DUE MEMBERS ===')
    cursor.execute("SELECT first_name, last_name, status_message FROM members WHERE status_message LIKE 'Past Due%' LIMIT 5")
    sample_members = cursor.fetchall()
    for member in sample_members:
        print(f'  {member[0]} {member[1]}: "{member[2]}"')
else:
    print('❌ NO Past Due members found with "Past Due%" pattern')

print('\n=== TOP STATUS_MESSAGE PATTERNS ===')
cursor.execute("SELECT DISTINCT status_message, COUNT(*) FROM members WHERE status_message IS NOT NULL GROUP BY status_message ORDER BY COUNT(*) DESC")
all_statuses = cursor.fetchall()
for status, count in all_statuses[:15]:  # Top 15 patterns
    print(f'  "{status}": {count}')

print('\n=== CHECKING SPECIFIC PAST DUE VARIATIONS ===')
# Check for various past due patterns
past_due_variations = [
    "Past Due%",
    "%past due%", 
    "%overdue%",
    "%delinquent%",
    "%behind%"
]

for pattern in past_due_variations:
    cursor.execute(f"SELECT COUNT(*) FROM members WHERE LOWER(status_message) LIKE LOWER(?)", (pattern,))
    count = cursor.fetchone()[0]
    if count > 0:
        print(f'  Pattern "{pattern}": {count} members')

conn.close()
