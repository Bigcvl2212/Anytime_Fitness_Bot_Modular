#!/usr/bin/env python3

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

def check_campaigns_table():
    """Check the structure of the campaigns table"""
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Check if campaigns table exists and show its structure
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="campaigns"')
        table_exists = cursor.fetchone()
        
        if table_exists:
            cursor.execute('PRAGMA table_info(campaigns)')
            columns = cursor.fetchall()
            print('✅ Current campaigns table structure:')
            for col in columns:
                print(f'  Column: {col[1]} | Type: {col[2]} | Not Null: {col[3]} | Default: {col[4]}')
        else:
            print('❌ campaigns table does not exist')
            
        # Also check what tables do exist
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        print('\n📋 All tables in database:')
        for table in tables:
            print(f'  - {table[0]}')
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking table: {e}")

if __name__ == "__main__":
    check_campaigns_table()