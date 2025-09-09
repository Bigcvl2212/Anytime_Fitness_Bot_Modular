import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.clubos_integration import ClubOSIntegration

# Initialize ClubOS integration
clubos = ClubOSIntegration()
clubos.authenticate()

print("Testing get_events_for_date_range method...")

# Test with July dates
events = clubos.get_events_for_date_range('2025-07-28', '2025-08-03')
print(f"July events found: {len(events)}")

# Test with current week
current_events = clubos.get_events_for_date_range('2025-08-25', '2025-08-31')
print(f"Current week events found: {len(current_events)}")

# Test with a broader range
broad_events = clubos.get_events_for_date_range('2025-07-01', '2025-12-31')
print(f"Broad range events found: {len(broad_events)}")

# Show first few events if any
if broad_events:
    print("\nFirst 3 events:")
    for i, event in enumerate(broad_events[:3]):
        print(f"  {i+1}. {event.get('title', 'No title')} - {event.get('start_time', 'No time')}")
else:
    print("No events found in any range!")
