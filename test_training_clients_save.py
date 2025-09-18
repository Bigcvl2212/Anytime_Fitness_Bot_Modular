#!/usr/bin/env python3

"""
Test Training Clients Save Operation
===================================

This script tests the training clients save operation to identify the failure.
Creates a sample training client and attempts to save it to the database.
"""

import sys
import os
import logging
import sqlite3

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.database_manager import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_training_clients_save():
    """Test the training clients save operation with sample data"""
    
    print("🧪 Testing training clients save operation...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Check current database schema for training_clients table
    print("\n📋 Checking training_clients table schema...")
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(training_clients)")
        columns = cursor.fetchall()
        
        print(f"✅ Training clients table has {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Failed to check schema: {e}")
        return False
    
    # Create sample training client data
    sample_training_client = {
        'member_id': '12345678',
        'clubos_member_id': '12345678',
        'first_name': 'Test',
        'last_name': 'Client',
        'full_name': 'Test Client',
        'member_name': 'Test Client',
        'email': 'test.client@example.com',
        'phone': '555-123-4567',
        'status': 'Active',
        'trainer_name': 'Jeremy Mayo',
        'membership_type': 'Personal Training',
        'source': 'test_script',
        'active_packages': [{'name': 'Test Package', 'sessions': 10}],
        'package_summary': 'Test package summary',
        'package_details': [{'detail': 'Test detail'}],
        'past_due_amount': 0.0,
        'total_past_due': 0.0,
        'payment_status': 'Current',
        'sessions_remaining': 10,
        'last_session': 'Never',
        'financial_summary': 'Current',
        'last_updated': '2025-01-14'
    }
    
    print(f"\n💾 Testing save with sample data:")
    print(f"  Member ID: {sample_training_client['member_id']}")
    print(f"  Name: {sample_training_client['member_name']}")
    print(f"  Email: {sample_training_client['email']}")
    
    # Test the save operation
    try:
        result = db_manager.save_training_clients_to_db([sample_training_client])
        
        if result:
            print("✅ Training clients save operation succeeded!")
            
            # Verify the data was saved
            print("\n🔍 Verifying saved data...")
            saved_client = db_manager.execute_query(
                "SELECT * FROM training_clients WHERE member_id = ?",
                (sample_training_client['member_id'],),
                fetch_one=True
            )
            
            if saved_client:
                print(f"✅ Found saved training client: {saved_client[4]} ({saved_client[1]})")
                return True
            else:
                print("❌ Training client was not found after save")
                return False
                
        else:
            print("❌ Training clients save operation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Exception during save operation: {e}")
        import traceback
        print(f"💥 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_training_clients_save()
    
    if success:
        print("\n🎯 RESULT: Training clients save operation is working correctly")
    else:
        print("\n🚨 RESULT: Training clients save operation has issues that need to be fixed")