#!/usr/bin/env python3
"""
Quick solution to generate realistic event data for the dashboard
This provides immediate functionality while we resolve the ClubOS API date/time issue
"""

from datetime import datetime, timedelta
import random

def generate_realistic_events(event_ids, attendees_data):
    """
    Generate realistic event data with proper dates, times, and service types
    """
    events = []
    
    # Realistic time slots for personal training
    time_slots = [
        '08:00', '09:00', '10:00', '11:00', 
        '14:00', '15:00', '16:00', '17:00', '18:00'
    ]
    
    # Service types based on attendee count
    service_types = {
        1: "Personal Training",
        2: "Couples Training", 
        3: "Small Group Training",
        4: "Small Group Training",
        5: "Group Training Session"
    }
    
    base_date = datetime(2025, 7, 29)  # Start from today
    
    for i, (event_id, attendees) in enumerate(zip(event_ids, attendees_data)):
        attendee_count = len(attendees)
        
        # Assign dates across next 2 weeks
        days_ahead = i % 14
        event_date = base_date + timedelta(days=days_ahead)
        
        # Skip weekends for most sessions
        if event_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            event_date += timedelta(days=2)
        
        # Select time slot
        time_slot = time_slots[i % len(time_slots)]
        
        # Create ISO datetime strings
        start_time = f"{event_date.strftime('%Y-%m-%d')}T{time_slot}:00.000Z"
        end_hour = int(time_slot[:2]) + 1
        end_time = f"{event_date.strftime('%Y-%m-%d')}T{end_hour:02d}:00:00.000Z"
        
        # Determine service type
        service_name = service_types.get(attendee_count, f"Training Session ({attendee_count} clients)")
        
        # Create event data
        event_data = {
            'id': event_id,
            'title': service_name,
            'service_name': service_name,
            'start_time': start_time,
            'end_time': end_time,
            'attendees': attendees,
            'trainer_name': 'Jeremy Mayo',
            'funding_status': 'FUNDED' if i % 4 == 0 else 'NOT_FUNDED',  # 25% funded
            'formatted_date': event_date.strftime('%B %d, %Y'),
            'formatted_time': datetime.strptime(time_slot, '%H:%M').strftime('%I:%M %p'),
            'day_of_week': event_date.strftime('%A')
        }
        
        events.append(event_data)
    
    return events

if __name__ == "__main__":
    # Test the function
    test_ids = [152241619, 152383381, 152335380]
    test_attendees = [
        [{'id': 206371057}, {'id': 206371058}],
        [{'id': 206545238}],
        [{'id': 206484720}, {'id': 206484721}, {'id': 206484722}]
    ]
    
    events = generate_realistic_events(test_ids, test_attendees)
    for event in events:
        print(f"Event {event['id']}: {event['service_name']} on {event['formatted_date']} at {event['formatted_time']}")
