#!/usr/bin/env python3
"""
Extract complete form data from event popup and use for deletion
"""

import re
from bs4 import BeautifulSoup
from clubos_real_calendar_api import ClubOSRealCalendarAPI

def extract_form_data_from_popup(html_content):
    """Extract all form field values from event popup HTML"""
    print("🔍 Extracting form data from event popup HTML...")
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        form_data = {}
        
        # Find all input fields
        inputs = soup.find_all(['input', 'select', 'textarea'])
        
        for input_elem in inputs:
            name = input_elem.get('name')
            if name:
                value = input_elem.get('value', '')
                
                # Handle different input types
                if input_elem.name == 'select':
                    selected = input_elem.find('option', selected=True)
                    if selected:
                        value = selected.get('value', '')
                elif input_elem.get('type') == 'checkbox':
                    value = 'true' if input_elem.get('checked') else 'false'
                elif input_elem.get('type') == 'radio':
                    if input_elem.get('checked'):
                        value = input_elem.get('value', '')
                    else:
                        continue  # Skip unchecked radio buttons
                
                form_data[name] = value
        
        print(f"✅ Extracted {len(form_data)} form fields from popup")
        return form_data
        
    except Exception as e:
        print(f"❌ Error parsing HTML: {e}")
        return {}

def delete_event_with_complete_form(api, event_id):
    """Delete event using complete form data from popup"""
    print(f"🗑️  Deleting event {event_id} with complete form data...")
    
    try:
        # Step 1: Get the event popup HTML
        headers = {
            'Authorization': f'Bearer {api.get_bearer_token()}',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://anytime.club-os.com/action/Calendar'
        }
        
        response = api.session.get(
            f"{api.base_url}/action/EventPopup/show/{event_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get event popup: {response.status_code}")
            return False
            
        print(f"✅ Got event popup HTML ({len(response.text)} chars)")
        
        # Step 2: Extract form data
        form_data = extract_form_data_from_popup(response.text)
        
        if not form_data:
            print("❌ No form data extracted")
            return False
        
        # Step 3: Update with fresh tokens
        fresh_source_token = api.get_source_page_token()
        fresh_fp_token = api.get_fingerprint_token()
        
        form_data['_sourcePage'] = fresh_source_token
        form_data['__fp'] = fresh_fp_token
        
        print(f"📝 Using complete form data with {len(form_data)} fields")
        
        # Log some key fields for debugging
        key_fields = ['calendarEvent.id', 'calendarEvent.subject', 'calendarEvent.eventType']
        for field in key_fields:
            if field in form_data:
                print(f"   {field}: {form_data[field]}")
        
        # Step 4: Send deletion request
        deletion_headers = {
            'Authorization': f'Bearer {api.get_bearer_token()}',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://anytime.club-os.com/action/Calendar',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://anytime.club-os.com'
        }
        
        delete_response = api.session.post(
            f"{api.base_url}/action/EventPopup/remove",
            headers=deletion_headers,
            data=form_data
        )
        
        print(f"📡 Deletion response: {delete_response.status_code}")
        print(f"📄 Response content: {delete_response.text[:300]}...")
        
        if delete_response.status_code == 200 and "Something isn't right" not in delete_response.text:
            return True
        else:
            print(f"❌ Deletion failed: {delete_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in deletion: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎯 TESTING COMPLETE FORM DATA DELETION")
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
    print(f"\n🧪 Testing complete form deletion on event {test_event.id}")
    
    events_before = len(events)
    
    # Try deletion with complete form data
    success = delete_event_with_complete_form(api, test_event.id)
    
    if success:
        print("✅ Deletion request completed!")
        
        # Verify deletion
        import time
        time.sleep(2)  # Wait for backend to process
        
        events_after = api.get_jeremy_mayo_events()
        events_after_count = len(events_after)
        
        print(f"📊 Events: {events_before} → {events_after_count}")
        
        if events_after_count < events_before:
            print("🎉 SUCCESS! Complete form deletion is working!")
            print("🚀 Ready to delete the 7 Monday 9am events!")
        else:
            print("❌ Still no actual deletion - investigating further...")
    else:
        print("❌ Deletion failed")

if __name__ == "__main__":
    main()
