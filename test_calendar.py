import requests
from datetime import datetime

# Test with July dates where we know there are events
response = requests.get('http://localhost:5000/api/calendar/events?start=2025-07-28&end=2025-08-03')
data = response.json()

print(f"Status: {response.status_code}")
print(f"Events found: {len(data.get('events', []))}")
print(f"Total events: {data.get('total_events', 0)}")

# Show first 5 events
for i, event in enumerate(data.get('events', [])[:5]):
    print(f"  {i+1}. {event.get('title', 'No title')} - {event.get('start_time', 'No time')}")

# Test with current week
print("\n--- Current Week Test ---")
current_week_response = requests.get('http://localhost:5000/api/calendar/events?start=2025-08-25&end=2025-08-31')
current_week_data = current_week_response.json()

print(f"Current week events: {len(current_week_data.get('events', []))}")
for i, event in enumerate(current_week_data.get('events', [])[:5]):
    print(f"  {i+1}. {event.get('title', 'No title')} - {event.get('start_time', 'No time')}")
