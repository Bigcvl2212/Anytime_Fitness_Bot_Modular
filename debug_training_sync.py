#!/usr/bin/env python3
"""
Debug script to test training client sync functionality
"""
import sys
import os
import logging
from typing import List, Dict, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_training_sync():
    """Test training client sync functionality"""
    try:
        logger.info("🔧 Testing training client sync functionality...")
        
        # Test ClubOS Integration directly
        logger.info("📋 Step 1: Testing ClubOS Integration...")
        try:
            from src.services.clubos_integration import ClubOSIntegration
            
            clubos = ClubOSIntegration()
            logger.info(f"✅ ClubOS Integration created: {clubos}")
            
            # Test authentication
            logger.info("🔐 Step 2: Testing ClubOS authentication...")
            auth_success = clubos.authenticate()
            logger.info(f"🔐 ClubOS authentication: {'✅ SUCCESS' if auth_success else '❌ FAILED'}")
            
            if not auth_success:
                logger.error("❌ Cannot proceed without authentication")
                return
            
            # Test getting training clients
            logger.info("🏋️ Step 3: Testing get_training_clients...")
            training_clients = clubos.get_training_clients()
            logger.info(f"🏋️ Training clients result: {type(training_clients)} with {len(training_clients) if training_clients else 0} items")
            
            if training_clients:
                logger.info(f"✅ Found {len(training_clients)} training clients:")
                for i, client in enumerate(training_clients[:3]):  # Show first 3
                    logger.info(f"  {i+1}. {client.get('full_name', 'Unknown')} - {client.get('payment_status', 'Unknown')}")
                if len(training_clients) > 3:
                    logger.info(f"  ... and {len(training_clients) - 3} more")
            else:
                logger.warning("⚠️ No training clients returned")
                
        except Exception as e:
            logger.error(f"❌ ClubOS Integration test failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test multi-club startup sync
        logger.info("🔄 Step 4: Testing multi-club startup sync...")
        try:
            from src.services.multi_club_startup_sync import sync_training_clients_for_club
            
            sync_result = sync_training_clients_for_club()
            logger.info(f"🔄 Sync result: {type(sync_result)} with {len(sync_result) if sync_result else 0} items")
            
            if sync_result:
                logger.info(f"✅ Sync returned {len(sync_result)} training clients")
            else:
                logger.warning("⚠️ Sync returned no training clients")
                
        except Exception as e:
            logger.error(f"❌ Multi-club sync test failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test database save
        logger.info("💾 Step 5: Testing database save...")
        try:
            from src.services.database_manager import DatabaseManager
            
            db_manager = DatabaseManager()
            logger.info(f"✅ Database manager created: {db_manager}")
            
            # Test with some dummy data if no real data
            if not training_clients:
                logger.warning("⚠️ No training clients to save, creating test data")
                training_clients = [
                    {
                        'id': 'test123',
                        'full_name': 'Test Client',
                        'payment_status': 'Current',
                        'past_due_amount': 0.0
                    }
                ]
            
            save_success = db_manager.save_training_clients_to_db(training_clients)
            logger.info(f"💾 Database save: {'✅ SUCCESS' if save_success else '❌ FAILED'}")
            
        except Exception as e:
            logger.error(f"❌ Database save test failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        logger.error(f"❌ Overall test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_training_sync()