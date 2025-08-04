#!/usr/bin/env python3
"""
Test the existing calendar methods in ClubOSIntegration
"""

from clubos_integration_fixed import ClubOSIntegration
from datetime import datetime, timedelta

def main():
    print("=== Testing ClubOS Calendar Methods ===")
    
    # Initialize ClubOS connection
    clubos = ClubOSIntegration()
    
    # Connect using the working authentication
    print("🔐 Connecting to ClubOS...")
    if not clubos.connect():
        print("❌ Failed to connect to ClubOS")
        return
    
    print("✅ Connected to ClubOS successfully!")
    
    # Test today's calendar
    print("\n📅 Testing calendar methods...")
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"\n1. Testing get_real_calendar_data() for today ({today}):")
    calendar_data = clubos.get_real_calendar_data(today)
    print(f"   Found {len(calendar_data)} events")
    for event in calendar_data[:3]:  # Show first 3 events
        print(f"   - {event}")
    
    print(f"\n2. Testing client.get_calendar_data() for today ({today}):")
    client_calendar_data = clubos.client.get_calendar_data(today)
    print(f"   Found {len(client_calendar_data)} events")
    for event in client_calendar_data[:3]:  # Show first 3 events
        print(f"   - {event}")
    
    print(f"\n3. Testing get_real_calendar_data() for tomorrow ({tomorrow}):")
    tomorrow_data = clubos.get_real_calendar_data(tomorrow)
    print(f"   Found {len(tomorrow_data)} events")
    for event in tomorrow_data[:3]:  # Show first 3 events
        print(f"   - {event}")
    
    print("\n4. Testing calendar data without date (default to today):")
    default_data = clubos.get_real_calendar_data()
    print(f"   Found {len(default_data)} events")
    for event in default_data[:3]:  # Show first 3 events
        print(f"   - {event}")

if __name__ == "__main__":
    main()
