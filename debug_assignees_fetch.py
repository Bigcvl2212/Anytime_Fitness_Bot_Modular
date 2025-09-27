#!/usr/bin/env python3
"""
Debug script to test ClubOS assignees fetching directly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
import logging

# Import credentials from the correct location
try:
    from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD
except ImportError:
    print("❌ Could not import ClubOS credentials")
    print("Please check that config/clubhub_credentials.py exists")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("=== CLUBOS ASSIGNEES FETCH DEBUG ===")
    print("This will test the assignees fetching directly")
    print()
    
    # Initialize ClubOS API (no parameters needed)
    clubos_api = ClubOSTrainingPackageAPI()
    
    print("🔐 Authenticating to ClubOS...")
    if not clubos_api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    print()
    
    print("🔍 Testing assignees fetch (force refresh)...")
    assignees = clubos_api.fetch_assignees(force_refresh=True)
    
    print(f"📊 Results:")
    print(f"   - Found {len(assignees)} assignees")
    
    if assignees:
        print(f"   - First 3 assignees:")
        for i, assignee in enumerate(assignees[:3]):
            print(f"     {i+1}. {assignee}")
            print(f"        Available keys: {list(assignee.keys())}")
    else:
        print("   - ❌ NO ASSIGNEES FOUND")
        print("   - Check debug files for more info:")
        print("     * debug_assignees_ajax.txt")
        print("     * debug_assignees_ajax_retry.txt")
        print("     * debug_assignees_page.html (if HTML parsing was used)")
    
    print()
    print("=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    main()