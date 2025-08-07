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

def test_direct_known_ids():
    """Test the exact IDs we know work from previous testing"""
    print("🧪 Testing known working IDs first...")
    
    training_api = ClubOSTrainingPackageAPI()
    if not training_api.authenticate():
        print("❌ ClubOS authentication failed")
        return False
    
    # Test known working IDs from previous successful runs
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
            print(f"🔍 Testing {description} ({test_id})...")
            payment_status = training_api.get_member_payment_status(test_id)
            
            if payment_status:
                status_emoji = "✅" if 'current' in str(payment_status).lower() else "⚠️"
                print(f"   {status_emoji} SUCCESS: {payment_status}")
                working_count += 1
            else:
                print(f"   ❌ No training data")
                
        except Exception as e:
            print(f"   ⚠️ Error: {str(e)}")
    
    print(f"\n📊 Direct ID test results: {working_count}/{len(known_working_ids)} working")
    return working_count > 0

def main():
    # First test direct known IDs to verify API is working
    if not test_direct_known_ids():
        print("❌ Known IDs not working - ClubOS API may have issues")
        return
    
    print(f"\n✅ Known IDs working! Proceeding with CSV mapping test...")
    
    client = ClubHubAPIClient()
    training_api = ClubOSTrainingPackageAPI()
    
    if not (client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD) and training_api.authenticate()):
        print("❌ Authentication failed")
        return

    print("✅ APIs authenticated")
    
    # Load CSV data for ID mapping
    print("📋 Loading CSV data...")
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
    
    # Get just first page of ClubHub members to find our test cases
    print("🔍 Getting ClubHub members (first few pages)...")
    all_members = []
    for page in range(1, 4):  # Just first 3 pages to find Dennis and Jordan
        members = client.get_all_members(page=page, page_size=100)
        if not members:
            break
        all_members.extend(members)
    
    print(f"📋 Retrieved {len(all_members)} members for testing")
    
    # Find known training clients
    known_training_clients = ['DENNIS ROST', 'JORDAN KRUEGER']
    test_members = []
    
    for member in all_members:
        member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".upper()
        if any(name in member_name for name in known_training_clients):
            test_members.append(member)
            print(f"✅ Found test member: {member_name}")
    
    print(f"\n🧪 Testing CSV ID mapping on {len(test_members)} known training clients...")
    
    training_clients = []
    
    for member in test_members:
        clubhub_id = str(member.get('id', ''))
        member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
        
        print(f"\n🔍 Testing: {member_name} (ClubHub ID: {clubhub_id})")
        
        if clubhub_id in csv_data:
            csv_member = csv_data[clubhub_id]
            print(f"   📄 Found in CSV data")
            
            # Try all ID mapping approaches
            test_ids = [
                ('agreement_agreementID', csv_member['agreement_agreementID']),
                ('userId', csv_member['userId']),
                ('clubhub_id', clubhub_id),
                ('agreementHistory_memberId', csv_member['agreementHistory_memberId'])
            ]
            
            for id_type, test_id in test_ids:
                if not test_id or test_id == '0':
                    print(f"   ⏭️ Skipping {id_type}: empty/zero")
                    continue
                    
                try:
                    print(f"   🔍 Testing {id_type} ({test_id})...")
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
                        break  # Found training data, stop trying other IDs
                    else:
                        print(f"   ❌ No training data with {id_type}")
                        
                except Exception as e:
                    print(f"   ⚠️ Error with {id_type}: {str(e)}")
        else:
            print(f"   ❌ Not found in CSV data")
    
    # Results
    print(f"\n=== TEST RESULTS ===")
    print(f"Training clients found: {len(training_clients)}")
    
    for client in training_clients:
        print(f"✅ {client['name']} - {client['payment_status']} (ClubOS ID: {client['clubos_id']}, Type: {client['id_type']})")
    
    if len(training_clients) >= 2:
        print(f"\n🎉 SUCCESS! CSV ID mapping works for known training clients!")
        print(f"\nNow let's think about batch processing optimization:")
        print(f"1. 🚀 Parallel processing: Process multiple members simultaneously")
        print(f"2. 📦 Batch API calls: Group requests to ClubOS")
        print(f"3. 🎯 Smart filtering: Only test members who have CSV data")
        print(f"4. ⚡ Connection pooling: Reuse HTTP connections")
        
        # Calculate estimated time for full run
        csv_members_count = len([m for m in all_members if str(m.get('id', '')) in csv_data])
        print(f"\nEstimated full run:")
        print(f"   Members with CSV data: {csv_members_count} (from {len(all_members)} total)")
        print(f"   Time estimate: ~{csv_members_count * 2} seconds (2s per member)")
        
        # Ask if user wants to proceed with optimized version
        print(f"\nReady to create optimized batch processing version? (Y/n)")
    else:
        print(f"❌ CSV ID mapping not working as expected")

if __name__ == "__main__":
    main()
