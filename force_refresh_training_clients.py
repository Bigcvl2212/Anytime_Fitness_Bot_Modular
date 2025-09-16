#!/usr/bin/env python3
"""
Force refresh training clients using the fixed ClubOS integration
"""
import sys
sys.path.append('src')

from services.clubos_integration import ClubOSIntegration  
from services.database_manager import DatabaseManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def force_refresh_training_clients():
    """Force refresh training clients using fixed ClubOS integration"""
    logger.info("🔄 Force refreshing training clients with fixed ClubOS integration...")
    
    # Initialize ClubOS integration
    clubos = ClubOSIntegration()
    
    # Get training clients with enhanced billing data
    logger.info("📊 Fetching training clients from ClubOS with billing details...")
    training_clients = clubos.get_training_clients()
    
    if not training_clients:
        logger.error("❌ No training clients returned from ClubOS integration")
        return
    
    logger.info(f"✅ Retrieved {len(training_clients)} training clients from ClubOS")
    
    # Show sample data
    for i, client in enumerate(training_clients[:3]):
        logger.info(f"📋 Sample {i+1}: {client.get('member_name', 'Unknown')}")
        logger.info(f"   Past Due: ${client.get('total_past_due', 0)}")
        logger.info(f"   Payment Status: {client.get('payment_status', 'Unknown')}")
        logger.info(f"   Package Details: {len(client.get('package_details', []))} packages")
    
    # Save to database
    db_manager = DatabaseManager()
    success = db_manager.save_training_clients_to_db(training_clients)
    
    if success:
        logger.info("✅ Training clients saved to database successfully")
    else:
        logger.error("❌ Failed to save training clients to database")

if __name__ == '__main__':
    force_refresh_training_clients()