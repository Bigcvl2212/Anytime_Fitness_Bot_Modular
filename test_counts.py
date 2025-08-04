#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print('=== MEMBER COUNTS ===')
cursor.execute('SELECT COUNT(*) FROM members')
total = cursor.fetchone()[0]
print(f'Total members: {total}')

cursor.execute('SELECT COUNT(*) FROM members WHERE amount_past_due > 0')
red = cursor.fetchone()[0]
print(f'Red (actually past due): {red}')

cursor.execute("SELECT COUNT(*) FROM members WHERE date_of_next_payment <= date('now', '+7 days') AND (amount_past_due IS NULL OR amount_past_due = 0)")
yellow = cursor.fetchone()[0]
print(f'Yellow (due within 7 days): {yellow}')

cursor.execute("SELECT COUNT(*) FROM members WHERE (amount_past_due IS NULL OR amount_past_due <= 0) AND (date_of_next_payment IS NULL OR date_of_next_payment > date('now', '+7 days'))")
current = cursor.fetchone()[0]
print(f'Current/Active members: {current}')

print(f'Total check: {red + yellow + current} should equal {total}')

# Show some examples
print('\n=== RED EXAMPLES ===')
cursor.execute('SELECT full_name, amount_past_due FROM members WHERE amount_past_due > 0 LIMIT 3')
for row in cursor.fetchall():
    print(f'- {row[0]}: ${row[1]}')

print('\n=== YELLOW EXAMPLES ===')
cursor.execute("SELECT full_name, date_of_next_payment, amount_past_due FROM members WHERE date_of_next_payment <= date('now', '+7 days') AND (amount_past_due IS NULL OR amount_past_due = 0) LIMIT 3")
for row in cursor.fetchall():
    print(f'- {row[0]}: Next payment {row[1]}, Past due: ${row[2] or 0}')

conn.close()
