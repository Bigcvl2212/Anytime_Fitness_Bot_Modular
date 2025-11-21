#!/usr/bin/env python3
"""
Fix ALL database schema issues - October 3, 2025
"""

import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_all_schemas():
    """Fix all missing columns in database tables"""
    
    # Database path
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    logger.info(f"🔧 Fixing ALL database schemas in: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    fixes_applied = []
    
    try:
        # Fix 1: Add mobile_phone to prospects if missing
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'mobile_phone' not in columns:
            logger.info("➕ Adding mobile_phone column to prospects table...")
            cursor.execute("ALTER TABLE prospects ADD COLUMN mobile_phone TEXT")
            conn.commit()
            fixes_applied.append("prospects.mobile_phone")
            logger.info("✅ Added mobile_phone column")
        else:
            logger.info("✅ prospects.mobile_phone already exists")
        
        # Fix 2: Add source to prospects if missing
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'source' not in columns:
            logger.info("➕ Adding source column to prospects table...")
            cursor.execute("ALTER TABLE prospects ADD COLUMN source TEXT")
            conn.commit()
            fixes_applied.append("prospects.source")
            logger.info("✅ Added source column")
        else:
            logger.info("✅ prospects.source already exists")
        
        # Fix 3: Add interest_level to prospects if missing
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'interest_level' not in columns:
            logger.info("➕ Adding interest_level column to prospects table...")
            cursor.execute("ALTER TABLE prospects ADD COLUMN interest_level TEXT")
            conn.commit()
            fixes_applied.append("prospects.interest_level")
            logger.info("✅ Added interest_level column")
        else:
            logger.info("✅ prospects.interest_level already exists")
        
        # Fix 4: Add club_name to prospects if missing
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'club_name' not in columns:
            logger.info("➕ Adding club_name column to prospects table...")
            cursor.execute("ALTER TABLE prospects ADD COLUMN club_name TEXT")
            conn.commit()
            fixes_applied.append("prospects.club_name")
            logger.info("✅ Added club_name column")
        else:
            logger.info("✅ prospects.club_name already exists")
        
        # Fix 5: Add created_date to prospects if missing
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'created_date' not in columns:
            logger.info("➕ Adding created_date column to prospects table...")
            cursor.execute("ALTER TABLE prospects ADD COLUMN created_date TEXT")
            conn.commit()
            fixes_applied.append("prospects.created_date")
            logger.info("✅ Added created_date column")
        else:
            logger.info("✅ prospects.created_date already exists")
        
        # Fix 6: Add last_contact_date to prospects if missing
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'last_contact_date' not in columns:
            logger.info("➕ Adding last_contact_date column to prospects table...")
            cursor.execute("ALTER TABLE prospects ADD COLUMN last_contact_date TEXT")
            conn.commit()
            fixes_applied.append("prospects.last_contact_date")
            logger.info("✅ Added last_contact_date column")
        else:
            logger.info("✅ prospects.last_contact_date already exists")
        
        # Fix 7: Add notes to prospects if missing
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'notes' not in columns:
            logger.info("➕ Adding notes column to prospects table...")
            cursor.execute("ALTER TABLE prospects ADD COLUMN notes TEXT")
            conn.commit()
            fixes_applied.append("prospects.notes")
            logger.info("✅ Added notes column")
        else:
            logger.info("✅ prospects.notes already exists")
        
        # Verify final schema
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        logger.info(f"\n📋 Final prospects columns: {columns}")
        
        if fixes_applied:
            logger.info(f"\n✅ Applied {len(fixes_applied)} fixes:")
            for fix in fixes_applied:
                logger.info(f"   • {fix}")
        else:
            logger.info("\n✅ No fixes needed - all columns already exist")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing schemas: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_all_schemas()
    exit(0 if success else 1)
