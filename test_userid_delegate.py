#!/usr/bin/env python3
"""
Test userID from CSV as delegate user ID for training packages
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
import pandas as pd
import json

def test_userid_as_delegate():
    """Test userID values from CSV as delegate user IDs"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    # Read the CSV file
    csv_file = "data/csv_exports/master_contact_list_with_invoices_20250723_154848.csv"
    
    try:
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded CSV with {len(df)} rows")
        print(f"📋 Available columns: {list(df.columns)}")
        
        # Filter for Dennis first
        dennis_rows = df[
            df['firstName'].str.contains('Dennis', case=False, na=False) |
            df['lastName'].str.contains('Rost', case=False, na=False)
        ]
        
        if len(dennis_rows) > 0:
            print(f"\n🎯 Found Dennis in CSV:")
            for idx, row in dennis_rows.iterrows():
                print(f"   Name: {row['firstName']} {row['lastName']}")
                print(f"   userID: {row['userId']}")
                print(f"   ID: {row['id']}")
                
                # Test the userID as delegate user ID
                user_id = str(row['userId'])
                print(f"\n🧪 Testing userID {user_id} as delegate user ID...")
                
                # Use delegation endpoint
                delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{user_id}/url=false")
                print(f"   Delegation status: {delegation_response.status_code}")
                
                if delegation_response.status_code == 200:
                    # Get package agreements
                    response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                    print(f"   Package agreements status: {response.status_code}")
                    
                    if response.status_code == 200:
                        agreements = response.json()
                        print(f"   Found {len(agreements)} agreements for userID {user_id}")
                        
                        if agreements:
                            for i, agreement in enumerate(agreements):
                                print(f"   📦 Agreement {i+1}: {agreement.get('packageAgreement', {}).get('name', 'No name')}")
        
        # Now look for the known working delegate ID 189425730 in the CSV
        print(f"\n🔍 Searching for known working delegate ID 189425730 in CSV...")
        
        # Check if 189425730 appears anywhere in the CSV
        for col in df.columns:
            if df[col].astype(str).str.contains('189425730', na=False).any():
                matching_rows = df[df[col].astype(str).str.contains('189425730', na=False)]
                print(f"   Found 189425730 in column '{col}':")
                for idx, row in matching_rows.iterrows():
                    print(f"     Name: {row.get('firstName', 'Unknown')} {row.get('lastName', 'Unknown')}")
                    print(f"     Value: {row[col]}")
        
        # Also check if any userID when converted to int equals 189425730
        dennis_working_id = 189425730
        userids_numeric = pd.to_numeric(df['userId'], errors='coerce')
        matching_userid = df[userids_numeric == dennis_working_id]
        
        if len(matching_userid) > 0:
            print(f"   🎯 Found exact userID match for 189425730:")
            for idx, row in matching_userid.iterrows():
                print(f"     Name: {row['firstName']} {row['lastName']}")
        else:
            print(f"   ❌ 189425730 not found as userID")
            
        # Let's try some variations - maybe there's a pattern
        print(f"\n🧮 Testing variations of Dennis's known IDs...")
        
        # Dennis's known IDs
        dennis_ids = [
            31489560,     # His userID from CSV
            189425730,    # Working delegate ID from HAR
            65828815,     # His ClubHub member ID
        ]
        
        for test_id in dennis_ids:
            print(f"   Testing {test_id} as delegate...")
            try:
                delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{test_id}/url=false")
                if delegation_response.status_code == 200:
                    response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                    if response.status_code == 200:
                        agreements = response.json()
                        if agreements:
                            print(f"     ✅ {len(agreements)} agreements found!")
                            for agreement in agreements:
                                member_info = agreement.get('packageAgreement', {})
                                print(f"       Package: {member_info.get('name', 'Unknown')}")
                        else:
                            print(f"     ❌ 0 agreements")
                    else:
                        print(f"     ❌ API error: {response.status_code}")
                else:
                    print(f"     ❌ Delegation failed: {delegation_response.status_code}")
            except Exception as e:
                print(f"     ❌ Error: {e}")
        
        # Now test a sample of other userIDs to find training clients
        print(f"\n🔍 Testing sample of other userIDs as delegate user IDs...")
        
        # Take first 20 rows as a sample
        sample_rows = df.head(20)
        
        training_clients_found = []
        
        for idx, row in sample_rows.iterrows():
            user_id = str(row['userId'])
            first_name = row.get('firstName', 'Unknown')
            last_name = row.get('lastName', 'Unknown')
            
            print(f"   Testing {first_name} {last_name} (userID: {user_id})...", end='')
            
            try:
                # Use delegation endpoint
                delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{user_id}/url=false")
                
                if delegation_response.status_code == 200:
                    # Get package agreements
                    response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                    
                    if response.status_code == 200:
                        agreements = response.json()
                        if agreements:
                            print(f" ✅ {len(agreements)} agreements!")
                            training_clients_found.append({
                                'name': f"{first_name} {last_name}",
                                'userID': user_id,
                                'agreements': len(agreements)
                            })
                        else:
                            print(" ❌ 0 agreements")
                    else:
                        print(" ❌ API error")
                else:
                    print(" ❌ delegation failed")
                    
            except Exception as e:
                print(f" ❌ Error: {e}")
        
        if training_clients_found:
            print(f"\n🎯 Found {len(training_clients_found)} training clients:")
            for client in training_clients_found:
                print(f"   {client['name']} (userID: {client['userID']}) - {client['agreements']} agreements")
        else:
            print(f"\n❌ No training clients found in sample")
            
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")

if __name__ == "__main__":
    print("🔍 Testing userID values as delegate user IDs...")
    print("=" * 60)
    
    test_userid_as_delegate()
    
    print("\n" + "=" * 60)
    print("🏁 Complete!")
