#!/usr/bin/env python3
"""
Test the existing calendar functionality in the working ClubOS client
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clubos_integration_fixed import RobustClubOSClient
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_existing_calendar_functionality():
    """Test the existing calendar functionality"""
    
    # Load credentials
    try:
        from config.secrets_local import get_secret
        CLUBOS_USERNAME = get_secret("clubos-username")
        CLUBOS_PASSWORD = get_secret("clubos-password")
        
        if not CLUBOS_USERNAME or not CLUBOS_PASSWORD:
            print("❌ Could not load ClubOS credentials")
            return
    except ImportError:
        print("❌ Could not load credentials from config.secrets_local")
        return
    
    print("=== Testing Existing ClubOS Calendar Functionality ===")
    
    # Initialize client with working authentication
    client = RobustClubOSClient(CLUBOS_USERNAME, CLUBOS_PASSWORD)
    
    # Authenticate
    print("🔐 Authenticating with ClubOS...")
    if not client.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful!")
    
    # Test calendar for today
    print("\n=== Testing Calendar for Today ===")
    today = datetime.now().strftime("%Y-%m-%d")
    events_today = client.get_calendar_data(today)
    
    if events_today:
        print(f"📅 Found {len(events_today)} events for {today}:")
        for i, event in enumerate(events_today[:5], 1):  # Show first 5
            print(f"  {i}. {event}")
    else:
        print(f"📅 No events found for {today}")
    
    # Test calendar for tomorrow
    print("\n=== Testing Calendar for Tomorrow ===")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    events_tomorrow = client.get_calendar_data(tomorrow)
    
    if events_tomorrow:
        print(f"📅 Found {len(events_tomorrow)} events for {tomorrow}:")
        for i, event in enumerate(events_tomorrow[:5], 1):  # Show first 5
            print(f"  {i}. {event}")
    else:
        print(f"📅 No events found for {tomorrow}")
    
    # Test calendar for next week
    print("\n=== Testing Calendar for Next Week ===")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    events_next_week = client.get_calendar_data(next_week)
    
    if events_next_week:
        print(f"📅 Found {len(events_next_week)} events for {next_week}:")
        for i, event in enumerate(events_next_week[:5], 1):  # Show first 5
            print(f"  {i}. {event}")
    else:
        print(f"📅 No events found for {next_week}")
    
    # Test if we can check multiple days
    print("\n=== Testing Multiple Days ===")
    total_events = 0
    for i in range(7):  # Check next 7 days
        check_date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        events = client.get_calendar_data(check_date)
        event_count = len(events) if events else 0
        total_events += event_count
        print(f"📅 {check_date}: {event_count} events")
    
    print(f"\n📊 Total events found across 7 days: {total_events}")
    
    if total_events > 0:
        print("\n✅ Calendar API is working! You can now:")
        print("   - Get available slots via API call")
        print("   - View existing events")
        print("   - Build features to add/remove events")
        print("   - Build features to add/remove people from events")
    else:
        print("\n⚠️ No events found - this might mean:")
        print("   - Calendar is empty for the tested dates")
        print("   - API is working but no events are scheduled")
        print("   - Need to test different date ranges")

if __name__ == "__main__":
    test_existing_calendar_functionality()
