#!/usr/bin/env python3
"""
Show all green members missing agreement_recurring_cost field
"""
import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("🔍 Green members missing agreement_recurring_cost field:")
print("="*80)

cursor.execute("""
    SELECT first_name, last_name, prospect_id, email, mobile_phone, 
           amount_past_due, date_of_next_payment, agreement_recurring_cost
    FROM members 
    WHERE status_message = 'Member is in good standing' 
    AND (agreement_recurring_cost IS NULL OR agreement_recurring_cost = 0)
    ORDER BY last_name, first_name
""")

missing_members = cursor.fetchall()

for i, member in enumerate(missing_members, 1):
    first_name, last_name, prospect_id, email, mobile_phone, past_due, next_payment, recurring_cost = member
    print(f"{i:2d}. {first_name} {last_name}")
    print(f"    Prospect ID: {prospect_id}")
    print(f"    Email: {email or 'Not provided'}")
    print(f"    Phone: {mobile_phone or 'Not provided'}")
    print(f"    Past Due: ${past_due or 0:.2f}")
    print(f"    Next Payment: {next_payment or 'Not set'}")
    print(f"    Recurring Cost: {recurring_cost or 'NULL'}")
    print()

print(f"📊 Total missing: {len(missing_members)} out of 312 green members")

# Also show a few examples of members WITH recurring cost for comparison
print("\n" + "="*80)
print("✅ Examples of green members WITH agreement_recurring_cost:")
print("="*80)

cursor.execute("""
    SELECT first_name, last_name, prospect_id, agreement_recurring_cost
    FROM members 
    WHERE status_message = 'Member is in good standing' 
    AND COALESCE(agreement_recurring_cost, 0) > 0
    ORDER BY agreement_recurring_cost DESC
    LIMIT 5
""")

working_members = cursor.fetchall()

for i, member in enumerate(working_members, 1):
    first_name, last_name, prospect_id, recurring_cost = member
    print(f"{i}. {first_name} {last_name} (ID: {prospect_id}) - ${recurring_cost:.2f}/month")

conn.close()