#!/usr/bin/env python3
"""
Debug Training Data Flow
Trace exactly what happens to the training client data from API to database
"""

import os
import sys
import logging
import json

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_training_data_flow():
    """Debug the complete training data flow"""
    try:
        logger.info("🔍 DEBUGGING TRAINING DATA FLOW")
        
        # STEP 1: Test ClubOS Integration directly
        logger.info("📋 STEP 1: Testing ClubOS Integration directly...")
        
        from src.services.clubos_integration import ClubOSIntegration
        
        clubos = ClubOSIntegration()
        if not clubos.authenticate():
            logger.error("❌ ClubOS authentication failed")
            return
        
        # Get training clients directly
        training_clients = clubos.get_training_clients()
        logger.info(f"✅ ClubOS returned {len(training_clients) if training_clients else 0} training clients")
        
        if training_clients:
            # Check first client's data structure
            first_client = training_clients[0]
            logger.info(f"📊 First client data structure:")
            logger.info(f"   Name: {first_client.get('member_name', 'Unknown')}")
            logger.info(f"   Package Details: {first_client.get('package_details', 'None')}")
            logger.info(f"   Payment Status: {first_client.get('payment_status', 'None')}")
            logger.info(f"   Past Due Amount: {first_client.get('past_due_amount', 0)}")
            logger.info(f"   Total Past Due: {first_client.get('total_past_due', 0)}")
            
            # Check if any clients have billing data
            clients_with_billing = [c for c in training_clients if c.get('package_details') and len(c.get('package_details', [])) > 0]
            clients_with_past_due = [c for c in training_clients if c.get('total_past_due', 0) > 0]
            
            logger.info(f"📊 Clients with package_details: {len(clients_with_billing)}/{len(training_clients)}")
            logger.info(f"💰 Clients with past due amounts: {len(clients_with_past_due)}/{len(training_clients)}")
            
            if clients_with_past_due:
                logger.info(f"💰 Clients with past due amounts:")
                for client in clients_with_past_due[:3]:  # Show first 3
                    logger.info(f"   {client.get('member_name', 'Unknown')}: ${client.get('total_past_due', 0):.2f}")
        
        # STEP 2: Test database saving directly
        logger.info("💾 STEP 2: Testing database saving directly...")
        
        from src.services.database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        
        if training_clients:
            # Save to database
            success = db_manager.save_training_clients_to_db(training_clients)
            logger.info(f"💾 Database save result: {success}")
            
            if success:
                # Verify data was saved
                saved_clients = db_manager.get_training_clients_with_agreements()
                logger.info(f"✅ Verified: {len(saved_clients)} clients retrieved from database")
                
                # Check if billing data was preserved
                saved_clients_with_billing = [c for c in saved_clients if c.get('package_details') and len(str(c.get('package_details', ''))) > 10]
                saved_clients_with_past_due = [c for c in saved_clients if c.get('total_past_due', 0) > 0]
                
                logger.info(f"📊 Saved clients with package_details: {len(saved_clients_with_billing)}/{len(saved_clients)}")
                logger.info(f"💰 Saved clients with past due amounts: {len(saved_clients_with_past_due)}/{len(saved_clients)}")
                
                if saved_clients_with_past_due:
                    logger.info(f"💰 Saved clients with past due amounts:")
                    for client in saved_clients_with_past_due[:3]:  # Show first 3
                        logger.info(f"   {client.get('member_name', 'Unknown')}: ${client.get('total_past_due', 0):.2f}")
            else:
                logger.error("❌ Database save failed")
        
        # STEP 3: Test multi-club sync
        logger.info("🔄 STEP 3: Testing multi-club sync...")
        
        from src.services.multi_club_startup_sync import sync_training_clients_for_club
        
        synced_clients = sync_training_clients_for_club("1156")
        logger.info(f"🔄 Multi-club sync returned {len(synced_clients) if synced_clients else 0} training clients")
        
        if synced_clients:
            # Check if synced data has billing info
            synced_with_billing = [c for c in synced_clients if c.get('package_details') and len(c.get('package_details', [])) > 0]
            synced_with_past_due = [c for c in synced_clients if c.get('total_past_due', 0) > 0]
            
            logger.info(f"📊 Synced clients with package_details: {len(synced_with_billing)}/{len(synced_clients)}")
            logger.info(f"💰 Synced clients with past due amounts: {len(synced_with_past_due)}/{len(synced_clients)}")
        
        logger.info("🎉 DEBUG COMPLETE")
        
    except Exception as e:
        logger.error(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_training_data_flow()