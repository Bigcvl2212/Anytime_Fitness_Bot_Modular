#!/usr/bin/env python3
"""
Test Fixed Training Client Data Flow
Test the complete flow after fixing the database save issue
"""

import os
import sys
import logging

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

def test_fixed_training_flow():
    """Test the fixed training client data flow"""
    try:
        logger.info("🔄 TESTING FIXED TRAINING CLIENT DATA FLOW")
        
        # Check database state before refresh
        logger.info("📋 BEFORE: Checking current database state...")
        
        from src.services.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        current_clients = db_manager.get_training_clients_with_agreements()
        clients_with_past_due_before = [c for c in current_clients if c.get('total_past_due', 0) > 0]
        
        logger.info(f"📊 BEFORE: {len(current_clients)} clients in database, {len(clients_with_past_due_before)} with past due amounts")
        
        # Trigger the fixed sync process
        logger.info("🔄 TRIGGERING FIXED SYNC PROCESS...")
        
        from src.services.multi_club_startup_sync import sync_training_clients_for_club
        
        # This should now fetch data AND save to database
        synced_clients = sync_training_clients_for_club("1156")
        
        if synced_clients:
            logger.info(f"✅ Sync returned {len(synced_clients)} clients")
            
            # Check how many have billing data
            synced_with_billing = [c for c in synced_clients if c.get('package_details') and len(c.get('package_details', [])) > 0]
            synced_with_past_due = [c for c in synced_clients if c.get('total_past_due', 0) > 0]
            
            logger.info(f"📊 SYNCED DATA: {len(synced_with_billing)} clients with package_details, {len(synced_with_past_due)} with past due amounts")
            
            if synced_with_past_due:
                logger.info("💰 Clients with past due amounts from sync:")
                for client in synced_with_past_due[:5]:  # Show first 5
                    logger.info(f"   {client.get('member_name', 'Unknown')}: ${client.get('total_past_due', 0):.2f}")
        
        # Check database state after refresh
        logger.info("📋 AFTER: Checking database state after sync...")
        
        updated_clients = db_manager.get_training_clients_with_agreements()
        clients_with_past_due_after = [c for c in updated_clients if c.get('total_past_due', 0) > 0]
        
        logger.info(f"📊 AFTER: {len(updated_clients)} clients in database, {len(clients_with_past_due_after)} with past due amounts")
        
        if clients_with_past_due_after:
            logger.info("💰 Clients with past due amounts in database:")
            for client in clients_with_past_due_after[:5]:  # Show first 5
                logger.info(f"   {client.get('member_name', 'Unknown')}: ${client.get('total_past_due', 0):.2f}")
        
        # Compare before and after
        if len(clients_with_past_due_after) > len(clients_with_past_due_before):
            logger.info(f"🎉 SUCCESS: Database now has {len(clients_with_past_due_after)} clients with past due amounts (was {len(clients_with_past_due_before)})")
        elif len(clients_with_past_due_after) == len(clients_with_past_due_before) and len(clients_with_past_due_after) > 0:
            logger.info(f"✅ MAINTAINED: Database still has {len(clients_with_past_due_after)} clients with past due amounts")
        else:
            logger.warning(f"⚠️ NO IMPROVEMENT: Database still has {len(clients_with_past_due_after)} clients with past due amounts")
        
        logger.info("🎉 FIXED FLOW TEST COMPLETE")
        
    except Exception as e:
        logger.error(f"❌ Fixed flow test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_training_flow()