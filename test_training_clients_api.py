import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_clients_api import ClubOSTrainingClientsAPI
import json

def test_training_clients_api():
    """Test the ClubOS Training Clients API to find Dennis"""
    print("🧪 TESTING CLUBOS TRAINING CLIENTS API")
    print("=" * 50)
    
    api = ClubOSTrainingClientsAPI()
    
    try:
        print("🔐 Authenticating...")
        if not api.authenticate():
            print("❌ Authentication failed")
            return
            
        print("✅ Authentication successful")
        
        # Get training clients
        print("\n🔍 Getting all training clients...")
        training_clients = api.get_training_clients()
        
        if training_clients:
            print(f"✅ Found {len(training_clients)} training clients")
            
            # Look for Dennis in the training clients
            dennis_found = False
            
            for i, client in enumerate(training_clients):
                print(f"\n👤 Client {i+1}:")
                
                # Print all client data
                if isinstance(client, dict):
                    for key, value in client.items():
                        print(f"   {key}: {value}")
                        
                        # Look for Dennis specifically
                        if isinstance(value, str):
                            value_lower = value.lower()
                            if 'dennis' in value_lower or 'rost' in value_lower:
                                print(f"   🎯 DENNIS FOUND! {key}: {value}")
                                dennis_found = True
                                
                else:
                    print(f"   {client}")
                    client_str = str(client).lower()
                    if 'dennis' in client_str or 'rost' in client_str:
                        print(f"   🎯 DENNIS FOUND! {client}")
                        dennis_found = True
                        
                # Limit output to avoid spam
                if i >= 10:
                    print(f"\n... (showing first 10 clients, {len(training_clients) - 10} more available)")
                    break
            
            if dennis_found:
                print(f"\n🎉 SUCCESS: Dennis found in training clients data!")
            else:
                print(f"\n❌ Dennis not found in training clients data")
                print(f"This confirms Dennis is not in ClubOS training system")
                
        else:
            print("❌ No training clients returned")
            
        # Also try the personal training dashboard
        print(f"\n🔍 Getting personal training dashboard...")
        dashboard_data = api.get_personal_training_dashboard()
        
        if dashboard_data:
            print(f"✅ Got dashboard data")
            
            # Look for Dennis in dashboard data
            dashboard_str = str(dashboard_data).lower()
            if 'dennis' in dashboard_str or 'rost' in dashboard_str:
                print(f"🎯 DENNIS FOUND in dashboard data!")
                print(f"Dashboard data: {json.dumps(dashboard_data, indent=2)}")
            else:
                print(f"❌ Dennis not found in dashboard data")
                
            print(f"📊 Dashboard structure:")
            if isinstance(dashboard_data, dict):
                for key, value in dashboard_data.items():
                    if isinstance(value, list):
                        print(f"   {key}: list[{len(value)}]")
                    else:
                        print(f"   {key}: {type(value).__name__}")
        else:
            print("❌ No dashboard data returned")
            
    except Exception as e:
        print(f"❌ Error testing training clients API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_training_clients_api()
