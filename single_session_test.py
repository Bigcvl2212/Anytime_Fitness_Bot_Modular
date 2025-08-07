import sys
import os
import csv
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services'))

from api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

# Import ClubOS APIs
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI
from config.clubhub_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD

def main():
    # Use single API instances throughout
    client = ClubHubAPIClient()
    training_api = ClubOSTrainingPackageAPI()
    
    # Authenticate once
    print("🔐 Authenticating APIs...")
    if not (client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD) and training_api.authenticate()):
        print("❌ Authentication failed")
        return
    
    print("✅ All APIs authenticated")
    
    # Test known working IDs first with the SAME API instance
    print("\n🧪 Testing known working IDs with main API instance...")
    known_working_ids = [
        ("Jordan - Known ClubOS ID", "160402199"),
        ("Jordan - agreement_agreementID", "47280095"), 
        ("Jordan - userId", "18092705"),
        ("Dennis - ClubHub ID", "65828815"),
        ("Dennis - agreement_agreementID", "96530079"),
        ("Dennis - userId", "31489560")
    ]
    
    working_count = 0
    for description, test_id in known_working_ids:
        try:
            payment_status = training_api.get_member_payment_status(test_id)
            if payment_status:
                status_emoji = "✅" if 'current' in str(payment_status).lower() else "⚠️"
                print(f"   {status_emoji} {description}: {payment_status}")
                working_count += 1
            else:
                print(f"   ❌ {description}: No data")
        except Exception as e:
            print(f"   ⚠️ {description}: Error - {str(e)}")
    
    if working_count == 0:
        print("❌ Known IDs not working - stopping here")
        return
        
    print(f"✅ {working_count}/{len(known_working_ids)} known IDs working")
    
    # Load CSV data for ID mapping
    print("\n📋 Loading CSV data...")
    csv_data = {}
    csv_file_path = r"c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\data\csv_exports\master_contact_list_with_agreements_20250722_180712.csv"
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            clubhub_id = row.get('id', '').strip()
            if clubhub_id:
                csv_data[clubhub_id] = {
                    'agreement_agreementID': row.get('agreement_agreementID', '').strip(),
                    'userId': row.get('userId', '').strip(),
                    'agreementHistory_memberId': row.get('agreementHistory_memberId', '').strip(),
                    'firstName': row.get('firstName', '').strip(),
                    'lastName': row.get('lastName', '').strip()
                }
    
    print(f"✅ Loaded {len(csv_data)} CSV records")
    
    # Get ClubHub members
    print("\n🔍 Getting ClubHub members...")
    all_members = []
    for page in range(1, 4):
        members = client.get_all_members(page=page, page_size=100)
        if not members:
            break
        all_members.extend(members)
    
    print(f"📋 Retrieved {len(all_members)} members")
    
    # Find known training clients and test with SAME API instance
    test_members = []
    for member in all_members:
        member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".upper()
        if 'DENNIS ROST' in member_name or 'JORDAN KRUEGER' in member_name:
            test_members.append(member)
            print(f"✅ Found test member: {member_name}")
    
    print(f"\n🧪 Testing CSV ID mapping with SAME API instance...")
    
    training_clients = []
    
    for member in test_members:
        clubhub_id = str(member.get('id', ''))
        member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
        
        print(f"\n🔍 Testing: {member_name} (ClubHub ID: {clubhub_id})")
        
        if clubhub_id in csv_data:
            csv_member = csv_data[clubhub_id]
            
            # Test specific IDs we know should work
            test_ids = [
                ('agreement_agreementID', csv_member['agreement_agreementID']),
                ('userId', csv_member['userId']),
                ('clubhub_id', clubhub_id)
            ]
            
            for id_type, test_id in test_ids:
                if not test_id or test_id == '0':
                    continue
                    
                try:
                    print(f"   🔍 Testing {id_type} ({test_id}) with SAME API instance...")
                    payment_status = training_api.get_member_payment_status(test_id)
                    
                    if payment_status:
                        training_clients.append({
                            'name': member_name,
                            'clubhub_id': clubhub_id,
                            'clubos_id': test_id,
                            'id_type': id_type,
                            'payment_status': payment_status
                        })
                        
                        status_emoji = "✅" if 'current' in str(payment_status).lower() else "⚠️"
                        print(f"   {status_emoji} SUCCESS: {payment_status}")
                        break
                    else:
                        print(f"   ❌ No training data")
                        
                except Exception as e:
                    print(f"   ⚠️ Error: {str(e)}")
        else:
            print(f"   ❌ Not found in CSV")
    
    # Results
    print(f"\n=== FINAL RESULTS ===")
    print(f"Training clients found: {len(training_clients)}")
    
    for tc in training_clients:
        print(f"✅ {tc['name']} - {tc['payment_status']} (ClubOS ID: {tc['clubos_id']}, Type: {tc['id_type']})")
    
    if len(training_clients) >= 2:
        print(f"\n🎉 SUCCESS! CSV ID mapping works!")
        
        # Estimate processing time for optimization
        members_with_csv = len([m for m in all_members[:100] if str(m.get('id', '')) in csv_data])
        total_estimated_members = (members_with_csv * 5.31)  # Scale to full 531 members
        
        print(f"\n📊 Batch Processing Analysis:")
        print(f"   Members with CSV data (sample): {members_with_csv}/100")
        print(f"   Estimated total members with CSV data: ~{int(total_estimated_members)}")
        print(f"   Current processing time: ~2 seconds per member")
        print(f"   Total estimated time: ~{int(total_estimated_members * 2 / 60)} minutes")
        
        print(f"\n🚀 Optimization Options:")
        print(f"   1. Parallel processing (4-8 threads): Reduce to ~{int(total_estimated_members * 2 / 60 / 4)}-{int(total_estimated_members * 2 / 60 / 8)} minutes")
        print(f"   2. Smart filtering: Only test members with agreement IDs")
        print(f"   3. Batch requests: Group multiple requests")
        
    else:
        print(f"❌ CSV ID mapping still not working")

if __name__ == "__main__":
    main()
