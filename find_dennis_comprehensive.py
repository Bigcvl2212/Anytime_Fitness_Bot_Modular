import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_integration_fixed import RobustClubOSClient
from clubos_training_api import ClubOSTrainingPackageAPI
from config.clubhub_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD

def find_dennis_in_clubos():
    """Try multiple approaches to find Dennis in ClubOS"""
    print("🔍 COMPREHENSIVE SEARCH FOR DENNIS IN CLUBOS")
    print("=" * 50)
    
    # Initialize APIs
    clubos_client = RobustClubOSClient(CLUBOS_USERNAME, CLUBOS_PASSWORD)
    training_api = ClubOSTrainingPackageAPI()
    
    if not (clubos_client.authenticate() and training_api.authenticate()):
        print("❌ ClubOS authentication failed")
        return
        
    print("✅ ClubOS APIs authenticated")
    
    # Method 1: Try name-based search
    print("\n🔍 METHOD 1: Name-based search")
    try:
        dennis_search_results = clubos_client._search_member("Dennis Rost")
        if dennis_search_results:
            print(f"✅ Found Dennis via name search: ID {dennis_search_results}")
            
            # Test this ID for training data
            payment_status = training_api.get_member_payment_status(dennis_search_results)
            if payment_status:
                print(f"✅ FOUND DENNIS'S TRAINING DATA: {payment_status}")
                return dennis_search_results
            else:
                print(f"❌ No training data for found ID")
        else:
            print("❌ Name search returned no results")
    except Exception as e:
        print(f"❌ Name search failed: {e}")
    
    # Method 2: Try variations of Dennis's name
    print("\n🔍 METHOD 2: Name variations")
    name_variations = [
        "DENNIS ROST",
        "Dennis Rost", 
        "ROST, DENNIS",
        "Rost, Dennis",
        "Dennis",
        "ROST"
    ]
    
    for name in name_variations:
        try:
            print(f"   Trying: {name}")
            result = clubos_client._search_member(name)
            if result:
                print(f"   ✅ Found with '{name}': ID {result}")
                payment_status = training_api.get_member_payment_status(result)
                if payment_status:
                    print(f"   ✅ HAS TRAINING DATA: {payment_status}")
                    return result
                else:
                    print(f"   ❌ No training data")
            else:
                print(f"   ❌ No results")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
    
    # Method 3: Try ID variations/ranges around Dennis's ClubHub ID
    print("\n🔍 METHOD 3: ID variations around 65828815")
    base_id = 65828815
    id_variations = [
        str(base_id),  # Exact ClubHub ID
        str(base_id - 1),
        str(base_id + 1),
        str(base_id - 10),
        str(base_id + 10),
        str(base_id - 100),
        str(base_id + 100)
    ]
    
    for test_id in id_variations:
        try:
            print(f"   Testing ID: {test_id}")
            payment_status = training_api.get_member_payment_status(test_id)
            if payment_status:
                print(f"   ✅ FOUND TRAINING DATA with ID {test_id}: {payment_status}")
                return test_id
            else:
                print(f"   ❌ No training data")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
    
    # Method 4: Try to get a list of all training clients and search manually
    print("\n🔍 METHOD 4: Browse all training clients")
    try:
        # Try to get a list of all members with training packages
        print("   Attempting to get list of all training clients...")
        
        # Try different endpoints that might list training clients
        endpoints_to_try = [
            "/api/agreements/package_agreements/list",
            "/api/agreements/package_agreements",
            "/api/members?hasTraining=true",
            "/api/training_clients",
            "/api/members/with_agreements"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                print(f"   Trying endpoint: {endpoint}")
                # This would require accessing the ClubOS API directly
                # For now, let's skip this complex approach
                print(f"   (Endpoint exploration skipped for now)")
            except Exception as e:
                print(f"   Error: {e}")
                
    except Exception as e:
        print(f"   Failed to browse training clients: {e}")
    
    # Method 5: Check if there are other possible ID mappings from CSV
    print("\n🔍 METHOD 5: Check CSV for other Dennis entries")
    import csv
    csv_file_path = r"c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\data\csv_exports\master_contact_list_with_agreements_20250722_180712.csv"
    
    try:
        dennis_entries = []
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'DENNIS' in row.get('firstName', '').upper() and 'ROST' in row.get('lastName', '').upper():
                    dennis_entries.append(row)
        
        print(f"   Found {len(dennis_entries)} Dennis entries in CSV")
        for i, entry in enumerate(dennis_entries):
            print(f"   Entry {i+1}:")
            for key, value in entry.items():
                if 'id' in key.lower():
                    print(f"      {key}: {value}")
                    
                    # Test this ID
                    if value and value != '0':
                        try:
                            payment_status = training_api.get_member_payment_status(value)
                            if payment_status:
                                print(f"      ✅ TRAINING DATA FOUND with {key} ({value}): {payment_status}")
                                return value
                        except:
                            pass
                            
    except Exception as e:
        print(f"   CSV check failed: {e}")
    
    print("\n❌ COULD NOT FIND DENNIS'S TRAINING DATA IN CLUBOS")
    print("This suggests either:")
    print("1. Dennis's training data is under a different ID/name in ClubOS")
    print("2. There's a sync issue between systems")
    print("3. Dennis's training package might be inactive/cancelled in ClubOS")
    print("4. Different ClubOS database/environment than expected")

if __name__ == "__main__":
    find_dennis_in_clubos()
