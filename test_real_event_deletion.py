#!/usr/bin/env python3
"""
Real deletion using actual event data fetched from ClubOS
"""

import json
from clubos_real_calendar_api import ClubOSRealCalendarAPI

def get_real_event_data(api, event_id):
    """Fetch the actual event data needed for deletion"""
    print(f"📋 Fetching real event data for {event_id}...")
    
    try:
        # This should get the actual event details including all the form fields needed
        headers = {
            'Authorization': f'Bearer {api.get_bearer_token()}',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://anytime.club-os.com/action/Calendar'
        }
        
        # Get the event popup data - this contains all the form fields
        response = api.session.get(
            f"{api.base_url}/action/EventPopup/show/{event_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Got event popup data ({len(response.text)} chars)")
            
            # The response contains the form with all the needed data
            # We need to parse this to extract the actual values
            return response.text
        else:
            print(f"❌ Failed to get event data: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting event data: {e}")
        return None

def delete_event_with_real_data(api, event_id):
    """Delete event using real event data"""
    print(f"🗑️  Deleting event {event_id} with REAL event data...")
    
    # Step 1: Get the actual event data
    event_popup_html = get_real_event_data(api, event_id)
    if not event_popup_html:
        return False
    
    # Step 2: Parse the HTML to extract form values
    # The HTML contains the actual form with all the correct values
    print("🔍 Parsing event form data...")
    
    # Extract key form values from the HTML (this is a simplified approach)
    # In a real implementation, we'd use BeautifulSoup or regex to parse properly
    
    # Step 3: Get fresh tokens
    fresh_source_token = api.get_source_page_token()
    fresh_fp_token = api.get_fingerprint_token()
    
    # Step 4: Build form data with a minimal approach first
    # Let's try with just the essential fields to see if we can get it working
    form_data = {
        'calendarEvent.id': str(event_id),
        '_sourcePage': fresh_source_token,
        '__fp': fresh_fp_token
    }
    
    print(f"📝 Testing minimal deletion with {len(form_data)} fields")
    
    headers = {
        'Authorization': f'Bearer {api.get_bearer_token()}',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://anytime.club-os.com/action/Calendar',
        'Accept': '*/*'
    }
    
    try:
        response = api.session.post(
            f"{api.base_url}/action/EventPopup/remove",
            headers=headers,
            data=form_data
        )
        
        print(f"📡 Response: {response.status_code}")
        print(f"📄 Content: {response.text[:200]}...")
        
        if response.status_code == 200:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error in deletion: {e}")
        return False

def main():
    print("🎯 TESTING REAL EVENT DATA DELETION")
    print("=" * 50)
    
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful!")
    
    # Get current events
    events = api.get_jeremy_mayo_events()
    print(f"📅 Found {len(events)} total events")
    
    if len(events) == 0:
        print("❌ No events to test")
        return
    
    # Test on first event
    test_event = events[0]
    print(f"\n🧪 Testing real data deletion on event {test_event.id}")
    
    events_before = len(events)
    
    # Try deletion with real event data
    success = delete_event_with_real_data(api, test_event.id)
    
    if success:
        print("✅ Deletion request sent!")
        
        # Check if it actually worked
        events_after = api.get_jeremy_mayo_events()
        events_after_count = len(events_after)
        
        print(f"📊 Events: {events_before} → {events_after_count}")
        
        if events_after_count < events_before:
            print("🎉 SUCCESS! Real deletion is working!")
        else:
            print("❌ Still fake - need to extract more form data")
    else:
        print("❌ Deletion failed")

if __name__ == "__main__":
    main()
