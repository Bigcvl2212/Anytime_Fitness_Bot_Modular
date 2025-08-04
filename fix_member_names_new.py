import sqlite3
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_member_names():
    """Update all member records to have proper full_name values"""
    # Use the main database file
    db_path = 'gym_bot.db'
    
    if not os.path.exists(db_path):
        logger.error(f"Database not found: {db_path}")
        return
    
    logger.info(f"Opening database at: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all members
        cursor.execute("SELECT COUNT(*) FROM members")
        total_members = cursor.fetchone()[0]
        logger.info(f"Found {total_members} members in database")
        
        # Update members with missing full_name
        cursor.execute("""
            UPDATE members 
            SET full_name = TRIM(IFNULL(first_name, '') || ' ' || IFNULL(last_name, ''))
            WHERE (full_name IS NULL OR full_name = '' OR full_name = ' ')
            AND (first_name IS NOT NULL OR last_name IS NOT NULL)
        """)
        
        updated_count = cursor.rowcount
        logger.info(f"Updated {updated_count} members with first_name/last_name")
        
        # For remaining members with no full_name, try to derive from email
        cursor.execute("""
            UPDATE members
            SET full_name = SUBSTR(email, 1, INSTR(email || '@', '@') - 1)
            WHERE (full_name IS NULL OR full_name = '' OR full_name = ' ')
            AND email IS NOT NULL
            AND INSTR(email, '@') > 1
        """)
        
        email_count = cursor.rowcount
        logger.info(f"Updated {email_count} members with names derived from email")
        
        # Commit changes
        conn.commit()
        
        # Log results
        cursor.execute("SELECT COUNT(*) FROM members WHERE full_name IS NULL OR full_name = '' OR full_name = ' '")
        remaining_empty = cursor.fetchone()[0]
        logger.info(f"Remaining members with empty full_name: {remaining_empty}")
        
        # Close connection
        conn.close()
        
        logger.info(f"Fix complete! Updated {updated_count + email_count} member records")
        return updated_count + email_count
        
    except Exception as e:
        logger.error(f"Error fixing member names: {str(e)}")
        return 0

if __name__ == "__main__":
    fixed = fix_member_names()
    print(f"✅ Fixed {fixed} member names!")
