import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check if ANY members have addresses
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN address IS NOT NULL AND address != '' THEN 1 ELSE 0 END) as with_address,
        SUM(CASE WHEN zip_code IS NOT NULL AND zip_code != '' THEN 1 ELSE 0 END) as with_zip
    FROM members
""")

stats = cursor.fetchone()
print(f"\n=== MEMBER ADDRESS STATISTICS ===")
print(f"Total Members: {stats[0]}")
print(f"Members with Street Address: {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
print(f"Members with Zip Code: {stats[2]} ({stats[2]/stats[0]*100:.1f}%)")

# Show sample of green members
print(f"\n=== SAMPLE GREEN MEMBERS (showing address data) ===\n")
cursor.execute("""
    SELECT full_name, email, mobile_phone, address, city, state, zip_code
    FROM members 
    WHERE status_message NOT LIKE '%Past Due%'
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"Name:    {row[0]}")
    print(f"Email:   {row[1] or 'NO EMAIL'}")
    print(f"Phone:   {row[2] or 'NO PHONE'}")
    print(f"Address: {row[3] or 'NO ADDRESS'}")
    print(f"City:    {row[4] or 'NO CITY'}, State: {row[5] or 'NO STATE'}, Zip: {row[6] or 'NO ZIP'}")
    print("-" * 80)

conn.close()
