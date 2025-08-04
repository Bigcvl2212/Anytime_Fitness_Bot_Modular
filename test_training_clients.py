"""
Test script to get all training clients from ClubOS
"""

import os
import sys
import json
from datetime import datetime

# Add the services directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.api.enhanced_clubos_client import EnhancedClubOSAPIClient
    from services.api.clubos_api_client import ClubOSAPIAuthentication
    from config.secrets_local import get_secret
    
    print("✅ Successfully imported ClubOS API modules")
    
    def test_training_clients_api():
        """Test getting all training clients"""
        
        print("\n🔐 Testing ClubOS Authentication...")
        
        # Initialize authentication
        auth = ClubOSAPIAuthentication()
        
        # Get credentials
        username = get_secret('clubos-username')
        password = get_secret('clubos-password')
        
        if not username or not password:
            print("❌ Missing ClubOS credentials in secrets")
            return False
        
        # Authenticate
        if not auth.login(username, password):
            print("❌ ClubOS authentication failed")
            return False
        
        print("✅ ClubOS authentication successful")
        
        # Initialize enhanced client
        client = EnhancedClubOSAPIClient(auth)
        
        print("\n📋 Testing get_all_training_clients...")
        
        try:
            training_clients = client.get_all_training_clients()
            print(f"✅ Retrieved {len(training_clients)} training clients")
            
            if training_clients:
                print("\n📄 First few training clients:")
                for i, client_data in enumerate(training_clients[:3]):
                    print(f"\n   Client {i+1}: {json.dumps(client_data, indent=4)}")
                    
                # Test getting packages for first client if available
                if len(training_clients) > 0:
                    first_client = training_clients[0]
                    client_id = first_client.get('id') or first_client.get('member_id')
                    
                    if client_id:
                        print(f"\n📦 Testing training packages for client ID: {client_id}")
                        packages_result = client.get_training_packages_for_client(str(client_id))
                        print(f"   📋 Packages result: {json.dumps(packages_result, indent=4)}")
                    
            else:
                print("⚠️ No training clients found")
                
        except Exception as e:
            print(f"❌ Error testing training clients: {e}")
            import traceback
            traceback.print_exc()
                
        return True
    
    if __name__ == "__main__":
        test_training_clients_api()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure you're running from the gym-bot-modular directory")
    print("   And that all required files exist in services/api/")
