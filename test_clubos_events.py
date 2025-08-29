#!/usr/bin/env python3
"""
Test ClubOS integration events methods directly
"""

import sys
import os
sys.path.append('src')

from src.services.clubos_integration import ClubOSIntegration

def test_clubos_events():
    """Test ClubOS events methods directly"""
    print("🔄 Testing ClubOS integration events methods...")
    
    try:
        # Create ClubOS integration instance
        clubos = ClubOSIntegration()
        
        print("\n📅 Testing get_live_events()...")
        live_events = clubos.get_live_events()
        print(f"Live events count: {len(live_events)}")
        if live_events:
            print(f"First event: {live_events[0]}")
        
        print("\n📅 Testing get_todays_events_lightweight()...")
        today_events = clubos.get_todays_events_lightweight()
        print(f"Today's events count: {len(today_events)}")
        if today_events:
            print(f"First event: {today_events[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ClubOS events: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_clubos_events()
    if success:
        print("\n✅ ClubOS events test completed!")
    else:
        print("\n❌ ClubOS events test failed!")
