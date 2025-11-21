#!/usr/bin/env python3
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from src.services.database_manager import DatabaseManager

# Initialize database
db_mgr = DatabaseManager('src/gym_bot.db')
result = db_mgr.init_database()
print('Database initialization result:', result)

# Verify tables were created
import sqlite3
conn = sqlite3.connect('src/gym_bot.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print("Tables created:")
for table in tables:
    print(f"  - {table[0]}")

# Check member_categories table specifically
cursor.execute('PRAGMA table_info(member_categories)')
columns = cursor.fetchall()
if columns:
    print("\nmember_categories columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")  # column name and type
else:
    print("\nmember_categories table not found")

conn.close()
