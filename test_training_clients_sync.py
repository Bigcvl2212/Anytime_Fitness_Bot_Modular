#!/usr/bin/env python3
"""
Test script to verify training clients sync database compatibility
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import modules
from src.services.database_manager import DatabaseManager
from src.utils.logger_config import setup_logger

logger = setup_logger(__name__)

def test_training_clients_sync():
    """Test training clients sync with sample data"""
    logger.info("🧪 Testing training clients database sync...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    logger.info(f"Database type: {db_manager.db_type}")
    
    # Sample training client data
    sample_clients = [
        {
            'member_id': 'test_123',
            'clubos_member_id': 'test_123',
            'first_name': 'Test',
            'last_name': 'Client',
            'member_name': 'Test Client',
            'email': 'test@example.com',
            'phone': '555-0123',
            'trainer_name': 'Jeremy Mayo',
            'membership_type': 'Personal Training',
            'source': 'test_sync',
            'active_packages': [{'name': 'Test Package', 'sessions': 10}],
            'package_summary': 'Test Package (10 sessions)',
            'package_details': [{'id': 1, 'name': 'Test Package'}],
            'past_due_amount': 0.0,
            'total_past_due': 0.0,
            'payment_status': 'Current',
            'sessions_remaining': 10,
            'last_session': 'Never',
            'financial_summary': 'Current',
            'last_updated': '2024-01-15'
        }
    ]
    
    # Test the sync
    try:
        result = db_manager.save_training_clients_to_db(sample_clients)
        
        if result:
            logger.info("✅ Training clients sync test PASSED")
            
            # Verify the data was saved
            saved_client = db_manager.execute_query(
                "SELECT * FROM training_clients WHERE member_id = ?",
                ('test_123',),
                fetch_one=True
            )
            
            if saved_client:
                logger.info(f"✅ Test client found in database: {saved_client[4]}")  # member_name
            else:
                logger.error("❌ Test client not found in database")
                
        else:
            logger.error("❌ Training clients sync test FAILED")
            
    except Exception as e:
        logger.error(f"❌ Training clients sync test ERROR: {e}")
    
    logger.info("🧪 Test complete")

if __name__ == "__main__":
    test_training_clients_sync()