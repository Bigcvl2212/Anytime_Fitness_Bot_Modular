#!/usr/bin/env python3
"""
Test the exact breakthrough process for Mark Benzinger
This replicates the exact working steps from yesterday's conversation
"""

print("🚀 TESTING EXACT BREAKTHROUGH PROCESS FOR MARK BENZINGER")
print("=" * 60)

try:
    # Import the working API
    from clubos_training_api_fixed import ClubOSTrainingPackageAPI
    from src.config.clubos_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
    
    # Test member details (from conversation history)
    member_id = "125814462"  # Mark Benzinger's clubos_member_id
    expected_guid = "66082049"  # Mark Benzinger's GUID
    expected_packages = 13  # From conversation: "Mark Benzinger's 13 training packages"
    
    print(f"📋 Testing Member: {member_id}")
    print(f"📋 Expected GUID: {expected_guid}")
    print(f"📋 Expected Packages: {expected_packages}")
    print()
    
    # STEP 1: Create API instance with exact working credentials
    print("🔐 STEP 1: AUTHENTICATION")
    print("-" * 20)
    api = ClubOSTrainingPackageAPI()
    api.username = CLUBOS_USERNAME
    api.password = CLUBOS_PASSWORD
    
    print(f"📋 Using credentials: {CLUBOS_USERNAME[:3]}*** / {len(CLUBOS_PASSWORD)} chars")
    
    # Authenticate
    auth_result = api.authenticate()
    print(f"✅ Authentication result: {auth_result}")
    
    if not auth_result:
        print("❌ AUTHENTICATION FAILED - Cannot proceed")
        exit(1)
    
    print(f"✅ Session cookies: {list(api.session.cookies.keys())}")
    print()
    
    # STEP 2: Delegate to member using GUID
    print("👤 STEP 2: DELEGATION")
    print("-" * 20)
    print(f"🔑 Delegating to member GUID: {expected_guid}")
    
    delegate_result = api.delegate_to_member(expected_guid)
    print(f"✅ Delegation result: {delegate_result}")
    
    if not delegate_result:
        print("❌ DELEGATION FAILED - Cannot proceed")
        exit(1)
    
    # Safe cookie logging to avoid CookieConflictError
    delegation_cookies = []
    for cookie in api.session.cookies:
        if cookie.name == 'delegatedUserId':
            delegation_cookies.append(cookie.value)
    print(f"✅ Delegation cookies: {delegation_cookies}")
    print()
    
    # STEP 3: Test the breakthrough discovery method
    print("📋 STEP 3: BREAKTHROUGH AGREEMENT DISCOVERY")
    print("-" * 40)
    print("🧪 Testing discover_member_agreement_ids (the breakthrough method)")
    
    agreement_ids = api.discover_member_agreement_ids(expected_guid)
    print(f"📦 Agreement IDs found: {len(agreement_ids)}")
    print(f"📦 Agreement IDs: {agreement_ids}")
    
    if agreement_ids:
        print(f"🎉 SUCCESS: Found {len(agreement_ids)} agreement IDs!")
        
        # STEP 4: Test V2 endpoint for one agreement
        if agreement_ids:
            test_agreement_id = agreement_ids[0]
            print()
            print("📊 STEP 4: TESTING V2 AGREEMENT ENDPOINT")
            print("-" * 40)
            print(f"🧪 Testing V2 endpoint for agreement: {test_agreement_id}")
            
            import time
            timestamp = int(time.time() * 1000)
            api_headers = api._auth_headers(referer=f'{api.base_url}/action/PackageAgreementUpdated/spa/')
            api_headers.update({
                'X-Requested-With': 'XMLHttpRequest',
            })
            
            detail_url = f"{api.base_url}/api/agreements/package_agreements/V2/{test_agreement_id}"
            detail_params = {
                'include': 'invoices,scheduledPayments,prohibitChangeTypes',
                '_': timestamp
            }
            
            print(f"🌐 V2 URL: {detail_url}")
            print(f"📋 V2 Params: {detail_params}")
            
            detail_response = api.session.get(detail_url, headers=api_headers, params=detail_params, timeout=15)
            print(f"📊 V2 Response Status: {detail_response.status_code}")
            
            if detail_response.status_code == 200:
                response_json = detail_response.json()
                detail_data = response_json.get('data', {})
                agreement_name = detail_data.get('name', f'Training Package {test_agreement_id}')
                agreement_status = detail_data.get('agreementStatus', 0)
                
                print(f"✅ Agreement Name: {agreement_name}")
                print(f"✅ Agreement Status: {agreement_status}")
                
                if agreement_status == 2:  # Active
                    print("🎯 SUCCESS: Found ACTIVE agreement!")
                else:
                    status_names = {1: "draft", 2: "active", 3: "pending downpayment", 4: "completed", 5: "canceled"}
                    status_name = status_names.get(agreement_status, f"unknown({agreement_status})")
                    print(f"ℹ️ Agreement status: {status_name}")
            else:
                print(f"❌ V2 endpoint failed: {detail_response.status_code}")
                print(f"❌ Response: {detail_response.text}")
    else:
        print("❌ No agreement IDs found - this is the problem!")
    
    print()
    print("📋 BREAKTHROUGH TEST COMPLETE")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
