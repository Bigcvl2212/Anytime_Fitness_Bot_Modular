#!/usr/bin/env python3
import os
import sys

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

print("Testing imports...")
try:
    from clubos_training_api_fixed import ClubOSTrainingPackageAPI
    print("✅ ClubOSTrainingPackageAPI imported successfully")
except ImportError as e:
    print(f"❌ ClubOSTrainingPackageAPI import failed: {e}")

try:
    from src.clubos_real_calendar_api import ClubOSRealCalendarAPI  
    print("✅ ClubOSRealCalendarAPI imported successfully")
except ImportError as e:
    print(f"❌ ClubOSRealCalendarAPI import failed: {e}")

try:
    from src.ical_calendar_parser import iCalClubOSParser
    print("✅ iCalClubOSParser imported successfully")
except ImportError as e:
    print(f"❌ iCalClubOSParser import failed: {e}")

try:
    from src.gym_bot_clean import ClubOSEventDeletion
    print("✅ ClubOSEventDeletion imported successfully")
except ImportError as e:
    print(f"❌ ClubOSEventDeletion import failed: {e}")

try:
    from src.clubos_fresh_data_api import ClubOSFreshDataAPI
    print("✅ ClubOSFreshDataAPI imported successfully")
except ImportError as e:
    print(f"❌ ClubOSFreshDataAPI import failed: {e}")

print("All import tests completed!")
