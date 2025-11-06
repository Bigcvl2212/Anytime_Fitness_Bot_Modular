#!/usr/bin/env python3
"""
Add missing columns to members and prospects tables
"""
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_missing_columns():
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()

    # Add club_name to members table
    try:
        cursor.execute("ALTER TABLE members ADD COLUMN club_name TEXT")
        logger.info("✅ Added club_name column to members table")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            logger.info("ℹ️ club_name column already exists in members table")
        else:
            logger.error(f"❌ Error adding club_name to members: {e}")

    # Add source to prospects table
    try:
        cursor.execute("ALTER TABLE prospects ADD COLUMN source TEXT")
        logger.info("✅ Added source column to prospects table")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            logger.info("ℹ️ source column already exists in prospects table")
        else:
            logger.error(f"❌ Error adding source to prospects: {e}")

    conn.commit()
    conn.close()

    logger.info("✅ Database schema updated successfully")

if __name__ == '__main__':
    add_missing_columns()
