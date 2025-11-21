#!/usr/bin/env python3
"""
Sync Cache to Database
Force sync members from cache to database for proper categorization
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main_app import app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_cache_to_db():
    """Sync cached members to database"""
    with app.app_context():
        try:
            # Get cached members
            cached_members = app.data_cache.get('members', [])
            if not cached_members:
                logger.warning("⚠️ No cached members found")
                return
            
            logger.info(f"📊 Found {len(cached_members)} cached members, syncing to DB...")
            
            # Save to database
            success = app.db_manager.save_members_to_db(cached_members)
            
            if success:
                logger.info("✅ Successfully synced members from cache to database")
                
                # Check counts
                db_count = app.db_manager.get_member_count()
                logger.info(f"📊 Database now has {db_count} members")
                
                # Check category counts
                category_counts = app.db_manager.get_category_counts()
                logger.info(f"📊 Category counts: {category_counts}")
                
            else:
                logger.error("❌ Failed to sync members to database")
                
        except Exception as e:
            logger.error(f"❌ Error syncing cache to DB: {e}")

if __name__ == '__main__':
    sync_cache_to_db()
