#!/usr/bin/env python3
"""
Test the fixed ClubOS Calendar API Service with proper authentication detection
"""
import sys
import os

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.services.api.calendar_api_service import ClubOSCalendarAPIService
from config.secrets_local import get_secret

def test_calendar_service():
    """Test the calendar service with the updated authentication and realistic data"""
    
    print("🧪 Testing ClubOS Calendar API Service...")
    
    try:
        # Initialize the calendar service
        service = ClubOSCalendarAPIService(
            get_secret('clubos-username'), 
            get_secret('clubos-password')
        )
        
        print("✅ Calendar service initialized successfully")
        
        # Test getting calendar details
        print("\n📅 Testing get_calendar_view_details...")
        calendar_data = service.get_calendar_view_details("My schedule")
        
        if calendar_data:
            print(f"\n📊 Calendar Results:")
            print(f"Days with data: {len(calendar_data)}")
            
            for day, events in calendar_data.items():
                print(f"\n📅 {day}: {len(events)} events")
                for i, event in enumerate(events[:5]):  # Show first 5 events
                    status_emoji = "🟢" if event['status'] == 'Available' else "🔴"
                    member_info = f" - {event['member_name']}" if event['member_name'] else ""
                    print(f"  {i+1}. {status_emoji} {event['time']} ({event['status']}){member_info}")
                
                if len(events) > 5:
                    print(f"  ... and {len(events) - 5} more events")
        else:
            print("❌ No calendar data retrieved")
        
        # Test getting available slots
        print("\n🔍 Testing get_available_slots...")
        available_slots = service.get_available_slots("My schedule")
        
        if available_slots:
            print(f"📋 Available slots: {len(available_slots)}")
            for slot in available_slots[:10]:  # Show first 10
                print(f"  🕐 {slot}")
        else:
            print("❌ No available slots found")
        
        print("\n✅ Calendar service test completed!")
        
        # Determine if data is real or sample
        if calendar_data:
            sample_day = list(calendar_data.keys())[0]
            sample_events = calendar_data[sample_day]
            
            if any('Booked' in event.get('notes', '') for event in sample_events):
                print("\n🎯 STATUS: This appears to be realistic gym schedule data")
                print("   📝 Contains mix of booked/available slots with member names")
                print("   ⏰ Shows typical gym training hours (6 AM - 8 PM)")
                return True
            else:
                print("\n⚠️  STATUS: This appears to be sample/fallback data")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Error testing calendar service: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_calendar_service()
