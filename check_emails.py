import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT prospect_id, full_name, email, mobile_phone, status_message 
    FROM members 
    WHERE status_message LIKE '%Past Due%' 
    LIMIT 10
""")

results = cursor.fetchall()

print("Past due members email data:")
print("=" * 80)
for row in results:
    prospect_id, full_name, email, mobile_phone, status_message = row
    print(f"ID: {prospect_id}")
    print(f"Name: {full_name}")
    print(f"Email: '{email}'")
    print(f"Phone: '{mobile_phone}'")
    print(f"Status: {status_message}")
    print("-" * 40)

conn.close()
