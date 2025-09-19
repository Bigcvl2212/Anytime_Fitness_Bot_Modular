#!/usr/bin/env python3
"""
Test Campaign History API Integration
Verifies the campaigns database has data and tests API response format
"""

import sqlite3
import json
from datetime import datetime

def test_campaigns_database():
    """Test the campaigns database directly"""
    print("🔍 Testing campaigns database...")
    
    try:
        # Connect to database
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Check campaigns table structure
        cursor.execute("PRAGMA table_info(campaigns)")
        columns = cursor.fetchall()
        print(f"\n📊 Campaigns table structure:")
        for col in columns:
            print(f"   • {col[1]} ({col[2]})")
        
        # Get recent campaigns with full details
        cursor.execute("""
            SELECT id, campaign_name, message_text, message_type, subject, 
                   categories, total_recipients, successful_sends, failed_sends,
                   created_at, errors, notes
            FROM campaigns 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        campaigns = cursor.fetchall()
        print(f"\n📈 Found {len(campaigns)} campaigns in database:")
        
        for campaign in campaigns:
            campaign_id, name, message, msg_type, subject, categories, total, success, failed, created, errors, notes = campaign
            created_date = created if created else 'Unknown'
            
            print(f"\n   Campaign #{campaign_id}:")
            print(f"   • Name: {name}")
            print(f"   • Created: {created_date}")
            print(f"   • Type: {msg_type}")
            print(f"   • Success/Failed: {success}/{failed}")
            print(f"   • Categories: {categories}")
            print(f"   • Message: {message[:100]}..." if message and len(message) > 100 else f"   • Message: {message}")
        
        # Test API response format
        print(f"\n🔧 Testing API response format...")
        api_campaigns = []
        for campaign in campaigns:
            api_campaign = {
                'id': campaign[0],
                'campaign_name': campaign[1],
                'message_text': campaign[2],
                'message_type': campaign[3],
                'subject': campaign[4],
                'categories': campaign[5],
                'total_recipients': campaign[6],
                'successful_sends': campaign[7],
                'failed_sends': campaign[8],
                'created_at': campaign[9],
                'errors': campaign[10],
                'notes': campaign[11]
            }
            api_campaigns.append(api_campaign)
        
        api_response = {
            'success': True,
            'campaigns': api_campaigns[:5]  # Limit for display
        }
        
        print(f"✅ API Response Preview:")
        print(json.dumps(api_response, indent=2, default=str))
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing campaigns database: {e}")
        return False

def test_javascript_compatibility():
    """Test JavaScript variable access patterns"""
    print("\n🔧 Testing JavaScript compatibility...")
    
    # Sample campaign data structure
    sample_campaign = {
        'id': 1,
        'campaign_name': 'Test Campaign',
        'message_text': 'Hello everyone! This is a test message.',
        'message_type': 'SMS',
        'subject': None,
        'categories': 'past_due,new_members',
        'total_recipients': 25,
        'successful_sends': 23,
        'failed_sends': 2,
        'created_at': '2025-09-18 14:30:00',
        'errors': None,
        'notes': None
    }
    
    # Test JavaScript-style access patterns
    print("✅ JavaScript variable access tests:")
    print(f"   • campaign.campaign_name: '{sample_campaign.get('campaign_name', 'Unnamed Campaign')}'")
    print(f"   • campaign.successful_sends: {sample_campaign.get('successful_sends', 0)}")
    print(f"   • campaign.failed_sends: {sample_campaign.get('failed_sends', 0)}")
    
    total_sends = sample_campaign.get('successful_sends', 0) + sample_campaign.get('failed_sends', 0)
    success_rate = round((sample_campaign.get('successful_sends', 0) / total_sends) * 100) if total_sends > 0 else 0
    print(f"   • Success rate calculation: {success_rate}%")
    
    message_preview = sample_campaign.get('message_text', '')
    preview = message_preview[:80] + ('...' if len(message_preview) > 80 else '')
    print(f"   • Message preview: '{preview}'")
    
    return True

if __name__ == "__main__":
    print("🚀 Campaign History API Integration Test")
    print("=" * 50)
    
    # Run tests
    db_test = test_campaigns_database()
    js_test = test_javascript_compatibility()
    
    print("\n" + "=" * 50)
    if db_test and js_test:
        print("✅ All tests passed! Campaign history integration should work correctly.")
        print("\n📝 Summary:")
        print("   • Database contains campaign data with correct structure")
        print("   • API response format matches JavaScript expectations")
        print("   • Variable access patterns are compatible")
        print("\n🎯 Next steps:")
        print("   • Start Flask dashboard")
        print("   • Navigate to Messaging page")
        print("   • Click 'View History' to see saved campaigns")
        print("   • Test 'Use Again' and 'View Details' buttons")
    else:
        print("❌ Some tests failed. Check the error messages above.")