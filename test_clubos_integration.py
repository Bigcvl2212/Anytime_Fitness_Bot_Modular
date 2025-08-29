#!/usr/bin/env python3
"""
Test script to verify ClubOS integration with training API
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.services.clubos_integration import ClubOSIntegration
    print("✅ ClubOS Integration imported successfully")
    
    # Create integration instance
    integration = ClubOSIntegration()
    print(f"✅ Integration instance created")
    
    # Try to authenticate
    print("🔐 Attempting authentication...")
    auth_result = integration.authenticate()
    print(f"✅ Authentication result: {auth_result}")
    print(f"✅ Authenticated: {integration.authenticated}")
    print(f"✅ Training API available: {integration.training_api is not None}")
    
    if auth_result and integration.training_api:
        # Try to get training clients
        print("📋 Fetching training clients...")
        training_clients = integration.get_training_clients()
        print(f"✅ Training clients fetched: {len(training_clients) if training_clients else 0}")
        
        if training_clients and len(training_clients) > 0:
            # Try to get payment details for the first client
            first_client = training_clients[0]
            member_id = first_client.get('id')
            print(f"🔍 Testing payment details for member: {member_id}")
            
            if member_id:
                # Try to get package details
                package_details = integration.training_api.get_member_training_payment_details(member_id)
                print(f"✅ Package details: {package_details}")
            else:
                print("⚠️ No member ID found in first client")
        else:
            print("⚠️ No training clients found")
    else:
        print("❌ Authentication failed or training API not available")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

