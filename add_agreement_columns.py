#!/usr/bin/env python3
"""
Add missing agreement columns to PostgreSQL database
"""

import os
import psycopg2
import logging
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_database_url(database_url):
    """Parse DATABASE_URL for Cloud SQL connection"""
    try:
        parsed = urlparse(database_url)
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 5432,
            'dbname': parsed.path.lstrip('/') if parsed.path else 'gym_bot',
            'user': parsed.username or 'postgres',
            'password': parsed.password or ''
        }
    except Exception as e:
        logger.error(f"❌ Error parsing DATABASE_URL: {e}")
        raise

def add_agreement_columns():
    """Add agreement_id, agreement_guid, and agreement_type columns to members table"""
    
    # Get database configuration
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        # Parse connection details
        postgres_config = parse_database_url(database_url)
        logger.info(f"🔗 Connecting to PostgreSQL database...")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(**postgres_config)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'members' 
            AND column_name IN ('agreement_id', 'agreement_guid', 'agreement_type')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        columns_to_add = []
        if 'agreement_id' not in existing_columns:
            columns_to_add.append(('agreement_id', 'TEXT'))
        if 'agreement_guid' not in existing_columns:
            columns_to_add.append(('agreement_guid', 'TEXT'))
        if 'agreement_type' not in existing_columns:
            columns_to_add.append(('agreement_type', "TEXT DEFAULT 'Membership'"))
        
        if not columns_to_add:
            logger.info("✅ All agreement columns already exist in members table")
            return True
        
        # Add missing columns
        for column_name, column_def in columns_to_add:
            logger.info(f"🔧 Adding column: {column_name}")
            cursor.execute(f"ALTER TABLE members ADD COLUMN IF NOT EXISTS {column_name} {column_def}")
        
        # Commit changes
        conn.commit()
        
        # Verify columns were added
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'members' 
            AND column_name IN ('agreement_id', 'agreement_guid', 'agreement_type')
            ORDER BY column_name
        """)
        final_columns = [row[0] for row in cursor.fetchall()]
        
        logger.info(f"✅ Agreement columns now present: {final_columns}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to add agreement columns: {e}")
        return False

if __name__ == "__main__":
    success = add_agreement_columns()
    if success:
        logger.info("🎉 Agreement columns added successfully!")
    else:
        logger.error("❌ Failed to add agreement columns")
