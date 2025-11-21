import pandas as pd
import requests
import time
from src.services.api.clubos_api_client import ClubOSAPIClient

MASTER_CONTACT_LIST_XLSX = "master_contact_list_20250715_181714.xlsx"
MASTER_CONTACT_LIST_CSV = "master_contact_list_20250715_181714.csv"

def is_training_or_single_club(row):
    """Check if member is a training or single club client"""
    # Check if they have training data from the merge
    has_training_data = any([
        pd.notna(row.get('ID')),
        pd.notna(row.get('Member Name')),
        pd.notna(row.get('Agreement Name')),
        pd.notna(row.get('Next Invoice Subtotal'))
    ])
    
    # Also check agreement name for training/single club indicators
    agreement_name = str(row.get('Agreement Name', '')).lower()
    is_training = any(term in agreement_name for term in ['training', 'sgt', 'coaching', '1x1'])
    is_single_club = 'single club' in agreement_name
    
    return has_training_data and (is_training or is_single_club)

def fetch_agreement_details(client, member_id):
    """Fetch agreement details for a member using ClubOS API"""
    try:
        # Use the existing get_member_agreements method
        agreements = client.get_member_agreements(member_id)
        if agreements:
            # Return the first agreement (or you can iterate through all)
            return agreements[0]
        return None
    except Exception as e:
        print(f"Error fetching agreement for {member_id}: {e}")
        return None

def main():
    # Load master contact list
    try:
        df = pd.read_excel(MASTER_CONTACT_LIST_XLSX)
    except:
        df = pd.read_csv(MASTER_CONTACT_LIST_CSV)
    
    # Filter for training/single club clients
    training_clients = df[df.apply(is_training_or_single_club, axis=1)].copy()
    print(f"Found {len(training_clients)} training/single club clients")
    
    # Initialize ClubOS client
    client = ClubOSAPIClient()
    if not client.authenticate():
        print("❌ Failed to authenticate to ClubOS")
        return
    
    print("✅ Authenticated to ClubOS")
    
    # Process each training client
    for idx, row in training_clients.iterrows():
        member_id = row['ProspectID']
        member_name = row.get('Member Name') or row.get('Name', 'Unknown')
        
        print(f"Processing {member_name} (ID: {member_id})...")
        
        # Fetch agreement details
        agreement = fetch_agreement_details(client, member_id)
        
        if agreement:
            # Extract relevant fields (adjust based on actual API response structure)
            df.at[idx, 'training_agreement_id'] = agreement.get('id')
            df.at[idx, 'training_agreement_name'] = agreement.get('name')
            df.at[idx, 'training_past_due_amount'] = agreement.get('pastDueAmount', 0)
            df.at[idx, 'training_next_payment'] = agreement.get('nextPaymentAmount', 0)
            df.at[idx, 'training_agreement_status'] = agreement.get('status')
            df.at[idx, 'training_agreement_expiry'] = agreement.get('expirationDate')
            
            print(f"  ✅ Found agreement: {agreement.get('name', 'Unknown')}")
        else:
            print(f"  ❌ No agreement found")
            df.at[idx, 'training_agreement_status'] = 'No agreement found'
        
        # Add delay to avoid overwhelming the API
        time.sleep(1)
    
    # Save updated master contact list
    df.to_excel(MASTER_CONTACT_LIST_XLSX, index=False)
    df.to_csv(MASTER_CONTACT_LIST_CSV, index=False)
    print(f"✅ Updated master contact list with training agreement details")

if __name__ == "__main__":
    main() 