#!/usr/bin/env python3
"""Check what data exists in the training_clients table"""

import sqlite3

def check_training_clients_data():
    """Check the current data in the training_clients table"""
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Check total count
        cursor.execute("SELECT COUNT(*) FROM training_clients")
        total_count = cursor.fetchone()[0]
        print(f"Total training clients in database: {total_count}")
        
        if total_count > 0:
            # Get sample data
            cursor.execute("SELECT * FROM training_clients LIMIT 3")
            samples = cursor.fetchall()
            
            print("\nSample training clients:")
            print("=" * 50)
            for i, sample in enumerate(samples):
                print(f"Client {i+1}:")
                print(f"  ID: {sample[0]}")
                print(f"  Member Name: {sample[4]}")
                print(f"  ClubOS Member ID: {sample[3]}")
                print(f"  Email: {sample[5]}")
                print(f"  Payment Status: {sample[21]}")
                print()
        else:
            print("No training clients found in database")
        
        # Check if there are any training clients in the cache
        print("Checking if training clients exist in cache...")
        print("(This would require the dashboard to be running)")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_training_clients_data()
