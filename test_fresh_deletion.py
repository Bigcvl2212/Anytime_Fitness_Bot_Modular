#!/usr/bin/env python3
"""
Parse the working deletion request from HAR file to understand the pattern
Then implement it with fresh event data
"""

import json
import base64
from urllib.parse import parse_qs
from clubos_real_calendar_api import ClubOSRealCalendarAPI

def parse_working_deletion_pattern():
    """Extract the working deletion pattern from HAR file"""
    print("🔍 Parsing working deletion pattern from HAR file...")
    
    try:
        with open("charles_session.chls/clubos_calendar_flow.har", "r", encoding="utf-8") as f:
            har_data = json.load(f)
        
        # Find the working deletion request
        for entry in har_data["log"]["entries"]:
            if (entry["request"]["method"] == "POST" and 
                "/action/EventPopup/remove" in entry["request"]["url"]):
                
                print("✅ Found working deletion request!")
                
                # Extract the pattern
                headers = {h["name"]: h["value"] for h in entry["request"]["headers"]}
                
                # Parse form data
                form_data = {}
                if "postData" in entry["request"] and "params" in entry["request"]["postData"]:
                    for param in entry["request"]["postData"]["params"]:
                        form_data[param["name"]] = param["value"]
                
                print(f"📋 Found {len(form_data)} form fields in working request")
                
                # Show the PATTERN (not exact values)
                required_fields = list(form_data.keys())
                print("🎯 Required form fields pattern:")
                for field in required_fields:
                    if "id" in field.lower():
                        print(f"   {field}: <EVENT_ID>")
                    elif field in ["_sourcePage", "__fp"]:
                        print(f"   {field}: <FRESH_TOKEN>")
                    else:
                        print(f"   {field}: <DYNAMIC_VALUE>")
                
                return {
                    "required_fields": required_fields,
                    "sample_headers": headers,
                    "pattern": form_data
                }
        
        print("❌ No deletion request found in HAR file")
        return None
        
    except Exception as e:
        print(f"❌ Error parsing HAR file: {e}")
        return None

def create_fresh_deletion_method(pattern):
    """Create deletion method using the working pattern with fresh data"""
    
    def delete_event_with_fresh_data(api, event_id):
        """Delete event using working pattern with fresh event data"""
        print(f"🗑️  Deleting event {event_id} with fresh form data...")
        
        try:
            # Step 1: Get fresh tokens
            fresh_source_token = api.get_source_page_token()
            fresh_fp_token = api.get_fingerprint_token()
            
            # Step 2: Build form data using the working pattern but with fresh values
            form_data = {}
            
            # Copy the pattern but update with fresh data
            for field_name in pattern["required_fields"]:
                if "calendarEvent.id" in field_name:
                    form_data[field_name] = str(event_id)
                elif "calendarEvent.repeatEvent.calendarEventId" in field_name:
                    form_data[field_name] = str(event_id)
                elif field_name == "_sourcePage":
                    form_data[field_name] = fresh_source_token
                elif field_name == "__fp":
                    form_data[field_name] = fresh_fp_token
                else:
                    # Use the pattern value but this should be dynamic based on actual event
                    form_data[field_name] = pattern["pattern"].get(field_name, "")
            
            print(f"📝 Built form data with {len(form_data)} fields for event {event_id}")
            
            # Step 3: Use the working headers pattern
            headers = {
                'Authorization': f'Bearer {api.get_bearer_token()}',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://anytime.club-os.com/action/Calendar',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Origin': 'https://anytime.club-os.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Step 4: Send the deletion request
            response = api.session.post(
                f"{api.base_url}/action/EventPopup/remove",
                headers=headers,
                data=form_data
            )
            
            print(f"📡 Deletion response: {response.status_code}")
            print(f"📄 Response preview: {response.text[:200]}...")
            
            if response.status_code == 200 and "Something isn't right" not in response.text:
                return True
            else:
                print(f"❌ Deletion failed: {response.text[:500]}")
                return False
                
        except Exception as e:
            print(f"❌ Error in deletion: {e}")
            return False
    
    return delete_event_with_fresh_data

def main():
    print("🎯 IMPLEMENTING WORKING DELETION WITH FRESH DATA")
    print("=" * 60)
    
    # Parse the working pattern
    pattern = parse_working_deletion_pattern()
    if not pattern:
        print("❌ Could not extract working pattern")
        return
    
    # Create the fresh deletion method
    delete_with_fresh_data = create_fresh_deletion_method(pattern)
    
    # Test with authentication
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful!")
    
    # Get current events
    events = api.get_jeremy_mayo_events()
    print(f"📅 Found {len(events)} total events")
    
    if len(events) == 0:
        print("❌ No events to test deletion on")
        return
    
    # Test deletion on the first event
    test_event = events[0]
    print(f"\n🧪 Testing fresh deletion on event {test_event.id}")
    
    # Count before deletion
    events_before = len(events)
    
    # Attempt deletion with fresh data
    success = delete_with_fresh_data(api, test_event.id)
    
    if success:
        print("✅ Deletion request completed successfully!")
        
        # Verify actual deletion
        events_after = api.get_jeremy_mayo_events()
        events_after_count = len(events_after)
        
        print(f"📊 Events before: {events_before}, after: {events_after_count}")
        
        if events_after_count < events_before:
            print("🎉 SUCCESS! Event actually deleted from calendar!")
            print("✅ Fresh deletion method is working!")
        else:
            print("❌ Event count unchanged - still fake deletion")
    else:
        print("❌ Deletion request failed")

if __name__ == "__main__":
    main()
