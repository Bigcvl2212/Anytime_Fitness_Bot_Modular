#!/usr/bin/env python3
"""
Test script to verify past due implementation on dashboard and calendar
"""

import requests
import json
import time

def test_dashboard_events():
    """Test dashboard events with past due information"""
    try:
        print("🔍 Testing dashboard events with past due information...")

        # Make request to dashboard (this will trigger our modified route)
        response = requests.get('http://localhost:5000/', timeout=10)

        if response.status_code == 200:
            print("✅ Dashboard loaded successfully")
            print(f"📄 Response length: {len(response.text)} characters")

            # Check if our past due logic is present in the response
            if 'past_due' in response.text:
                print("✅ Past due information found in dashboard response")
            else:
                print("⚠️ Past due information not found in dashboard response")

        else:
            print(f"❌ Dashboard returned status code: {response.status_code}")

    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")

def test_calendar_events():
    """Test calendar events API with past due information"""
    try:
        print("\n🔍 Testing calendar events API with past due information...")

        # Test calendar events API
        calendar_response = requests.get('http://localhost:5000/api/calendar/events', timeout=10)

        if calendar_response.status_code == 200:
            data = calendar_response.json()
            print(f"✅ Calendar API returned {len(data.get('events', []))} events")

            # Check for past due information in events
            events_with_past_due = 0
            for event in data.get('events', []):
                if event.get('attendees'):
                    for attendee in event['attendees']:
                        if attendee.get('past_due'):
                            events_with_past_due += 1
                            print(f"✅ Found past due attendee: {attendee['name']} - {attendee['past_due']['formatted_amount']}")
                            break

            if events_with_past_due > 0:
                print(f"✅ Found {events_with_past_due} events with past due information")
            else:
                print("ℹ️ No events with past due information found (this may be normal if no training clients have past due amounts)")

        else:
            print(f"❌ Calendar API returned status code: {calendar_response.status_code}")

    except Exception as e:
        print(f"❌ Error testing calendar API: {e}")

def test_training_client_lookup():
    """Test that training client lookup is working"""
    try:
        print("\n🔍 Testing training client database lookup...")

        # Query the database directly to see if we have training clients
        import sqlite3
        import os

        db_path = os.path.join(os.path.dirname(__file__), 'src', 'gym_bot.db')
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM training_clients")
            count = cursor.fetchone()[0]
            print(f"📊 Found {count} training clients in database")

            if count > 0:
                cursor.execute("SELECT member_name, first_name, last_name, member_id FROM training_clients LIMIT 3")
                clients = cursor.fetchall()
                print("👥 Sample training clients:")
                for client in clients:
                    print(f"   - {client[0] or f'{client[1]} {client[2]}'} (ID: {client[3]})")

            conn.close()
        else:
            print("❌ Database file not found")

    except Exception as e:
        print(f"❌ Error testing database: {e}")

if __name__ == "__main__":
    print("🧪 Testing Past Due Implementation")
    print("=" * 50)

    test_training_client_lookup()
    test_dashboard_events()
    test_calendar_events()

    print("\n" + "=" * 50)
    print("✅ Testing completed!")



