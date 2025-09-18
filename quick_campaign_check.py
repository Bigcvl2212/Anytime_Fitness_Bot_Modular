"""
Quick Campaign Status Check
Check if campaigns are being saved and tracked properly
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def check_campaign_status():
    """Quick check of campaign system status"""
    print("🔍 Checking Campaign System Status...")
    
    # Check prospects campaign status
    print("\n1️⃣ Checking Prospects Campaign Status:")
    try:
        response = requests.get(f"{BASE_URL}/api/campaigns/status/prospects")
        status_data = response.json()
        print(f"   Status: {json.dumps(status_data, indent=2)}")
        
        if status_data.get('status') != 'none':
            print(f"   ✅ Found active campaign: {status_data.get('name', 'Unknown')}")
            campaign_id = status_data.get('campaign_id')
            
            if campaign_id:
                # Get campaign progress
                print(f"\n2️⃣ Checking Campaign Progress (ID: {campaign_id}):")
                progress_response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}/progress")
                progress_data = progress_response.json()
                print(f"   Progress: {json.dumps(progress_data, indent=2)}")
        else:
            print("   ⚠️ No active campaigns found for prospects")
            
    except Exception as e:
        print(f"   ❌ Error checking campaign status: {e}")
    
    # Check campaign templates
    print("\n3️⃣ Checking Campaign Templates:")
    try:
        response = requests.get(f"{BASE_URL}/api/campaigns/templates")
        templates_data = response.json()
        print(f"   Templates: {json.dumps(templates_data, indent=2)}")
    except Exception as e:
        print(f"   ❌ Error checking templates: {e}")

if __name__ == "__main__":
    check_campaign_status()