#!/usr/bin/env python3
"""
Fix member_categories table schema to match database_manager.py expectations
"""

import sys
import os
sys.path.append('src')

# Set up environment
from src.config.environment_setup import load_environment_variables
load_environment_variables()

from src.services.database_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_member_categories_schema():
    """Fix member_categories table schema"""
    try:
        # Use DatabaseManager to get connection
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'member_categories'
            ORDER BY ordinal_position
        """)
        current_columns = cursor.fetchall()
        logger.info(f"Current member_categories columns: {current_columns}")
        
        # Add missing columns
        columns_to_add = [
            ("full_name", "TEXT"),
            ("classified_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE member_categories ADD COLUMN {column_name} {column_type};")
                logger.info(f"✅ Added column: {column_name} {column_type}")
            except Exception as e:
                if 'already exists' in str(e):
                    logger.info(f"✅ Column {column_name} already exists")
                else:
                    logger.error(f"❌ Error adding column {column_name}: {e}")
                    conn.rollback()
                    continue
        
        # Commit changes
        conn.commit()
        
        # Verify final schema
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'member_categories'
            ORDER BY ordinal_position
        """)
        final_columns = cursor.fetchall()
        logger.info(f"Final member_categories schema:")
        for col in final_columns:
            logger.info(f"  {col[0]} - {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        cursor.close()
        conn.close()
        
        logger.info("✅ member_categories schema fix completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing schema: {e}")
        return False

if __name__ == "__main__":
    success = fix_member_categories_schema()
    sys.exit(0 if success else 1)