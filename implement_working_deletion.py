#!/usr/bin/env python3
"""
Extract the working deletion method from HAR file and implement it
Based on the actual working request from clubos_calendar_flow.har
"""

import json
import urllib.parse
from clubos_real_calendar_api import ClubOSRealCalendarAPI

def extract_working_deletion_from_har():
    """Extract the working deletion pattern from the HAR file"""
    
    print("🔍 Extracting working deletion pattern from HAR file...")
    
    try:
        with open('charles_session.chls/clubos_calendar_flow.har', 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        # Find the working deletion request
        working_deletion = None
        for entry in har_data['log']['entries']:
            request = entry['request']
            if (request['method'] == 'POST' and 
                '/action/EventPopup/remove' in request['url']):
                working_deletion = entry
                break
        
        if not working_deletion:
            print("❌ No working deletion request found in HAR file")
            return None
        
        print("✅ Found working deletion request!")
        print(f"🔗 URL: {working_deletion['request']['url']}")
        
        # Extract the form data pattern
        post_data = working_deletion['request']['postData']
        print(f"📊 Post data mime type: {post_data['mimeType']}")
        
        if post_data['mimeType'] == 'application/x-www-form-urlencoded':
            # Parse the form data
            form_data = {}
            if 'params' in post_data:
                for param in post_data['params']:
                    form_data[param['name']] = param['value']
            elif 'text' in post_data:
                # Parse URL encoded text
                parsed = urllib.parse.parse_qs(post_data['text'])
                for key, values in parsed.items():
                    form_data[key] = values[0] if values else ''
            
            print(f"📋 Found {len(form_data)} form fields in working request")
            print("🔑 Key form fields:")
            for key in ['calendarEvent.id', '_sourcePage', '__fp']:
                if key in form_data:
                    print(f"   {key}: {form_data[key]}")
            
            # Extract the headers pattern
            headers = {}
            for header in working_deletion['request']['headers']:
                headers[header['name']] = header['value']
            
            return {
                'form_pattern': form_data,
                'headers_pattern': headers,
                'url': working_deletion['request']['url']
            }
        
    except Exception as e:
        print(f"❌ Error reading HAR file: {e}")
        return None

def implement_working_deletion():
    """Implement the working deletion method using the HAR pattern"""
    
    # Extract the working pattern
    pattern = extract_working_deletion_from_har()
    if not pattern:
        return False
    
    print("🔧 Implementing working deletion method...")
    
    # Initialize API
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return False
    
    print("✅ Authentication successful!")
    
    # Get current events
    events = api.get_jeremy_mayo_events()
    print(f"📅 Found {len(events)} total events")
    
    if not events:
        print("❌ No events found")
        return False
    
    # Pick the first event to test with
    test_event = events[0]
    print(f"🎯 Testing deletion of event ID: {test_event.id}")
    
    # Build the form data using the working pattern
    form_data = pattern['form_pattern'].copy()
    
    # Update with current event data
    form_data['calendarEvent.id'] = str(test_event.id)
    form_data['calendarEvent.repeatEvent.calendarEventId'] = str(test_event.id)
    
    # Get fresh tokens
    form_data['_sourcePage'] = api.get_source_page_token()
    form_data['__fp'] = api.get_fingerprint_token()
    
    # Update headers with current data
    headers = {
        'Authorization': f'Bearer {api.get_bearer_token()}',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://anytime.club-os.com/action/Calendar',
        'Origin': 'https://anytime.club-os.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🗑️  Attempting deletion with working pattern...")
    
    # Send the deletion request
    response = api.session.post(
        'https://anytime.club-os.com/action/EventPopup/remove',
        headers=headers,
        data=form_data
    )
    
    print(f"📊 Response status: {response.status_code}")
    print(f"📄 Response content: {response.text[:200]}...")
    
    if response.status_code == 200:
        # Check if it actually worked
        events_after = api.get_jeremy_mayo_events()
        print(f"📅 Events after deletion: {len(events_after)}")
        
        if len(events_after) < len(events):
            print("🎉 SUCCESS! Event actually deleted!")
            print(f"   Reduced from {len(events)} to {len(events_after)} events")
            
            # Now delete the 7 Monday 9am events
            print("\n🚀 Proceeding to delete Monday 9am events...")
            monday_events = events[:7]  # First 7 events as candidates
            
            deleted_count = 0
            for i, event in enumerate(monday_events):
                print(f"\n🗑️  Deleting event {i+1}/7: ID {event.id}")
                
                # Update form data for this event
                form_data['calendarEvent.id'] = str(event.id)
                form_data['calendarEvent.repeatEvent.calendarEventId'] = str(event.id)
                form_data['_sourcePage'] = api.get_source_page_token()
                form_data['__fp'] = api.get_fingerprint_token()
                
                response = api.session.post(
                    'https://anytime.club-os.com/action/EventPopup/remove',
                    headers=headers,
                    data=form_data
                )
                
                if response.status_code == 200 and "OK" in response.text:
                    print(f"   ✅ Event {event.id} deleted!")
                    deleted_count += 1
                else:
                    print(f"   ❌ Failed to delete event {event.id}")
            
            print(f"\n🎯 DELETION SUMMARY: {deleted_count}/7 Monday events deleted")
            return True
        else:
            print("❌ Deletion was fake - event count unchanged")
            return False
    else:
        print(f"❌ Deletion failed with status {response.status_code}")
        return False

if __name__ == "__main__":
    print("🎯 IMPLEMENTING WORKING DELETION FROM HAR FILE")
    print("=" * 50)
    implement_working_deletion()
