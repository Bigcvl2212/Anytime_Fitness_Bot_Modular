import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services'))

from api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

client = ClubHubAPIClient()
if client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
    print("✅ ClubHub authenticated")
    
    # Get all members
    all_members = []
    page = 1
    while page <= 6:
        members = client.get_all_members(page=page, page_size=100)
        if not members:
            break
        all_members.extend(members)
        page += 1
    
    print(f"📋 Total members retrieved: {len(all_members)}")
    
    # Analyze userType distribution
    user_type_counts = {}
    training_candidates = []
    
    for member in all_members:
        user_type = member.get('userType', 'None')
        user_type_counts[user_type] = user_type_counts.get(user_type, 0) + 1
        
        # Collect potential training clients (userType 16 or 17)
        if user_type in [16, 17]:
            name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
            training_candidates.append({
                'name': name,
                'userType': user_type,
                'agreementId': member.get('agreementId'),
                'statusMessage': member.get('statusMessage', ''),
                'contractTypes': member.get('contractTypes', []),
                'rating': member.get('rating', 0)
            })
    
    print("\n=== USER TYPE DISTRIBUTION ===")
    for user_type, count in sorted(user_type_counts.items()):
        print(f"UserType {user_type}: {count} members")
    
    print(f"\n=== POTENTIAL TRAINING CLIENTS (userType 16 or 17) ===")
    print(f"Found {len(training_candidates)} potential training clients:")
    
    for candidate in training_candidates[:20]:  # Show first 20
        print(f"{candidate['name']:<25} | UserType: {candidate['userType']} | Status: {candidate['statusMessage']:<20} | Agreement: {candidate['agreementId']}")
    
    if len(training_candidates) > 20:
        print(f"... and {len(training_candidates) - 20} more")
        
    # Count by status for training candidates
    print(f"\n=== TRAINING CLIENT STATUS BREAKDOWN ===")
    status_counts = {}
    for candidate in training_candidates:
        status = candidate['statusMessage'] or 'No Status'
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in sorted(status_counts.items()):
        print(f"{status}: {count}")
        
else:
    print("❌ Authentication failed")
