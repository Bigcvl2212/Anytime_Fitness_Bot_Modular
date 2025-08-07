import sys
import os
import csv
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services'))

from api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

# Import ClubOS APIs
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI

print("🔍 DEBUG: Testing known training clients Dennis and Jordan")
print("=" * 60)

# Initialize APIs
client = ClubHubAPIClient()
training_api = ClubOSTrainingPackageAPI()

if client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD) and training_api.authenticate():
    print("✅ APIs authenticated")
    
    # Test the known working IDs directly
    print("\n🧪 Testing known working IDs:")
    
    test_cases = [
        ("Dennis ClubHub ID", "65828815"),
        ("Dennis agreement_agreementID", "96530079"),
        ("Dennis userId", "31489560"),
        ("Jordan Known ClubOS ID", "160402199"),
        ("Jordan agreement_agreementID", "47280095"),
        ("Jordan userId", "18092705")
    ]
    
    for name, test_id in test_cases:
        try:
            print(f"\n🔍 Testing {name} ({test_id})...")
            payment_status = training_api.get_member_payment_status(test_id)
            if payment_status:
                print(f"   ✅ SUCCESS: {payment_status}")
            else:
                print(f"   ❌ No training data returned")
        except Exception as e:
            print(f"   ⚠️ Error: {str(e)}")
    
    # Now check if we can find Dennis and Jordan in ClubHub
    print(f"\n🔍 Finding Dennis and Jordan in ClubHub...")
    all_members = []
    page = 1
    while page <= 6:
        members = client.get_all_members(page=page, page_size=100)
        if not members:
            break
        all_members.extend(members)
        page += 1
    
    print(f"📋 Retrieved {len(all_members)} ClubHub members")
    
    dennis = None
    jordan = None
    for member in all_members:
        if 'DENNIS' in member.get('firstName', '').upper() and 'ROST' in member.get('lastName', '').upper():
            dennis = member
        elif 'JORDAN' in member.get('firstName', '').upper() and 'KRUEGER' in member.get('lastName', '').upper():
            jordan = member
    
    if dennis:
        print(f"\n✅ Found Dennis in ClubHub:")
        print(f"   ClubHub ID: {dennis.get('id')}")
        print(f"   Name: {dennis.get('firstName')} {dennis.get('lastName')}")
    else:
        print(f"\n❌ Dennis not found in ClubHub")
        
    if jordan:
        print(f"\n✅ Found Jordan in ClubHub:")
        print(f"   ClubHub ID: {jordan.get('id')}")
        print(f"   Name: {jordan.get('firstName')} {jordan.get('lastName')}")
    else:
        print(f"\n❌ Jordan not found in ClubHub")
    
    # Load CSV data
    print(f"\n📄 Loading CSV data...")
    csv_file = r"c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\data\csv_exports\master_contact_list_with_agreements_20250722_180712.csv"
    
    csv_data = {}
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                clubhub_id = row.get('id', '').strip()
                if clubhub_id:
                    csv_data[clubhub_id] = {
                        'agreement_agreementID': row.get('agreement_agreementID', '').strip(),
                        'userId': row.get('userId', '').strip(),
                        'firstName': row.get('firstName', '').strip(),
                        'lastName': row.get('lastName', '').strip()
                    }
        print(f"✅ Loaded {len(csv_data)} CSV records")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        exit(1)
    
    # Check CSV data for Dennis and Jordan
    if dennis:
        dennis_id = str(dennis.get('id'))
        if dennis_id in csv_data:
            print(f"\n🔍 Dennis CSV data:")
            csv_dennis = csv_data[dennis_id]
            print(f"   agreement_agreementID: {csv_dennis['agreement_agreementID']}")
            print(f"   userId: {csv_dennis['userId']}")
            
            # Test these IDs
            for id_type, test_id in [('agreement_agreementID', csv_dennis['agreement_agreementID']), ('userId', csv_dennis['userId'])]:
                if test_id:
                    try:
                        payment_status = training_api.get_member_payment_status(test_id)
                        if payment_status:
                            print(f"   ✅ {id_type} ({test_id}): {payment_status}")
                        else:
                            print(f"   ❌ {id_type} ({test_id}): No data")
                    except Exception as e:
                        print(f"   ⚠️ {id_type} ({test_id}): Error - {str(e)}")
        else:
            print(f"\n❌ Dennis not found in CSV data")
    
    if jordan:
        jordan_id = str(jordan.get('id'))
        if jordan_id in csv_data:
            print(f"\n🔍 Jordan CSV data:")
            csv_jordan = csv_data[jordan_id]
            print(f"   agreement_agreementID: {csv_jordan['agreement_agreementID']}")
            print(f"   userId: {csv_jordan['userId']}")
            
            # Test these IDs
            for id_type, test_id in [('agreement_agreementID', csv_jordan['agreement_agreementID']), ('userId', csv_jordan['userId'])]:
                if test_id:
                    try:
                        payment_status = training_api.get_member_payment_status(test_id)
                        if payment_status:
                            print(f"   ✅ {id_type} ({test_id}): {payment_status}")
                        else:
                            print(f"   ❌ {id_type} ({test_id}): No data")
                    except Exception as e:
                        print(f"   ⚠️ {id_type} ({test_id}): Error - {str(e)}")
        else:
            print(f"\n❌ Jordan not found in CSV data")

else:
    print("❌ Authentication failed")
