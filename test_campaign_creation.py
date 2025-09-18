#!/usr/bin/env python3
"""Test campaign creation with specific categories"""

import requests
import json

def test_campaign_creation_by_category():
    """Test campaign creation for each category"""
    base_url = "http://localhost:5000"
    categories = [
        ('prospects', 'Prospect Welcome Campaign'),
        ('green', 'Green Member Engagement'),
        ('training_clients', 'Training Package Promotion'),
        ('past_due', 'Past Due Reminder')
    ]
    
    print("🎯 Testing Campaign Creation by Category...")
    print("=" * 60)
    
    for category, campaign_name in categories:
        print(f"\n📊 Testing {category} campaign creation...")
        
        campaign_data = {
            "category": category,
            "name": campaign_name, 
            "message": f"Test message for {category} category",
            "message_type": "sms",
            "max_recipients": 5
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/campaigns/create", 
                json=campaign_data,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if result.get('status') == 'success':
                print(f"✅ {category} campaign created successfully!")
                campaign_id = result.get('campaign_id')
                if campaign_id:
                    print(f"   Campaign ID: {campaign_id}")
            else:
                print(f"❌ {category} campaign creation failed: {result.get('message', 'Unknown error')}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ {category} campaign creation timed out")
        except Exception as e:
            print(f"💥 {category} campaign creation error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_campaign_creation_by_category()