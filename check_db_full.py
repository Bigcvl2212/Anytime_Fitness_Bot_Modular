#!/usr/bin/env python3
"""
Script to thoroughly check database contents and identify issues.
"""

import sqlite3
import os
import sys
import json
from datetime import datetime

def main():
    # Connect to the database
    db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')
    print(f"Connecting to database at: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables in database: {', '.join(tables)}")
    
    # Check each table
    for table in tables:
        print(f"\n{'='*50}")
        print(f"TABLE: {table}")
        print(f"{'='*50}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Row count: {count}")
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"Columns: {', '.join(col[1] for col in columns)}")
        
        # Check for duplicate key values if there's an ID column
        id_columns = [col[1] for col in columns if col[1].endswith('_id') or col[1] == 'id']
        for id_col in id_columns:
            cursor.execute(f"""
                SELECT {id_col}, COUNT(*) as count 
                FROM {table} 
                GROUP BY {id_col} 
                HAVING count > 1
            """)
            duplicates = cursor.fetchall()
            if duplicates:
                print(f"WARNING: Found {len(duplicates)} duplicate values for {id_col}")
                for dup in duplicates[:5]:  # Show first 5
                    print(f"  {id_col}={dup[0]} appears {dup[1]} times")
                if len(duplicates) > 5:
                    print(f"  ...and {len(duplicates)-5} more duplicates")
            else:
                print(f"No duplicates found for {id_col}")
        
        # Sample data
        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
        sample_rows = cursor.fetchall()
        print("\nSample data:")
        for row in sample_rows:
            row_dict = {key: row[key] for key in row.keys()}
            print(json.dumps(row_dict, indent=2, default=str))
    
    # Close connection
    conn.close()
    print("\nDatabase check complete.")

if __name__ == "__main__":
    main()
