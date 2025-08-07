#!/usr/bin/env python3
"""
Test what Dennis's payment token actually does with ClubOS API
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
import json

def test_payment_token_usage():
    """Test Dennis's payment token with various API endpoints"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("🔍 Testing Dennis's payment token usage...")
    print("=" * 70)
    
    # Dennis's payment token from CSV
    dennis_token = "8d4b4880-39dd-4a6a-b3d4-0b3a7c9fc02f"
    print(f"Dennis's payment token: {dennis_token}")
    
    # Test token in various ways
    token_tests = [
        # As query parameter
        ("/api/agreements/package_agreements/list", {"token": dennis_token}),
        ("/api/agreements/package_agreements/list", {"paymentToken": dennis_token}),
        ("/api/agreements/package_agreements/list", {"agreementToken": dennis_token}),
        
        # As header
        ("/api/agreements/package_agreements/list", None, {"X-Payment-Token": dennis_token}),
        ("/api/agreements/package_agreements/list", None, {"Authorization": f"Bearer {dennis_token}"}),
        ("/api/agreements/package_agreements/list", None, {"X-Agreement-Token": dennis_token}),
        
        # Token-specific endpoints
        ("/api/agreements/token/" + dennis_token, None),
        ("/api/payments/token/" + dennis_token, None),
        ("/api/billing/token/" + dennis_token, None),
        
        # Action endpoints with token
        ("/action/Agreement/token/" + dennis_token, None),
        ("/action/Payment/token/" + dennis_token, None),
    ]
    
    for i, test in enumerate(token_tests):
        endpoint = test[0]
        params = test[1] if len(test) > 1 else None
        headers = test[2] if len(test) > 2 else None
        
        print(f"\n🧪 Test {i+1}: {endpoint}")
        if params:
            print(f"   Params: {params}")
        if headers:
            print(f"   Headers: {headers}")
        
        try:
            # Prepare request headers
            request_headers = api.session.headers.copy()
            if headers:
                request_headers.update(headers)
            
            response = api.session.get(
                f"{api.base_url}{endpoint}",
                params=params,
                headers=request_headers
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS! JSON response")
                    print(f"   Data: {json.dumps(data, indent=2)[:300]}...")
                except:
                    print(f"   ✅ SUCCESS! HTML response ({len(response.text)} chars)")
                    if len(response.text) < 1000:
                        print(f"   Content: {response.text[:200]}...")
            elif response.status_code == 404:
                print(f"   ❌ 404 Not Found")
            elif response.status_code == 401:
                print(f"   🔐 401 Unauthorized")
            elif response.status_code == 403:
                print(f"   🚫 403 Forbidden")
            else:
                print(f"   ⚠️  {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_agreement_id_from_csv():
    """Test the agreement ID that's associated with Dennis's payment token"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print(f"\n🎯 Testing Dennis's agreement ID from CSV...")
    print("=" * 70)
    
    # From the CSV analysis, Dennis has agreement ID 1598572
    agreement_id = "1598572"
    print(f"Dennis's agreement ID: {agreement_id}")
    
    # Test agreement-specific endpoints
    agreement_tests = [
        f"/api/agreements/{agreement_id}",
        f"/api/agreements/{agreement_id}/details",
        f"/api/agreements/{agreement_id}/packages",
        f"/api/agreements/{agreement_id}/billing",
        f"/api/agreements/{agreement_id}/status",
        f"/action/Agreement/{agreement_id}",
        f"/action/Agreement/{agreement_id}/view",
    ]
    
    for endpoint in agreement_tests:
        print(f"\n📍 Testing: {endpoint}")
        
        try:
            response = api.session.get(f"{api.base_url}{endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS! JSON response")
                    print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    if isinstance(data, dict) and 'packageAgreement' in data:
                        package = data['packageAgreement']
                        print(f"   Package: {package.get('name', 'No name')}")
                        print(f"   Member ID: {package.get('memberId', 'No member ID')}")
                except:
                    print(f"   ✅ SUCCESS! HTML response ({len(response.text)} chars)")
            else:
                print(f"   ❌ {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def analyze_csv_payment_tokens():
    """Analyze what the payment tokens in CSV actually represent"""
    
    print(f"\n📊 Analyzing CSV payment token patterns...")
    print("=" * 70)
    
    try:
        import pandas as pd
        
        csv_path = "data/csv_exports/master_contact_list_with_invoices_20250723_154848.csv"
        df = pd.read_csv(csv_path)
        
        # Look at members with payment tokens
        with_tokens = df[df['agreementTokenQuery_paymentToken'].notna()]
        
        print(f"Total members: {len(df)}")
        print(f"Members with payment tokens: {len(with_tokens)}")
        print(f"Percentage: {len(with_tokens)/len(df)*100:.1f}%")
        
        # Look at the agreement IDs for members with tokens
        if 'agreementId' in df.columns:
            unique_agreements = with_tokens['agreementId'].nunique()
            print(f"Unique agreement IDs: {unique_agreements}")
        
        # Look at payment status patterns
        if 'payment_status' in df.columns:
            payment_status_counts = with_tokens['payment_status'].value_counts()
            print(f"\nPayment status distribution:")
            for status, count in payment_status_counts.items():
                print(f"   {status}: {count}")
        
        # Look at member status patterns
        if 'member_status' in df.columns:
            member_status_counts = with_tokens['member_status'].value_counts()
            print(f"\nMember status distribution:")
            for status, count in member_status_counts.items():
                print(f"   {status}: {count}")
        
        # Sample a few token holders to see what they have in common
        print(f"\nSample token holders:")
        sample_cols = ['name', 'agreementId', 'payment_status', 'member_status', 'agreementTokenQuery_paymentToken']
        available_cols = [col for col in sample_cols if col in df.columns]
        
        for i, row in with_tokens[available_cols].head(10).iterrows():
            print(f"   {row.get('name', 'Unknown')}: Agreement {row.get('agreementId', 'N/A')}, Status: {row.get('payment_status', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error analyzing CSV: {e}")

if __name__ == "__main__":
    test_payment_token_usage()
    test_agreement_id_from_csv()
    analyze_csv_payment_tokens()
    
    print("\n" + "=" * 70)
    print("🏁 Payment token analysis complete!")
