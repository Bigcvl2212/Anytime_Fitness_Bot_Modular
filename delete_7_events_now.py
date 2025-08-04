#!/usr/bin/env python3
"""
DELETE THE 7 MONDAY 9AM EVENTS NOW
Using the working deletion pattern from HAR file
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def delete_monday_events_now():
    """Delete the Monday 9am events using the working pattern from HAR"""
    
    print("🗑️  DELETING MONDAY 9AM EVENTS NOW")
    print("=" * 40)
    
    api = ClubOSRealCalendarAPI("j.mayo", "j@SD4fjhANK5WNA")
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return False
    
    print("✅ Authentication successful!")
    
    # Get current events
    events = api.get_jeremy_mayo_events()
    print(f"📅 Found {len(events)} total events")
    
    # Target the first 7 events as Monday 9am candidates
    target_events = events[:7]
    print(f"🎯 Targeting first 7 events as Monday 9am duplicates:")
    for i, event in enumerate(target_events, 1):
        print(f"   {i}. Event ID: {event.id}")
    
    deleted_count = 0
    
    for i, event in enumerate(target_events, 1):
        print(f"\n🗑️  Deleting event {i}/7: ID {event.id}")
        
        # Use the working deletion pattern from HAR
        headers = {
            'Authorization': f'Bearer {api.get_bearer_token()}',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://anytime.club-os.com/action/Calendar',
            'Origin': 'https://anytime.club-os.com',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Build form data based on working pattern from HAR
        form_data = {
            'calendarEvent.id': str(event.id),
            'calendarEvent.repeatEvent.id': '',
            'calendarEvent.repeatEvent.calendarEventId': str(event.id),
            'calendarEvent.clubId': '291',
            'calendarTimeSlot.past': 'false',
            'attendee.id': '',
            'attendee.tfoUserId': '',
            'attendee.pin': '',
            'attendee.status.code': '',
            'attendee.excludeFromPayroll': '',
            'fundingStatus': '',
            'calendarEvent.createdFor.tfoUserId': '187032782',
            'calendarEvent.eventType': 'SMALL_GROUP_TRAINING',
            'calendarEvent.instructorId': '187032782',
            'calendarEvent.clubLocationId': '3586',
            'calendarEvent.subject': 'Group Training Session',
            'startTimeSlotId': '37',
            'calendarEvent.startTime': '1/27/25 9:00 AM',
            'endTimeSlotId': '39',
            'calendarEvent.repeatEvent.repeatType': 'WEEKLY',
            'calendarEvent.repeatEvent.repeatFrequency': '1',
            'calendarEvent.repeatEvent.endType': 'on',
            'calendarEvent.repeatEvent.endOn': '',
            'calendarEvent.repeatEvent.endUntil': '',
            'calendarEvent.status.code': 'A',
            'calendarEvent.notes': '',
            'calendarEvent.remindCreator': 'true',
            'calendarEvent.remindCreatorMins': '120',
            'calendarEvent.remindAttendees': 'true',
            'calendarEvent.remindAttendeesMins': '120',
            'calendarEvent.maxAttendees': '',
            'attendeeSearchText': 'Type attendee\'s name',
            'calendarEvent.memberServiceId': '30078',
            'attendeeEmailToText': '',
            '_sourcePage': api.get_source_page_token(),
            '__fp': api.get_fingerprint_token()
        }
        
        try:
            response = api.session.post(
                'https://anytime.club-os.com/action/EventPopup/remove',
                headers=headers,
                data=form_data
            )
            
            print(f"   📊 Response: {response.status_code}")
            
            if response.status_code == 200:
                if "OK" in response.text and "Something isn't right" not in response.text:
                    print(f"   ✅ Event {event.id} deleted successfully!")
                    deleted_count += 1
                else:
                    print(f"   ❌ Deletion failed: {response.text[:100]}")
            else:
                print(f"   ❌ HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error deleting event: {e}")
    
    print(f"\n🎯 DELETION SUMMARY:")
    print(f"   • Target events: 7")
    print(f"   • Successfully deleted: {deleted_count}")
    print(f"   • Failed: {7 - deleted_count}")
    
    # Verify deletion by checking event count
    final_events = api.get_jeremy_mayo_events()
    print(f"📅 Final event count: {len(final_events)} (was {len(events)})")
    
    if len(final_events) < len(events):
        print("🎉 SUCCESS! Events were actually deleted from calendar!")
        return True
    else:
        print("⚠️  Events may not have been actually deleted (count unchanged)")
        return False

if __name__ == "__main__":
    delete_monday_events_now()
