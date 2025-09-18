"""
Test Campaign API Endpoints
Test the complete campaign management functionality
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_campaign_endpoints():
    """Test all campaign endpoints"""
    print("🧪 Testing Campaign API Endpoints...")
    
    # Test 1: Get campaign status (should be 'none' initially)
    print("\n1️⃣ Testing campaign status...")
    response = requests.get(f"{BASE_URL}/api/campaigns/status/prospects")
    status_data = response.json()
    print(f"Status Response: {status_data}")
    
    # Verify the response format matches frontend expectations
    if 'success' in status_data and 'campaign' in status_data:
        print("✅ Response format is correct for frontend!")
        print(f"   Success: {status_data['success']}")
        print(f"   Campaign: {status_data['campaign']}")
        if status_data['campaign'] is None:
            print("   No active campaign (expected for initial test)")
        else:
            print(f"   Active campaign found: {status_data['campaign']}")
    else:
        print("❌ Response format doesn't match frontend expectations!")
        print("   Expected: {'success': bool, 'campaign': data}")
        print(f"   Got: {list(status_data.keys())}")
    
    # Test 2: Create a campaign
    print("\n2️⃣ Testing campaign creation...")
    campaign_data = {
        "category": "prospects",
        "name": "Welcome Test Campaign", 
        "message": "Welcome to our gym! We'd love to meet you. Schedule a free consultation today!",
        "message_type": "sms",
        "max_recipients": 5
    }
    
    response = requests.post(f"{BASE_URL}/api/campaigns/create", json=campaign_data)
    create_result = response.json()
    print(f"Create Response: {create_result}")
    
    if create_result.get('status') == 'success':
        campaign_id = create_result['campaign_id']
        print(f"✅ Campaign created with ID: {campaign_id}")
        
        # Test 3: Get updated campaign status
        print("\n3️⃣ Testing updated campaign status...")
        response = requests.get(f"{BASE_URL}/api/campaigns/status/prospects")
        updated_status = response.json()
        print(f"Updated Status: {updated_status}")
        
        # Verify frontend format again
        if updated_status.get('success') and 'campaign' in updated_status:
            campaign_data = updated_status['campaign']
            if campaign_data:
                print(f"✅ Campaign found: {campaign_data.get('name')} (Status: {campaign_data.get('status')})")
            else:
                print("✅ Response format correct, but no active campaign found")
        else:
            print("❌ No campaign data in expected format!")
        
        # Test 4: Get campaign progress
        print("\n4️⃣ Testing campaign progress...")
        response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}/progress")
        print(f"Progress Response: {response.json()}")
        
        # Test 5: Start campaign
        print("\n5️⃣ Testing campaign start...")
        response = requests.post(f"{BASE_URL}/api/campaigns/{campaign_id}/start", json={"continue_from_position": False})
        start_result = response.json()
        print(f"Start Response: {start_result}")
        
        if start_result.get('status') == 'success':
            # Wait a moment for campaign to process
            time.sleep(2)
            
            # Test 6: Check progress during execution
            print("\n6️⃣ Testing progress during execution...")
            response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}/progress")
            print(f"Running Progress: {response.json()}")
            
            # Test 7: Pause campaign
            print("\n7️⃣ Testing campaign pause...")
            response = requests.post(f"{BASE_URL}/api/campaigns/{campaign_id}/pause")
            print(f"Pause Response: {response.json()}")
            
            # Test 8: Resume campaign
            print("\n8️⃣ Testing campaign resume...")
            response = requests.post(f"{BASE_URL}/api/campaigns/{campaign_id}/resume")
            print(f"Resume Response: {response.json()}")
    
    # Test 9: Get campaign templates
    print("\n9️⃣ Testing campaign templates...")
    response = requests.get(f"{BASE_URL}/api/campaigns/templates")
    print(f"Templates Response: {response.json()}")
    
    # Test 10: Save a campaign template
    print("\n🔟 Testing template creation...")
    template_data = {
        "name": "Welcome Template",
        "category": "prospects",
        "message": "Welcome to our fitness family! 💪 Ready to start your journey?",
        "target_group": "prospects",
        "max_recipients": 100
    }
    
    response = requests.post(f"{BASE_URL}/api/campaigns/templates", json=template_data)
    print(f"Template Save Response: {response.json()}")
    
    print("\n✅ Campaign API testing completed!")

if __name__ == "__main__":
    try:
        test_campaign_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error during testing: {e}")