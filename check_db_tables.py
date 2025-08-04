import sqlite3
import os

def check_db_tables(db_path):
    """Check tables in a SQLite database"""
    try:
        print(f"Checking database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print(f"  Columns: {', '.join(col[1] for col in columns)}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  Row count: {count}")
            print()
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check each database
    dbs = ["data/members.db", "data/gym_bot.db", "gym_bot.db"]
    
    for db in dbs:
        if os.path.exists(db):
            check_db_tables(db)
            print("-" * 50)
        else:
            print(f"Database not found: {db}")
