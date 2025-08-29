#!/usr/bin/env python3
"""Clear the training clients table to start fresh"""

import sqlite3

def clear_training_clients():
    """Clear all training clients from the database"""
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Check current count
        cursor.execute("SELECT COUNT(*) FROM training_clients")
        current_count = cursor.fetchone()[0]
        print(f"Current training clients in database: {current_count}")
        
        if current_count > 0:
            # Clear the table
            cursor.execute("DELETE FROM training_clients")
            deleted_count = cursor.rowcount
            
            conn.commit()
            print(f"✅ Cleared {deleted_count} training clients from database")
            
            # Verify it's empty
            cursor.execute("SELECT COUNT(*) FROM training_clients")
            new_count = cursor.fetchone()[0]
            print(f"Training clients remaining: {new_count}")
        else:
            print("Database is already empty")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clear_training_clients()
