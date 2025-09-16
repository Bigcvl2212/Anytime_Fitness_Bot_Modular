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

client = ClubHubAPIClient()
if client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
    print("✅ ClubHub authenticated")
    
    # Initialize ClubOS client for member search
    clubos_client = RobustClubOSClient(CLUBOS_USERNAME, CLUBOS_PASSWORD)
    
    # Initialize ClubOS training API for payment status
    training_api = ClubOSTrainingPackageAPI()
    
    # Authenticate both
    if clubos_client.authenticate() and training_api.authenticate():
        print("✅ ClubOS APIs authenticated and ready")
    else:
        print("❌ ClubOS authentication failed")
        exit(1)
    
    # Skip the ClubOS member fetch since it's failing - use direct ID testing instead
    print("� Using hybrid ID mapping approach (direct + cached mapping)...")
    
    # Get all members and find Dennis
    all_members = []
    page = 1
    while page <= 6:  # We know there are about 6 pages
        members = client.get_all_members(page=page, page_size=100)
        if not members:
            break
        all_members.extend(members)
        page += 1
    
    print(f"📋 Total members retrieved: {len(all_members)}")
    
    # Find Dennis and Jordan for testing different ID columns from CSV
    dennis = None
    jordan = None
    for member in all_members:
        if 'DENNIS' in member.get('firstName', '').upper() and 'ROST' in member.get('lastName', '').upper():
            dennis = member
        elif 'JORDAN' in member.get('firstName', '').upper() and 'KRUEGER' in member.get('lastName', '').upper():
            jordan = member
    
    if dennis:
        print("\n=== DENNIS ROST - CLUBOS TRAINING CHECK ===")
        print(f"ClubHub ID: {dennis.get('id')}")
        print(f"Name: {dennis.get('firstName')} {dennis.get('lastName')}")
        
        # NOW CHECK CLUBOS FOR TRAINING DATA (Jordan's method)
        dennis_name = f"{dennis.get('firstName')} {dennis.get('lastName')}"
        dennis_id = str(dennis.get('id'))
        
    # Test CSV ID columns as potential ClubOS IDs
    print("\n=== TESTING CSV ID COLUMNS AS CLUBOS IDS ===")
    
    # Test Jordan's different IDs from CSV
    if jordan:
        print(f"\n🔍 JORDAN KRUEGER - Testing multiple ID columns:")
        print(f"   ClubHub ID: {jordan.get('id')}")
        
        # From CSV data: agreementHistory_memberId: 9100, agreement_agreementID: 47280095, userId: 18092705
        test_ids = [
            ("ClubHub ID", str(jordan.get('id'))),  # 44871105
            ("agreementHistory_memberId", "9100"),  # From CSV
            ("Known ClubOS ID", "160402199"),  # From funding_status_cache
            ("agreement_agreementID", "47280095"),  # From CSV
            ("userId", "18092705")  # From CSV
        ]
        
        for id_type, test_id in test_ids:
            try:
                print(f"   Testing {id_type} ({test_id})...")
                payment_status = training_api.get_member_payment_status(test_id)
                if payment_status:
                    print(f"   ✅ SUCCESS with {id_type}: {payment_status}")
                else:
                    print(f"   ❌ No training data with {id_type}")
            except Exception as e:
                print(f"   ⚠️ Error with {id_type}: {str(e)}")
    
    # Test Dennis's IDs (should work with ClubHub ID)
    if dennis:
        print(f"\n🔍 DENNIS ROST - Testing multiple ID columns:")
        print(f"   ClubHub ID: {dennis.get('id')}")
        
        # From CSV data: agreementHistory_memberId: 65828815 (same as ClubHub ID), agreement_agreementID: 96530079, userId: 31489560
        test_ids = [
            ("ClubHub ID", str(dennis.get('id'))),  # 65828815
            ("agreementHistory_memberId", "65828815"),  # From CSV (same as ClubHub)
            ("agreement_agreementID", "96530079"),  # From CSV
            ("userId", "31489560")  # From CSV
        ]
        
        for id_type, test_id in test_ids:
            try:
                print(f"   Testing {id_type} ({test_id})...")
                payment_status = training_api.get_member_payment_status(test_id)
                if payment_status:
                    print(f"   ✅ SUCCESS with {id_type}: {payment_status}")
                else:
                    print(f"   ❌ No training data with {id_type}")
            except Exception as e:
                print(f"   ⚠️ Error with {id_type}: {str(e)}")
        
    
    # Test name-based search approach for Dennis
    if dennis:
        print("\n=== DENNIS ROST - CLUBOS NAME SEARCH ===")
        print(f"ClubHub ID: {dennis.get('id')}")
        print(f"Name: {dennis.get('firstName')} {dennis.get('lastName')}")
        
        dennis_name = f"{dennis.get('firstName')} {dennis.get('lastName')}"
        
        try:
            print(f"🔍 Searching ClubOS for member: {dennis_name}")
            
            # Search for Dennis using the ClubOS member search
            dennis_clubos_id = clubos_client._search_member(dennis_name)
            
            if dennis_clubos_id:
                print(f"✅ Found Dennis in ClubOS with ID: {dennis_clubos_id}")
                
                # Now get his training payment status
                print(f"🔍 Getting training payment status...")
                payment_status = training_api.get_member_payment_status(dennis_clubos_id)
                
                if payment_status:
                    print(f"✅ DENNIS HAS TRAINING DATA!")
                    print(f"   ClubOS ID: {dennis_clubos_id}")
                    print(f"   Payment Status: {payment_status}")
                    print(f"   Data Type: {type(payment_status)}")
                else:
                    print(f"❌ Dennis found but has no training data")
            else:
                print(f"❌ Dennis not found in ClubOS member search")
                
        except Exception as e:
            print(f"⚠️ Error searching for Dennis: {str(e)}")
    else:
        print("❌ Dennis not found in ClubHub")
        
    # Test the name-based search approach on sample members
    print(f"\n=== TESTING NAME-BASED SEARCH + TRAINING LOOKUP ON SAMPLE MEMBERS ===")
    
    training_clients_found = []
    
    # Test on first 10 members to see if search + training lookup works
    for i, member in enumerate(all_members[:10]):
        member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
        print(f"\n🔍 Testing: {member_name}")
        
        try:
            # Search for member in ClubOS
            clubos_id = clubos_client._search_member(member_name)
            
            if clubos_id:
                print(f"   ✅ Found ClubOS ID: {clubos_id}")
                
                # Check for training data
                payment_status = training_api.get_member_payment_status(clubos_id)
                
                if payment_status:
                    training_clients_found.append({
                        'name': member_name,
                        'clubhub_id': member.get('id'),
                        'clubos_id': clubos_id,
                        'payment_status': payment_status
                    })
                    
                    status_emoji = "✅" if 'current' in str(payment_status).lower() else "⚠️"
                    print(f"   {status_emoji} TRAINING CLIENT: {payment_status}")
                else:
                    print(f"   ❌ No training data")
            else:
                print(f"   ❌ Not found in ClubOS")
                
        except Exception as e:
            print(f"   ⚠️ Error: {str(e)}")
            
        if i >= 4:  # Just test first  5 members
            break
    
    print(f"\n=== SAMPLE TEST RESULTS ===")
    print(f"Found {len(training_clients_found)} training clients in sample:")
    for client in training_clients_found:
        print(f"   ✅ {client['name']} - {client['payment_status']} (ClubOS: {client['clubos_id']})")
    
    if len(training_clients_found) > 0:
        print(f"\n🎉 SUCCESS! Name-based search + training lookup works!")
        print(f"Ready to scale to all {len(all_members)} members")
    else:
        print(f"\n❌ No training clients found in sample - need to debug approach")
        
else:
    print("❌ Authentication failed")
