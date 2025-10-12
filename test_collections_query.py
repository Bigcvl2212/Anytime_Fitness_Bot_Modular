import sqlite3

# Test the collections query
conn = sqlite3.connect(r'C:\Users\mayoj\AppData\Local\GymBot\data\gym_bot.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Test query for past due members
print("=" * 80)
print("PAST DUE MEMBERS WITH ADDRESSES")
print("=" * 80)

cursor.execute("""
    SELECT
        full_name as name,
        first_name,
        last_name,
        email,
        COALESCE(mobile_phone, phone) as phone,
        phone as home_phone,
        address,
        city,
        state,
        zip_code,
        amount_past_due as past_due_amount,
        status
    FROM members
    WHERE amount_past_due > 0
    ORDER BY amount_past_due DESC
    LIMIT 5
""")

members = cursor.fetchall()
print(f"\nFound {len(members)} past due members")
for i, member in enumerate(members, 1):
    print(f"\n{i}. {member['name']}")
    print(f"   Email: {member['email']}")
    print(f"   Phone: {member['phone']}")
    print(f"   Address: {member['address']}")
    print(f"   City/State/Zip: {member['city']}, {member['state']} {member['zip_code']}")
    print(f"   Past Due: ${member['past_due_amount']}")

# Test query for training clients
print("\n" + "=" * 80)
print("PAST DUE TRAINING CLIENTS WITH ADDRESSES (FROM JOIN)")
print("=" * 80)

cursor.execute("""
    SELECT
        tc.member_name as name,
        COALESCE(m.first_name, tc.first_name) as first_name,
        COALESCE(m.last_name, tc.last_name) as last_name,
        COALESCE(m.email, tc.email) as email,
        COALESCE(m.mobile_phone, m.phone, tc.phone, tc.mobile_phone) as phone,
        m.phone as home_phone,
        COALESCE(m.address, tc.address) as address,
        COALESCE(m.city, tc.city) as city,
        COALESCE(m.state, tc.state) as state,
        COALESCE(m.zip_code, tc.zip_code) as zip_code,
        tc.total_past_due as past_due_amount,
        tc.payment_status as status,
        'training_client' as type
    FROM training_clients tc
    LEFT JOIN members m ON (
        LOWER(TRIM(tc.member_name)) = LOWER(TRIM(m.full_name))
        OR LOWER(TRIM(tc.member_name)) = LOWER(TRIM(m.first_name || ' ' || m.last_name))
    )
    WHERE tc.total_past_due > 0 OR tc.past_due_amount > 0
    ORDER BY COALESCE(tc.total_past_due, tc.past_due_amount) DESC
    LIMIT 5
""")

training_clients = cursor.fetchall()
print(f"\nFound {len(training_clients)} past due training clients")
for i, client in enumerate(training_clients, 1):
    print(f"\n{i}. {client['name']}")
    print(f"   Email: {client['email']}")
    print(f"   Phone: {client['phone']}")
    print(f"   Address: {client['address']}")
    print(f"   City/State/Zip: {client['city']}, {client['state']} {client['zip_code']}")
    print(f"   Past Due: ${client['past_due_amount']}")

conn.close()
