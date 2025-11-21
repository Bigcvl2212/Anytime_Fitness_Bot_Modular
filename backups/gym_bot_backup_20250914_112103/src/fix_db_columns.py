#!/usr/bin/env python3
import sqlite3
import os

def add_training_clients_columns():
    """Add missing columns to training_clients table in the correct database"""
    db_path = 'gym_bot.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List of columns to add
        columns = [
            "clubos_member_id TEXT",
            "first_name TEXT", 
            "last_name TEXT",
            "full_name TEXT",
            "member_name TEXT",
            "email TEXT",
            "phone TEXT",
            "trainer_name TEXT DEFAULT 'Jeremy Mayo'",
            "source TEXT DEFAULT 'clubos_assignees_with_agreements'",
            "active_packages TEXT DEFAULT '[]'",
            "package_summary TEXT DEFAULT ''",
            "package_details TEXT DEFAULT '[]'",
            "past_due_amount REAL DEFAULT 0.0",
            "total_past_due REAL DEFAULT 0.0",
            "payment_status TEXT DEFAULT 'Current'",
            "sessions_remaining INTEGER DEFAULT 0",
            "last_session TEXT DEFAULT 'See ClubOS'",
            "financial_summary TEXT DEFAULT 'Current'",
            "last_updated TEXT DEFAULT ''"
        ]
        
        for column in columns:
            try:
                cursor.execute(f"ALTER TABLE training_clients ADD COLUMN {column}")
                print(f"✅ Added column: {column}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"⚠️ Column already exists: {column}")
                else:
                    print(f"❌ Error adding column {column}: {e}")
        
        conn.commit()
        print(f"✅ Database updated successfully: {os.path.abspath(db_path)}")
        
        # Verify columns exist
        cursor.execute("PRAGMA table_info(training_clients)")
        columns_info = cursor.fetchall()
        print(f"\n📋 Current training_clients columns: {len(columns_info)} total")
        for col in columns_info:
            print(f"   - {col[1]} ({col[2]})")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")

if __name__ == "__main__":
    add_training_clients_columns()
