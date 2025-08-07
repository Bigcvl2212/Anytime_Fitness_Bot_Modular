#!/usr/bin/env python3
"""
HAR File Analysis Summary - Training Package Endpoints and Workflow
Based on the patterns found in the codebase from previous HAR analysis
"""

def har_training_workflow_summary():
    """Summary of training package workflow discovered from HAR analysis"""
    
    print("🔍 HAR Analysis Summary - Training Package Workflow")
    print("=" * 60)
    
    print("\n📋 Key Findings from HAR Files:")
    
    print(f"\n1. 🎯 Delegation Pattern:")
    print(f"   • URL: /action/Delegate/{{delegateUserId}}/url=false")
    print(f"   • Must be called BEFORE accessing training packages")
    print(f"   • Sets session context for the specified user")
    print(f"   • Working delegate IDs found in HAR:")
    print(f"     - 189425730 (Dennis Rost)")
    print(f"     - 184027841 (Common in HAR files)")
    print(f"     - 185777276 (Alternative ID)")
    print(f"     - 1840278041 (JWT delegateUserId)")
    
    print(f"\n2. 📦 Training Package Endpoints:")
    print(f"   • Primary: /api/agreements/package_agreements/list")
    print(f"   • With member filter: /api/agreements/package_agreements/list?memberId={{id}}")
    print(f"   • Active only: /api/agreements/package_agreements/active?memberId={{id}}")
    print(f"   • Alternative: /api/agreements/package_agreements?memberId={{id}}")
    print(f"   • V2 endpoint: /api/agreements/package_agreements/V2/{{agreementId}}")
    print(f"   • Billing status: /api/agreements/package_agreements/{{agreementId}}/billing_status")
    print(f"   • Search: /api/agreements/package_agreements/search")
    print(f"   • Invoices: /api/agreements/package_agreements/invoices")
    
    print(f"\n3. 🔄 Required Workflow Sequence:")
    print(f"   1. Authenticate with ClubOS (login)")
    print(f"   2. Set delegation: GET /action/Delegate/{{delegateUserId}}/url=false")
    print(f"   3. Get packages: GET /api/agreements/package_agreements/list")
    print(f"   4. Get billing details: GET /api/agreements/package_agreements/{{id}}/billing_status")
    
    print(f"\n4. 🔑 Authentication Details:")
    print(f"   • Cookie-based session management")
    print(f"   • Key cookies: JSESSIONID, loggedInUserId, delegatedUserId")
    print(f"   • Headers: User-Agent, Accept, Referer required")
    print(f"   • Content-Type: application/json for API calls")
    
    print(f"\n5. 📊 Response Structure (Dennis Example):")
    response_example = {
        "packageAgreement": {
            "id": 1598572,
            "name": "2025 1X1 Training", 
            "memberId": 189425730,
            "agreementStatus": 2,
            "startDate": "2025-02-14",
            "endDate": "2026-02-14"
        },
        "packageAgreementMemberServices": [{
            "name": "Month Coaching Membership",
            "unitPrice": 30.0,
            "unitsPerBillingDuration": 4,
            "billingDuration": 2,
            "billingDurationType": 6
        }]
    }
    print(f"   Structure: {response_example}")
    
    print(f"\n6. ❌ Key Limitations Discovered:")
    print(f"   • CSV member IDs ≠ Training delegate IDs")
    print(f"   • Manual member search workflow doesn't work for training clients")
    print(f"   • ClubServices page navigation fails with CSV IDs")
    print(f"   • No systematic way found to map CSV IDs to delegate IDs")
    
    print(f"\n7. 🎯 Working Training Client IDs Found:")
    working_ids = [
        ("Dennis Rost", "189425730", "2025 1X1 Training"),
        ("Jeremy Mayo", "184027841", "Unknown package"),
        ("Alternative User", "185777276", "Unknown package")
    ]
    
    for name, delegate_id, package in working_ids:
        print(f"   • {name}: {delegate_id} - {package}")
    
    print(f"\n8. 🔍 Discovery Strategy:")
    print(f"   • Systematic ID scanning around known working IDs")
    print(f"   • Test ranges: ±1000 from known working IDs")
    print(f"   • Delegate ID pattern: 180000000-190000000 range")
    print(f"   • Manual verification of package names and client names")

def test_har_discovered_endpoints():
    """Test the endpoints discovered from HAR analysis"""
    
    print(f"\n🧪 Testing HAR-Discovered Endpoints")
    print("=" * 60)
    
    try:
        import sys
        sys.path.append('.')
        from clubos_training_api import ClubOSTrainingPackageAPI
        
        api = ClubOSTrainingPackageAPI()
        if not api.authenticate():
            print("❌ Authentication failed")
            return
        
        # Test Dennis's known working delegate ID
        dennis_delegate_id = "189425730"
        
        print(f"\n📝 Testing delegation workflow for Dennis ({dennis_delegate_id})...")
        
        # Step 1: Set delegation
        delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{dennis_delegate_id}/url=false")
        print(f"   Delegation status: {delegation_response.status_code}")
        
        if delegation_response.status_code == 200:
            # Step 2: Test multiple package endpoints
            endpoints_to_test = [
                "/api/agreements/package_agreements/list",
                f"/api/agreements/package_agreements/list?memberId={dennis_delegate_id}",
                f"/api/agreements/package_agreements/active?memberId={dennis_delegate_id}",
                f"/api/agreements/package_agreements?memberId={dennis_delegate_id}",
                "/api/agreements/package_agreements/search",
                "/api/agreements/package_agreements/invoices"
            ]
            
            for endpoint in endpoints_to_test:
                try:
                    response = api.session.get(f"{api.base_url}{endpoint}")
                    print(f"   {endpoint}: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"      → {len(data)} items returned")
                        elif isinstance(data, dict):
                            if 'agreements' in data:
                                print(f"      → {len(data['agreements'])} agreements found")
                            else:
                                print(f"      → {len(data)} keys in response")
                    else:
                        print(f"      → Error: {response.text[:100]}...")
                        
                except Exception as e:
                    print(f"      → Exception: {e}")
        
        # Test the other known working IDs
        other_delegate_ids = ["184027841", "185777276"]
        
        for test_id in other_delegate_ids:
            print(f"\n📝 Testing delegation for ID {test_id}...")
            
            delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{test_id}/url=false")
            print(f"   Delegation status: {delegation_response.status_code}")
            
            if delegation_response.status_code == 200:
                agreements_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                print(f"   Agreements status: {agreements_response.status_code}")
                
                if agreements_response.status_code == 200:
                    agreements = agreements_response.json()
                    print(f"   Found {len(agreements)} agreements for ID {test_id}")
                    
                    if agreements:
                        for i, agreement in enumerate(agreements):
                            package_info = agreement.get('packageAgreement', {})
                            name = package_info.get('name', 'No name')
                            member_id = package_info.get('memberId', 'No member ID')
                            print(f"      Agreement {i+1}: {name} (Member: {member_id})")
        
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")

if __name__ == "__main__":
    har_training_workflow_summary()
    test_har_discovered_endpoints()
    
    print(f"\n" + "=" * 60)
    print("🏁 HAR Analysis Summary Complete!")
    print(f"\nNext Steps:")
    print(f"1. Use the working delegation + package_agreements workflow")
    print(f"2. Systematically scan for more training delegate IDs")
    print(f"3. Build mapping from discovered delegates to member names")
    print(f"4. Add discovered training clients to database")
