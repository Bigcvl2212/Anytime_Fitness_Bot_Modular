from src.ical_calendar_parser import iCalClubOSParser
from datetime import datetime

# Test the iCal parser directly
calendar_url = "https://anytime.club-os.com/CalendarSync/4984a5b2aac135a95b6bc173054e95716b27e6b9"
parser = iCalClubOSParser(calendar_url)
events = parser.get_real_events()

print(f"Total events found: {len(events)}")

# Check date ranges
if events:
    dates = [event.start_time.date() for event in events if event.start_time]
    min_date = min(dates)
    max_date = max(dates)
    
    print(f"Date range: {min_date} to {max_date}")
    
    # Check for events in current week (Aug 25-31)
    current_week_events = []
    for event in events:
        if event.start_time:
            event_date = event.start_time.date()
            if event_date >= datetime(2025, 8, 25).date() and event_date <= datetime(2025, 8, 31).date():
                current_week_events.append(event)
    
    print(f"Events in current week (Aug 25-31): {len(current_week_events)}")
    
    # Show first few current week events
    for i, event in enumerate(current_week_events[:5]):
        print(f"  {i+1}. {event.summary} - {event.start_time}")
    
    # Check for events in July
    july_events = []
    for event in events:
        if event.start_time:
            event_date = event.start_time.date()
            if event_date >= datetime(2025, 7, 1).date() and event_date <= datetime(2025, 7, 31).date():
                july_events.append(event)
    
    print(f"Events in July: {len(july_events)}")
    
    # Show first few July events
    for i, event in enumerate(july_events[:5]):
        print(f"  {i+1}. {event.summary} - {event.start_time}")
