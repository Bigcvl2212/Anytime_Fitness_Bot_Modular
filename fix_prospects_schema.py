#!/usr/bin/env python3
"""
Fix prospects table schema - add mobile_phone column if missing
"""

import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_prospects_schema():
    """Add mobile_phone column to prospects table if it doesn't exist"""
    
    # Database path
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    logger.info(f"🔧 Fixing prospects table schema in: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if mobile_phone column exists
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        logger.info(f"📋 Current prospects columns: {columns}")
        
        if 'mobile_phone' not in columns:
            logger.info("➕ Adding mobile_phone column to prospects table...")
            cursor.execute("ALTER TABLE prospects ADD COLUMN mobile_phone TEXT")
            conn.commit()
            logger.info("✅ Successfully added mobile_phone column")
        else:
            logger.info("✅ mobile_phone column already exists")
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        logger.info(f"📋 Updated prospects columns: {columns}")
        
    except Exception as e:
        logger.error(f"❌ Error fixing schema: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fix_prospects_schema()
