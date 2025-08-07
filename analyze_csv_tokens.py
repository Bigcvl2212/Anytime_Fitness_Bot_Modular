#!/usr/bin/env python3
"""
Analyze the master contact list CSV to extract useful data for API access
"""

import pandas as pd
import json
import ast
import sys
sys.path.append('.')

def analyze_csv_columns():
    """Analyze all columns in the master contact list CSV"""
    
    print("📄 Analyzing master contact list CSV columns...")
    print("=" * 70)
    
    try:
        csv_path = 'data/csv_exports/master_contact_list_with_invoices_20250723_154848.csv'
        df = pd.read_csv(csv_path)
        
        print(f"Total rows: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        
        print(f"\n📋 All columns:")
        for i, col in enumerate(df.columns):
            print(f"   {i+1:2d}. {col}")
        
        # Look specifically for token-related columns
        print(f"\n🔑 Token-related columns:")
        token_columns = [col for col in df.columns if 'token' in col.lower()]
        for col in token_columns:
            print(f"   {col}")
            
        # Look for agreement-related columns  
        print(f"\n📝 Agreement-related columns:")
        agreement_columns = [col for col in df.columns if 'agreement' in col.lower()]
        for col in agreement_columns:
            print(f"   {col}")
        
        # Look for ID-related columns
        print(f"\n🆔 ID-related columns:")
        id_columns = [col for col in df.columns if 'id' in col.lower() or 'guid' in col.lower()]
        for col in id_columns:
            print(f"   {col}")
            
        return df
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return None

def examine_dennis_data(df):
    """Look specifically at Dennis's data in the CSV"""
    
    if df is None:
        return
        
    print(f"\n🔍 Looking for Dennis Rost in CSV...")
    print("=" * 70)
    
    # Search for Dennis
    dennis_rows = df[
        (df['firstName'].str.contains('Dennis', case=False, na=False)) |
        (df['lastName'].str.contains('Rost', case=False, na=False))
    ]
    
    print(f"Found {len(dennis_rows)} rows for Dennis")
    
    for i, (idx, row) in enumerate(dennis_rows.iterrows()):
        print(f"\n📋 Dennis Record {i+1}:")
        print(f"   Name: {row.get('firstName', 'N/A')} {row.get('lastName', 'N/A')}")
        print(f"   Email: {row.get('email', 'N/A')}")
        print(f"   ID: {row.get('id', 'N/A')}")
        print(f"   UserID: {row.get('userId', 'N/A')}")
        print(f"   GUID: {row.get('guid', 'N/A')}")
        
        # Check token-related fields
        print(f"\n🔑 Token Information:")
        for col in df.columns:
            if 'token' in col.lower() and pd.notna(row.get(col)):
                print(f"   {col}: {row.get(col)}")
        
        # Check agreement data
        print(f"\n📝 Agreement Information:")
        agreement_cols = ['agreementHistory_activeAgreement', 'agreement_agreementGuid', 'agreement_agreementID']
        for col in agreement_cols:
            if col in row and pd.notna(row.get(col)):
                value = row.get(col)
                print(f"   {col}: {value}")
                
                # Try to parse JSON data
                if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                    try:
                        parsed = ast.literal_eval(value)
                        print(f"     Parsed: {json.dumps(parsed, indent=6)[:500]}...")
                    except:
                        print(f"     (Failed to parse as JSON)")

def find_token_patterns(df):
    """Look for patterns in token data that might help with API access"""
    
    if df is None:
        return
        
    print(f"\n🔍 Analyzing token patterns...")
    print("=" * 70)
    
    # Look at payment token data
    if 'agreementTokenQuery_paymentToken' in df.columns:
        tokens = df['agreementTokenQuery_paymentToken'].dropna()
        print(f"Found {len(tokens)} payment tokens")
        
        if len(tokens) > 0:
            print(f"Sample payment tokens:")
            for i, token in enumerate(tokens.head(5)):
                print(f"   Token {i+1}: {token}")
    
    # Look at agreement endpoints data
    if 'agreement_endpoints_found' in df.columns:
        endpoints = df['agreement_endpoints_found'].dropna()
        print(f"\nFound {len(endpoints)} endpoint entries")
        
        unique_endpoints = endpoints.unique()
        print(f"Unique endpoint patterns:")
        for endpoint in unique_endpoints:
            print(f"   {endpoint}")

def extract_member_ids_and_tokens(df):
    """Extract all member IDs and any tokens that might be useful"""
    
    if df is None:
        return
        
    print(f"\n🗂️  Extracting member IDs and tokens...")
    print("=" * 70)
    
    # Get all unique member IDs
    member_ids = df['id'].dropna().unique()
    user_ids = df['userId'].dropna().unique()
    
    print(f"Unique member IDs: {len(member_ids)} (first 10: {member_ids[:10]})")
    print(f"Unique user IDs: {len(user_ids)} (first 10: {user_ids[:10]})")
    
    # Look for any URLs or endpoints in the data
    print(f"\n🔗 Looking for URLs or endpoints...")
    
    url_columns = [col for col in df.columns if 'url' in col.lower() or 'endpoint' in col.lower()]
    print(f"URL-related columns: {url_columns}")
    
    for col in url_columns:
        if col in df.columns:
            urls = df[col].dropna().unique()
            if len(urls) > 0:
                print(f"   {col}: {len(urls)} unique values")
                for url in urls[:3]:  # Show first 3
                    print(f"     {url}")

def test_extracted_tokens():
    """Test if any of the extracted tokens can be used with ClubOS API"""
    
    print(f"\n🧪 Testing extracted data with ClubOS API...")
    print("=" * 70)
    
    try:
        from clubos_training_api import ClubOSTrainingPackageAPI
        
        api = ClubOSTrainingPackageAPI()
        if not api.authenticate():
            print("❌ Failed to authenticate")
            return
        
        # Read CSV again to get fresh data
        csv_path = 'data/csv_exports/master_contact_list_with_invoices_20250723_154848.csv'
        df = pd.read_csv(csv_path)
        
        # Test a few member IDs as delegation targets
        test_ids = df['id'].dropna().head(5).tolist()
        
        print(f"Testing delegation with sample member IDs...")
        
        for member_id in test_ids:
            print(f"\n🎯 Testing member ID: {member_id}")
            
            try:
                # Try delegation
                delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{member_id}/url=false")
                print(f"   Delegation status: {delegation_response.status_code}")
                
                if delegation_response.status_code == 200:
                    # Check for agreements
                    agreements_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                    print(f"   Agreements status: {agreements_response.status_code}")
                    
                    if agreements_response.status_code == 200:
                        agreements = agreements_response.json()
                        print(f"   Found {len(agreements)} agreements")
                        
                        if agreements:
                            for agreement in agreements[:1]:  # Show first one
                                package_info = agreement.get('packageAgreement', {})
                                name = package_info.get('name', 'No name')
                                training_id = package_info.get('memberId', 'No member ID')
                                print(f"     Package: {name} (Training ID: {training_id})")
                            
            except Exception as e:
                print(f"   Error: {e}")
                
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    df = analyze_csv_columns()
    examine_dennis_data(df)
    find_token_patterns(df)
    extract_member_ids_and_tokens(df)
    test_extracted_tokens()
    
    print("\n" + "=" * 70)
    print("🏁 CSV analysis complete!")
