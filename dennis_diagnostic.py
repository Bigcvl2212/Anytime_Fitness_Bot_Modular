import sys
import os
import csv
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services'))

from api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

# Import ClubOS APIs
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI
from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD

def main():
    print("🔍 DEEP DIAGNOSTIC: What's really happening with Dennis's data?")
    print("=" * 70)
    
    # Authenticate
    client = ClubHubAPIClient()
    training_api = ClubOSTrainingPackageAPI()
    
    if not (client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD) and training_api.authenticate()):
        print("❌ Authentication failed")
        return
    
    print("✅ APIs authenticated")
    
    # Load CSV to get Dennis's various IDs
    csv_file_path = r"c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\data\csv_exports\master_contact_list_with_agreements_20250722_180712.csv"
    dennis_csv_data = None
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if 'DENNIS' in row.get('firstName', '').upper() and 'ROST' in row.get('lastName', '').upper():
                dennis_csv_data = row
                break
    
    if not dennis_csv_data:
        print("❌ Dennis not found in CSV")
        return
        
    print(f"📄 Dennis's CSV data:")
    for key, value in dennis_csv_data.items():
        if 'id' in key.lower() or key in ['firstName', 'lastName', 'email']:
            print(f"   {key}: {value}")
    
    # Get Dennis from ClubHub
    all_members = []
    for page in range(1, 4):
        members = client.get_all_members(page=page, page_size=100)
        if not members:
            break
        all_members.extend(members)
    
    dennis_clubhub = None
    for member in all_members:
        if 'DENNIS' in member.get('firstName', '').upper() and 'ROST' in member.get('lastName', '').upper():
            dennis_clubhub = member
            break
    
    if dennis_clubhub:
        print(f"\n👤 Dennis's ClubHub data:")
        print(f"   ID: {dennis_clubhub.get('id')}")
        print(f"   Name: {dennis_clubhub.get('firstName')} {dennis_clubhub.get('lastName')}")
        print(f"   Email: {dennis_clubhub.get('email')}")
        print(f"   Status: {dennis_clubhub.get('membershipStatus')}")
    
    # Now test ALL possible IDs for Dennis and see what data we get
    print(f"\n🔬 DETAILED TESTING - Dennis's Payment Status for ALL IDs:")
    print("-" * 60)
    
    test_ids = [
        ("ClubHub ID", dennis_clubhub.get('id') if dennis_clubhub else None),
        ("CSV agreement_agreementID", dennis_csv_data.get('agreement_agreementID')),
        ("CSV userId", dennis_csv_data.get('userId')),
        ("CSV agreementHistory_memberId", dennis_csv_data.get('agreementHistory_memberId')),
        ("Known working Jordan ID (test)", "160402199"),  # This should work for Jordan
        ("Known working Jordan agreement ID (test)", "47280095")  # This should work for Jordan
    ]
    
    for description, test_id in test_ids:
        if not test_id or test_id == '0':
            print(f"⏭️ {description}: Skipping (empty/zero)")
            continue
            
        print(f"\n🔍 Testing {description}: {test_id}")
        
        try:
            # Get payment status
            payment_status = training_api.get_member_payment_status(test_id)
            
            if payment_status:
                print(f"   📊 Payment Status: {payment_status}")
                print(f"   📊 Status Type: {type(payment_status)}")
                print(f"   📊 Status String: '{str(payment_status)}'")
                
                # Try to get more detailed info if possible
                try:
                    # Check if the API has other methods to get member details
                    if hasattr(training_api, 'get_member_details'):
                        details = training_api.get_member_details(test_id)
                        print(f"   📋 Member Details: {details}")
                except:
                    pass
                    
                # Check if this might be someone else's data
                if 'current' in str(payment_status).lower():
                    print(f"   ⚠️ WARNING: Shows 'Current' - but Dennis should NOT be current!")
                    print(f"   ⚠️ This might be the wrong person's data!")
                
            else:
                print(f"   ❌ No payment status returned")
                
        except Exception as e:
            print(f"   ⚠️ Error: {str(e)}")
    
    print(f"\n🤔 ANALYSIS:")
    print(f"If Dennis is NOT current on training payments, but we're seeing 'Current' status,")
    print(f"it could mean:")
    print(f"1. 🆔 ID collision - these IDs belong to someone else")
    print(f"2. 📊 Cached/stale data in ClubOS API")
    print(f"3. 🔄 Different meaning of 'Current' (maybe membership, not training)")
    print(f"4. 🐛 API bug or wrong endpoint")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"1. Verify Dennis's actual training payment status manually in ClubOS")
    print(f"2. Check if these IDs might belong to other members")
    print(f"3. Test with a few more known members to see if we're getting correct data")

if __name__ == "__main__":
    main()
