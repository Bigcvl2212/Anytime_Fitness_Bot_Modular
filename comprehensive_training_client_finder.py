import sys
import os
import csv
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services'))

from api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

# Import ClubOS APIs
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_integration_fixed import RobustClubOSClient
from clubos_training_api import ClubOSTrainingPackageAPI
from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD

def main():
    client = ClubHubAPIClient()
    if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
        print("❌ ClubHub authentication failed")
        return

    print("✅ ClubHub authenticated")
    
    # Initialize ClubOS APIs
    clubos_client = RobustClubOSClient(CLUBOS_USERNAME, CLUBOS_PASSWORD)
    training_api = ClubOSTrainingPackageAPI()
    
    if not (clubos_client.authenticate() and training_api.authenticate()):
        print("❌ ClubOS authentication failed")
        return
        
    print("✅ ClubOS APIs authenticated and ready")
    
    # Load CSV data for ID mapping
    print("📋 Loading CSV data for ID mapping...")
    csv_data = {}
    csv_file_path = r"c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\data\csv_exports\master_contact_list_with_agreements_20250722_180712.csv"
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Use ClubHub ID as key for mapping
                clubhub_id = row.get('id', '').strip()
                if clubhub_id:
                    csv_data[clubhub_id] = {
                        'agreement_agreementID': row.get('agreement_agreementID', '').strip(),
                        'userId': row.get('userId', '').strip(),
                        'agreementHistory_memberId': row.get('agreementHistory_memberId', '').strip(),
                        'firstName': row.get('firstName', '').strip(),
                        'lastName': row.get('lastName', '').strip(),
                        'email': row.get('email', '').strip()
                    }
        print(f"✅ Loaded {len(csv_data)} CSV records for ID mapping")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    # Get all ClubHub members
    print("🔍 Fetching all ClubHub members...")
    all_members = []
    page = 1
    while page <= 10:  # Increase page limit to be safe
        members = client.get_all_members(page=page, page_size=100)
        if not members:
            break
        all_members.extend(members)
        page += 1
    
    print(f"📋 Total ClubHub members retrieved: {len(all_members)}")
    
    # Find all training clients using CSV ID mapping
    print(f"\n=== FINDING ALL TRAINING CLIENTS USING CSV ID MAPPING ===")
    
    training_clients = []
    members_with_csv_data = 0
    api_calls_made = 0
    
    for i, member in enumerate(all_members):
        clubhub_id = str(member.get('id', ''))
        member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
        
        if i % 50 == 0:  # Progress update every 50 members
            print(f"📊 Progress: {i+1}/{len(all_members)} members checked, {len(training_clients)} training clients found so far...")
        
        # Check if we have CSV data for this member
        if clubhub_id in csv_data:
            members_with_csv_data += 1
            csv_member = csv_data[clubhub_id]
            
            # Try the working ID fields in order of preference
            test_ids = [
                ('agreement_agreementID', csv_member['agreement_agreementID']),
                ('userId', csv_member['userId']),
                ('clubhub_id', clubhub_id),  # Direct ClubHub ID
                ('agreementHistory_memberId', csv_member['agreementHistory_memberId'])
            ]
            
            training_status_found = False
            
            for id_type, test_id in test_ids:
                if not test_id or test_id == '0' or test_id == '':  # Skip empty, zero, or blank IDs
                    continue
                    
                try:
                    api_calls_made += 1
                    payment_status = training_api.get_member_payment_status(test_id)
                    
                    if payment_status and str(payment_status).strip():  # Make sure payment_status is not empty
                        training_clients.append({
                            'name': member_name,
                            'clubhub_id': clubhub_id,
                            'clubos_id': test_id,
                            'id_type': id_type,
                            'payment_status': payment_status,
                            'email': csv_member.get('email', member.get('email', 'N/A'))
                        })
                        
                        status_emoji = "✅" if 'current' in str(payment_status).lower() else "⚠️"
                        print(f"   {status_emoji} TRAINING CLIENT: {member_name} ({id_type}: {test_id}) - {payment_status}")
                        training_status_found = True
                        break  # Found training data, no need to try other IDs
                        
                except Exception as e:
                    # Debug: Show errors for known members
                    if 'dennis' in member_name.lower() or 'jordan' in member_name.lower():
                        print(f"   ⚠️ Error testing {member_name} with {id_type} ({test_id}): {str(e)}")
                    pass
    
    # Results summary
    print(f"\n=== COMPREHENSIVE TRAINING CLIENT DISCOVERY RESULTS ===")
    print(f"Total ClubHub members: {len(all_members)}")
    print(f"Members with CSV data: {members_with_csv_data}")
    print(f"API calls made to ClubOS: {api_calls_made}")
    print(f"Training clients found: {len(training_clients)}")
    
    # Group by payment status
    status_groups = {}
    for client in training_clients:
        status = client['payment_status']
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(client)
    
    print(f"\n📊 Training clients by status:")
    for status, clients in status_groups.items():
        print(f"   {status}: {len(clients)} members")
    
    # Group by ID type used
    id_type_groups = {}
    for client in training_clients:
        id_type = client['id_type']
        if id_type not in id_type_groups:
            id_type_groups[id_type] = []
        id_type_groups[id_type].append(client)
    
    print(f"\n🔍 Success by ID mapping type:")
    for id_type, clients in id_type_groups.items():
        print(f"   {id_type}: {len(clients)} members")
        
    # Show all current training clients
    current_clients = [c for c in training_clients if 'current' in str(c['payment_status']).lower()]
    print(f"\n=== CURRENT TRAINING CLIENTS ({len(current_clients)}) ===")
    for client in current_clients:
        print(f"✅ {client['name']} - {client['payment_status']} (ClubOS ID: {client['clubos_id']}, Type: {client['id_type']})")
        
    # Show other status training clients
    other_clients = [c for c in training_clients if 'current' not in str(c['payment_status']).lower()]
    if other_clients:
        print(f"\n=== OTHER STATUS TRAINING CLIENTS ({len(other_clients)}) ===")
        for client in other_clients:
            print(f"⚠️ {client['name']} - {client['payment_status']} (ClubOS ID: {client['clubos_id']}, Type: {client['id_type']})")

if __name__ == "__main__":
    main()
