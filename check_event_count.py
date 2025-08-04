#!/usr/bin/env python3
"""
Quick check of current event count
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI

api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")

if api.authenticate():
    events = api.get_jeremy_mayo_events()
    print(f"✅ Current event count: {len(events)}")
    
    if len(events) < 29:
        print(f"🎉 SUCCESS! Reduced from 29 to {len(events)} events")
        print(f"   Deleted: {29 - len(events)} events")
    else:
        print("⚠️  Event count unchanged - deletion may have been fake")
else:
    print("❌ Authentication failed")
