#!/usr/bin/env python3
"""Test script to debug ClubOS API issues."""

from clubos_training_api import ClubOSTrainingPackageAPI

def main():
    print("🧪 Testing ClubOS Training API...")
    
    # Create API instance
    api = ClubOSTrainingPackageAPI()
    
    # Test authentication
    print("🔐 Attempting authentication...")
    ok = api.authenticate()
    print(f"✅ Authentication: {ok}")
    
    if not ok:
        print("❌ Authentication failed, cannot continue")
        return
    
    # Test fetching assignees
    print("📋 Fetching assignees...")
    try:
        assignees = api.fetch_assignees(force_refresh=True)
        print(f"✅ Found {len(assignees)} assignees")
        
        if assignees:
            print("📝 Sample assignee:")
            print(f"   ID: {assignees[0].get('id')}")
            print(f"   Name: {assignees[0].get('name')}")
            print(f"   Email: {assignees[0].get('email')}")
        
    except Exception as e:
        print(f"❌ Error fetching assignees: {e}")
        import traceback
        traceback.print_exc()
    
    # Test agreement discovery for first assignee
    if assignees:
        first_id = assignees[0].get('id')
        print(f"\n🔍 Testing agreement discovery for member {first_id}...")
        try:
            agreements = api.discover_member_agreement_ids(first_id)
            print(f"✅ Found {len(agreements)} agreement IDs: {agreements}")
        except Exception as e:
            print(f"❌ Error discovering agreements: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
