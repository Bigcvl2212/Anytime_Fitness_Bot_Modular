#!/usr/bin/env python3
"""
Test dashboard context and ClubOS integration
"""

import requests
import json

def test_dashboard_context():
    """Test the dashboard context and ClubOS integration"""
    print("🔄 Testing dashboard context and ClubOS integration...")
    
    try:
        # Test the main dashboard route
        print("\n📊 Testing main dashboard route...")
        response = requests.get('http://localhost:5000/')
        print(f"Dashboard status: {response.status_code}")
        
        if response.ok:
            # Check if the response contains events data
            content = response.text
            if 'today_events' in content:
                print("✅ Dashboard contains 'today_events' data")
            else:
                print("❌ Dashboard missing 'today_events' data")
            
            if 'clubos_status' in content:
                print("✅ Dashboard contains 'clubos_status' data")
            else:
                print("❌ Dashboard missing 'clubos_status' data")
        
        # Test the calendar events API directly
        print("\n📅 Testing calendar events API...")
        events_response = requests.get('http://localhost:5000/api/calendar/events')
        print(f"Events API status: {events_response.status_code}")
        
        if events_response.ok:
            events_data = events_response.json()
            print(f"Events API returned {len(events_data)} events")
            if events_data:
                print(f"First event: {events_data[0]}")
            else:
                print("❌ Events API returned empty events array")
        else:
            print(f"❌ Events API error: {events_response.text[:200]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing dashboard context: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dashboard_context()
    if success:
        print("\n✅ Dashboard context test completed!")
    else:
        print("\n❌ Dashboard context test failed!")








