import sqlite3

# Connect to database
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Search for Grace by email
cursor.execute("SELECT id, full_name, email FROM members WHERE email LIKE '%grace%' OR email LIKE '%sphatt%'")
results = cursor.fetchall()
print(f"Grace search results: {results}")

# If no exact match, search for similar names in email
cursor.execute("SELECT id, full_name, email FROM members WHERE email LIKE '%g%' AND email LIKE '%s%'")
broader_results = cursor.fetchall()
print(f"Broader search (emails with 'g' and 's'): {broader_results}")

# Show first 20 emails to see the pattern
cursor.execute("SELECT id, email FROM members LIMIT 20")
sample_emails = cursor.fetchall()
print(f"Sample emails: {sample_emails}")

conn.close()
