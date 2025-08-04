import sqlite3
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_member_names():
    """Update all member records to have proper full_name values"""
    # Use the main database file (from line 425 in clean_dashboard.py)
    db_path = 'gym_bot.db'
    
    if not os.path.exists(db_path):
        logger.error(f"Database not found: {db_path}")
        return
    
    logger.info(f"Opening database at: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if there's a members table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='members'")
    if not cursor.fetchone():
        logger.error("No 'members' table found in the database")
        return
    
    # Get column info
    cursor.execute("PRAGMA table_info(members)")
    columns = [col[1] for col in cursor.fetchall()]
    logger.info(f"Columns in members table: {columns}")
    
    # Check for necessary columns
    if 'first_name' not in columns or 'last_name' not in columns:
        logger.error("Required columns 'first_name' and/or 'last_name' not found in members table")
        return
    
    # Count total members
    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]
    logger.info(f"Total members in database: {total_members}")
    
    # Update all members to have a proper full_name
    cursor.execute("""
        UPDATE members 
        SET full_name = TRIM(COALESCE(first_name, '') || ' ' || COALESCE(last_name, ''))
        WHERE first_name IS NOT NULL OR last_name IS NOT NULL
    """)
    
    fixed_count = cursor.rowcount
    logger.info(f"Updated {fixed_count} member records with proper full_name from first_name and last_name")
        
    # Commit changes
    conn.commit()
    
    # Verify the results
    cursor.execute("SELECT COUNT(*) FROM members WHERE full_name IS NULL OR full_name = '' OR full_name = ' '")
    still_missing = cursor.fetchone()[0]
    logger.info(f"Members still missing full_name: {still_missing}")
    
    # Close connection
    conn.close()
    
    logger.info("✅ Member names update completed")

if __name__ == "__main__":
    fix_member_names()
