#!/usr/bin/env python3

"""
Add agreement_id, agreement_guid, and agreement_type columns to members table in PostgreSQL
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.database_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)

def add_agreement_columns_postgresql():
    """Add agreement columns to members table in PostgreSQL"""
    
    print("🔧 Adding Agreement Columns to PostgreSQL Members Table")
    print("=" * 60)
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        cursor = db_manager.get_cursor(conn)
        
        print("✅ Connected to PostgreSQL database")
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'members' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"Current columns: {existing_columns}")
        
        # Add agreement_id column if it doesn't exist
        if 'agreement_id' not in existing_columns:
            print("Adding agreement_id column...")
            cursor.execute("ALTER TABLE members ADD COLUMN agreement_id TEXT")
            print("✅ agreement_id column added")
        else:
            print("✅ agreement_id column already exists")
        
        # Add agreement_guid column if it doesn't exist
        if 'agreement_guid' not in existing_columns:
            print("Adding agreement_guid column...")
            cursor.execute("ALTER TABLE members ADD COLUMN agreement_guid TEXT")
            print("✅ agreement_guid column added")
        else:
            print("✅ agreement_guid column already exists")
        
        # Add agreement_type column if it doesn't exist
        if 'agreement_type' not in existing_columns:
            print("Adding agreement_type column...")
            cursor.execute("ALTER TABLE members ADD COLUMN agreement_type TEXT")
            print("✅ agreement_type column added")
        else:
            print("✅ agreement_type column already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the new structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'members' 
            AND table_schema = 'public'
            AND column_name IN ('agreement_id', 'agreement_guid', 'agreement_type')
            ORDER BY column_name
        """)
        
        new_columns = cursor.fetchall()
        print(f"\nNew agreement columns:")
        for col_name, col_type in new_columns:
            print(f"   {col_name}: {col_type}")
        
        # Test the columns work
        cursor.execute("""
            SELECT COUNT(*) 
            FROM members 
            WHERE agreement_id IS NOT NULL
        """)
        
        count_with_agreement_id = cursor.fetchone()[0]
        print(f"\n📊 Members with agreement_id: {count_with_agreement_id}")
        
        conn.close()
        print("\n✅ PostgreSQL database schema updated successfully!")
        print("🎯 Ready to sync agreement data from ClubHub API")
        
    except Exception as e:
        print(f"❌ Error updating PostgreSQL database schema: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    add_agreement_columns_postgresql()