#!/usr/bin/env python3
"""Quick script to get assignees list"""

from clubos_training_api import ClubOSTrainingPackageAPI

def main():
    api = ClubOSTrainingPackageAPI()
    if api.authenticate():
        assignees = api.fetch_assignees()
        print(f"📋 Found {len(assignees)} assignees:")
        for i, assignee in enumerate(assignees[:15]):  # Show first 15
            # Print the full assignee dict to see available keys
            if i == 0:
                print(f"📄 Sample assignee structure: {assignee}")
            
            # Try different possible key names
            member_id = assignee.get('member_id') or assignee.get('id') or assignee.get('memberId') or 'Unknown'
            name = assignee.get('name') or assignee.get('full_name') or 'Unknown'
            print(f"  {i+1:2d}. {name} (ID: {member_id})")
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    main()
