#!/usr/bin/env python3
"""
Script to analyze and fix the duplicate members in the database.
"""

import sqlite3
import os

def main():
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')
    print(f"Connecting to database at: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get schema
    cursor.execute("PRAGMA table_info(members)")
    columns = cursor.fetchall()
    print("Members table schema:")
    for col in columns:
        print(f"  {col[0]}: {col[1]} {col[2]} {'PRIMARY KEY' if col[5] > 0 else ''}")
    
    # Check if there's a unique constraint on prospect_id
    cursor.execute("PRAGMA index_list(members)")
    indexes = cursor.fetchall()
    print("\nIndexes on members table:")
    for idx in indexes:
        print(f"  {idx[1]} (unique: {idx[2]})")
        
        # Get the indexed columns
        cursor.execute(f"PRAGMA index_info({idx[1]})")
        idx_columns = cursor.fetchall()
        print(f"    Columns: {', '.join(str(col[2]) for col in idx_columns)}")
    
    # Count members
    cursor.execute("SELECT COUNT(*) FROM members")
    count = cursor.fetchone()[0]
    print(f"\nTotal members: {count}")
    
    # Count unique prospect_ids
    cursor.execute("SELECT COUNT(DISTINCT prospect_id) FROM members WHERE prospect_id IS NOT NULL")
    unique_count = cursor.fetchone()[0]
    print(f"Unique prospect_ids: {unique_count}")
    
    # Check for duplicates
    cursor.execute("""
        SELECT prospect_id, COUNT(*) as count 
        FROM members 
        WHERE prospect_id IS NOT NULL
        GROUP BY prospect_id 
        HAVING count > 1
        ORDER BY count DESC
        LIMIT 10
    """)
    duplicates = cursor.fetchall()
    if duplicates:
        print(f"\nSample of duplicate prospect_ids:")
        for dup in duplicates:
            print(f"  {dup[0]}: {dup[1]} occurrences")
    
    print("\n=== FIX PLAN ===")
    print("1. Create a temporary table with unique prospect_ids")
    print("2. Drop the existing members table")
    print("3. Create a new members table with unique constraint on prospect_id")
    print("4. Copy data from temporary table to new members table")
    
    # Execute the fix plan
    response = input("\nWould you like to fix the duplicate members? (yes/no): ")
    if response.lower() == "yes":
        print("\nFixing duplicate members...")
        
        # Create temporary table with unique records
        cursor.execute("""
            CREATE TABLE temp_members AS
            SELECT *
            FROM members
            WHERE id IN (
                SELECT MIN(id)
                FROM members
                GROUP BY prospect_id
            )
        """)
        
        # Drop existing table
        cursor.execute("DROP TABLE members")
        
        # Create new table with constraint
        cursor.execute("""
            CREATE TABLE members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guid TEXT,
                club_id TEXT,
                first_name TEXT,
                last_name TEXT,
                full_name TEXT,
                email TEXT,
                mobile_phone TEXT,
                home_phone TEXT,
                work_phone TEXT,
                address1 TEXT,
                address2 TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                country TEXT,
                date_of_birth TEXT,
                gender TEXT,
                membership_start TEXT,
                membership_end TEXT,
                last_visit TEXT,
                status TEXT,
                status_message TEXT,
                user_type TEXT,
                key_fob TEXT,
                photo_url TEXT,
                home_club_name TEXT,
                home_club_address TEXT,
                home_club_city TEXT,
                home_club_state TEXT,
                home_club_zip TEXT,
                home_club_af_number TEXT,
                agreement_id TEXT,
                agreement_guid TEXT,
                agreement_status TEXT,
                agreement_start_date TEXT,
                agreement_end_date TEXT,
                agreement_type TEXT,
                agreement_rate TEXT,
                payment_amount TEXT,
                amount_past_due REAL,
                amount_of_next_payment TEXT,
                date_of_next_payment TEXT,
                payment_token TEXT,
                card_type TEXT,
                card_last4 TEXT,
                expiration_month TEXT,
                expiration_year TEXT,
                billing_name TEXT,
                billing_address TEXT,
                billing_city TEXT,
                billing_state TEXT,
                billing_zip TEXT,
                account_type TEXT,
                routing_number TEXT,
                emergency_contact TEXT,
                emergency_phone TEXT,
                employer TEXT,
                occupation TEXT,
                has_app INTEGER,
                last_activity_timestamp TEXT,
                contract_types TEXT,
                bucket TEXT,
                color TEXT,
                rating TEXT,
                source TEXT,
                trial INTEGER,
                originated_from TEXT,
                female TEXT,
                contact_type TEXT,
                biller_message TEXT,
                created_at TEXT,
                updated_at TEXT,
                prospect_id TEXT UNIQUE,
                phone TEXT
            )
        """)
        
        # Copy data from temporary table
        cursor.execute("INSERT INTO members SELECT * FROM temp_members")
        
        # Drop temporary table
        cursor.execute("DROP TABLE temp_members")
        
        # Create index for prospect_id
        cursor.execute("CREATE UNIQUE INDEX idx_members_prospect_id ON members(prospect_id)")
        
        # Update the data_refresh_log
        cursor.execute("""
            UPDATE data_refresh_log 
            SET record_count = (SELECT COUNT(*) FROM members),
                last_refresh = CURRENT_TIMESTAMP
            WHERE table_name = 'members'
        """)
        
        # Commit the changes
        conn.commit()
        
        # Check the result
        cursor.execute("SELECT COUNT(*) FROM members")
        new_count = cursor.fetchone()[0]
        print(f"Fixed! New member count: {new_count}")
    else:
        print("Fix cancelled.")
    
    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()
