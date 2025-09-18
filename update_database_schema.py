"""
Update Database Schema - Add Campaign Tables
This script will create the campaign tables in the existing database
"""

import sys
import os
import logging

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.services.database_manager import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_database_schema():
    """Add campaign tables to existing database"""
    try:
        logger.info("🔄 Updating database schema with campaign tables...")
        
        # Force SQLite usage by setting environment variable
        os.environ['DB_TYPE'] = 'sqlite'
        
        # Initialize database manager
        db_path = os.path.join(project_root, 'gym_bot.db')
        db_manager = DatabaseManager(db_path=db_path)
        
        # Check if campaigns table already exists
        check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='campaigns'"
        result = db_manager.execute_query(check_query, fetch_one=True)
        
        if result:
            logger.info("✅ Campaigns table already exists")
            return True
        
        logger.info("📝 Creating campaign tables...")
        
        # Create campaign tables
        campaign_tables = {
            'campaigns': '''
                CREATE TABLE campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    name TEXT NOT NULL,
                    message TEXT NOT NULL,
                    message_type TEXT DEFAULT 'sms',
                    email_subject TEXT,
                    max_recipients INTEGER DEFAULT 100,
                    notes TEXT,
                    status TEXT DEFAULT 'draft',
                    total_recipients INTEGER DEFAULT 0,
                    sent_count INTEGER DEFAULT 0,
                    delivered_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    current_position INTEGER DEFAULT 0,
                    progress_data TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    paused_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'campaign_templates': '''
                CREATE TABLE campaign_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT,
                    message TEXT NOT NULL,
                    target_group TEXT,
                    max_recipients INTEGER DEFAULT 100,
                    usage_count INTEGER DEFAULT 0,
                    last_used TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'campaign_recipients': '''
                CREATE TABLE campaign_recipients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER NOT NULL,
                    member_id TEXT NOT NULL,
                    member_name TEXT,
                    member_email TEXT,
                    member_phone TEXT,
                    status TEXT DEFAULT 'pending',
                    sent_at TIMESTAMP,
                    delivered_at TIMESTAMP,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
                )
            '''
        }
        
        # Execute table creation queries
        for table_name, create_query in campaign_tables.items():
            try:
                db_manager.execute_query(create_query)
                logger.info(f"✅ Created {table_name} table")
            except Exception as e:
                logger.error(f"❌ Error creating {table_name} table: {e}")
                return False
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX idx_campaigns_category ON campaigns(category)",
            "CREATE INDEX idx_campaigns_status ON campaigns(status)",
            "CREATE INDEX idx_campaign_recipients_campaign_id ON campaign_recipients(campaign_id)",
            "CREATE INDEX idx_campaign_recipients_member_id ON campaign_recipients(member_id)",
            "CREATE INDEX idx_campaign_recipients_status ON campaign_recipients(status)"
        ]
        
        for index_query in indexes:
            try:
                db_manager.execute_query(index_query)
                logger.info(f"✅ Created index: {index_query.split()[2]}")
            except Exception as e:
                logger.warning(f"⚠️ Could not create index: {e}")
        
        logger.info("✅ Database schema updated with campaign tables!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating database schema: {e}")
        return False

if __name__ == "__main__":
    success = update_database_schema()
    if success:
        print("✅ Database schema updated successfully!")
    else:
        print("❌ Failed to update database schema!")
        sys.exit(1)