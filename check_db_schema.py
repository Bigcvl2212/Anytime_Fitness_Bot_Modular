import sqlite3

# Check database schema
conn = sqlite3.connect('data/gym_data.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])

# Check members table schema if it exists
try:
    cursor.execute("PRAGMA table_info(members)")
    members_cols = cursor.fetchall()
    print("Members columns:", [col[1] for col in members_cols])
except:
    print("Members table doesn't exist or is empty")

# Check training_clients table schema if it exists
try:
    cursor.execute("PRAGMA table_info(training_clients)")
    training_cols = cursor.fetchall()
    print("Training_clients columns:", [col[1] for col in training_cols])
except:
    print("Training_clients table doesn't exist or is empty")

# Check current counts
try:
    cursor.execute("SELECT COUNT(*) FROM members")
    members_count = cursor.fetchone()[0]
    print(f"Members count: {members_count}")
except:
    print("Can't count members")

try:
    cursor.execute("SELECT COUNT(*) FROM training_clients")
    training_count = cursor.fetchone()[0]
    print(f"Training clients count: {training_count}")
except:
    print("Can't count training clients")

conn.close()
