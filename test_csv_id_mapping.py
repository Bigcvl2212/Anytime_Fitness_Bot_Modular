import sys
import os
import csv
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services'))

from api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

# Import ClubOS APIs
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI

print("🧪 Testing CSV ID mapping for training client discovery")
print("=" * 60)

# Read the CSV file to create ID mappings
csv_file = r"c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\data\csv_exports\master_contact_list_with_agreements_20250722_180712.csv"

clubhub_to_agreement_id = {}
clubhub_to_user_id = {}
clubhub_to_agreement_member_id = {}

try:
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clubhub_id = row.get('id', '').strip()
            agreement_id = row.get('agreement_agreementID', '').strip()
            user_id = row.get('userId', '').strip()
            agreement_member_id = row.get('agreementHistory_memberId', '').strip()
            
            if clubhub_id:
                if agreement_id:
                    clubhub_to_agreement_id[clubhub_id] = agreement_id
                if user_id:
                    clubhub_to_user_id[clubhub_id] = user_id
                if agreement_member_id:
                    clubhub_to_agreement_member_id[clubhub_id] = agreement_member_id
    
    print(f"📄 CSV loaded successfully")
    print(f"   Agreement ID mappings: {len(clubhub_to_agreement_id)}")
    print(f"   User ID mappings: {len(clubhub_to_user_id)}")
    print(f"   Agreement Member ID mappings: {len(clubhub_to_agreement_member_id)}")
    
except Exception as e:
    print(f"❌ Error loading CSV: {e}")
    exit(1)

# Initialize APIs
client = ClubHubAPIClient()
training_api = ClubOSTrainingPackageAPI()

if client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD) and training_api.authenticate():
    print("✅ All APIs authenticated")
    
    # Get all ClubHub members
    print("\n🔍 Getting all ClubHub members...")
    all_members = []
    page = 1
    while page <= 6:
        members = client.get_all_members(page=page, page_size=100)
        if not members:
            break
        all_members.extend(members)
        page += 1
    
    print(f"📋 Retrieved {len(all_members)} ClubHub members")
    
    # Test the CSV ID mapping approaches
    training_clients_found = []
    mapping_success_rates = {
        'direct_clubhub_id': {'success': 0, 'total': 0},
        'agreement_id': {'success': 0, 'total': 0},
        'user_id': {'success': 0, 'total': 0},
        'agreement_member_id': {'success': 0, 'total': 0}
    }
    
    print(f"\n🧪 Testing ID mapping approaches on all {len(all_members)} members...")
    
    for i, member in enumerate(all_members):
        clubhub_id = str(member.get('id', ''))
        member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
        
        if i % 50 == 0:  # Progress update every 50 members
            print(f"   Progress: {i+1}/{len(all_members)} members processed...")
        
        member_training_status = None
        working_id_type = None
        working_id = None
        
        # Test approaches in order of expected success based on our findings
        test_approaches = [
            ('agreement_id', clubhub_to_agreement_id.get(clubhub_id)),
            ('user_id', clubhub_to_user_id.get(clubhub_id)),
            ('direct_clubhub_id', clubhub_id),
            ('agreement_member_id', clubhub_to_agreement_member_id.get(clubhub_id))
        ]
        
        for approach_name, test_id in test_approaches:
            if not test_id:
                continue
                
            mapping_success_rates[approach_name]['total'] += 1
            
            try:
                payment_status = training_api.get_member_payment_status(test_id)
                if payment_status:
                    mapping_success_rates[approach_name]['success'] += 1
                    
                    if not member_training_status:  # Only record the first successful approach
                        member_training_status = payment_status
                        working_id_type = approach_name
                        working_id = test_id
                        
            except Exception:
                pass  # Continue to next approach
        
        # If we found training data, record this member
        if member_training_status:
            training_clients_found.append({
                'name': member_name,
                'clubhub_id': clubhub_id,
                'working_id_type': working_id_type,
                'working_id': working_id,
                'payment_status': member_training_status
            })
    
    print(f"\n🎉 TRAINING CLIENT DISCOVERY COMPLETE!")
    print(f"=" * 60)
    print(f"📊 Found {len(training_clients_found)} training clients out of {len(all_members)} members")
    
    # Show mapping success rates
    print(f"\n📈 ID Mapping Success Rates:")
    for approach, stats in mapping_success_rates.items():
        if stats['total'] > 0:
            success_rate = (stats['success'] / stats['total']) * 100
            print(f"   {approach}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
    
    # Show found training clients
    print(f"\n✅ Training Clients Found:")
    current_clients = []
    other_status_clients = []
    
    for client_data in training_clients_found:
        status = client_data['payment_status']
        if 'current' in str(status).lower():
            current_clients.append(client_data)
        else:
            other_status_clients.append(client_data)
    
    print(f"\n🟢 CURRENT Training Clients ({len(current_clients)}):")
    for client_data in current_clients:
        print(f"   ✅ {client_data['name']} - {client_data['payment_status']} (via {client_data['working_id_type']})")
    
    if other_status_clients:
        print(f"\n🟡 Other Status Training Clients ({len(other_status_clients)}):")
        for client_data in other_status_clients:
            print(f"   ⚠️ {client_data['name']} - {client_data['payment_status']} (via {client_data['working_id_type']})")
    
    print(f"\n🎯 SUMMARY:")
    print(f"   Total Members: {len(all_members)}")
    print(f"   Training Clients: {len(training_clients_found)} ({(len(training_clients_found)/len(all_members)*100):.1f}%)")
    print(f"   Current Status: {len(current_clients)}")
    print(f"   Other Status: {len(other_status_clients)}")

else:
    print("❌ Authentication failed")
