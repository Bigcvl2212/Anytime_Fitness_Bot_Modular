import os
import json
import requests
import pandas as pd
from datetime import datetime

# --- CONFIG ---
# Get the absolute path to the project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))

CONTACT_LIST_CSV = "master_contact_list_20250715_181714.csv"
CONTACT_LIST_XLSX = "master_contact_list_20250715_181714.xlsx"
TOKEN_FILE = os.path.join(project_root, "data", "clubhub_tokens.json")
OUTPUT_DIR = os.path.join(project_root, "data", "csv_exports")
CLUBHUB_BASE = "https://clubhub-ios-api.anytimefitness.com"
CLUBOS_BASE = "https://anytime.club-os.com"
ID_COLUMN = "agreementHistory_memberId"

# --- HELPERS ---
def get_latest_bearer_token(token_file=TOKEN_FILE):
    try:
        # Final fallback - try to read from token file
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            
            if isinstance(token_data, list) and token_data:
                latest_token = token_data[-1]
                bearer_token = latest_token.get('bearer_token')
                if bearer_token:
                    print("Using token from token file")
                    return bearer_token
            elif isinstance(token_data, dict):
                # Try different token file formats
                for key, value in token_data.items():
                    if isinstance(value, dict) and "bearer_token" in value:
                        token = value["bearer_token"]
                        if token:
                            return token
                        
    except Exception as e:
        print(f"Error reading token file: {e}")
    
    raise ValueError("No bearer_token found in token file!")

def fetch_agreement(member_id, bearer_token):
    """Fetch detailed agreement information for a member using the working approach"""
    try:
        # First get the basic agreement from ClubHub (like the working script)
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Accept': 'application/json',
            'User-Agent': 'ClubHub-iOS/4.0.0',
            'API-version': '1'
        }
        
        url = f"{CLUBHUB_BASE}/api/members/{member_id}/agreement"
        
        resp = requests.get(url, headers=headers, verify=False, timeout=15)
        
        if resp.ok:
            basic_agreement = resp.json()
            
            # If we have an agreement ID, we could get detailed info from ClubOS
            # But for now, just return the basic agreement data
            return basic_agreement
        else:
            print(f"[WARN] {member_id}: HTTP {resp.status_code}")
            return None
            
    except Exception as e:
        print(f"[ERROR] {member_id}: {e}")
        return None

def flatten_dict(d, parent_key='', sep='.'):  # For nested JSON
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

# --- MAIN ---
def main():
    print("Loading latest ClubHub API token...")
    bearer_token = get_latest_bearer_token()
    print("Loading master contact list...")
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load as DataFrame - look for existing contact list in the project data directory
    contact_list_csv = os.path.join(project_root, "data", "csv_exports", "master_contact_list_with_agreements_20250722_180712.csv")
    contact_list_xlsx = os.path.join(project_root, "data", "csv_exports", "master_contact_list_with_agreements_20250722_180712.xlsx")
    
    if os.path.exists(contact_list_xlsx):
        print(f"Loading from: {contact_list_xlsx}")
        df = pd.read_excel(contact_list_xlsx, dtype=str)
    elif os.path.exists(contact_list_csv):
        print(f"Loading from: {contact_list_csv}")
        df = pd.read_csv(contact_list_csv, dtype=str)
    else:
        raise FileNotFoundError(f"No contact list found at:\n- {contact_list_csv}\n- {contact_list_xlsx}")
        
    if ID_COLUMN not in df.columns:
        raise ValueError(f"Column '{ID_COLUMN}' not found in contact list!")
    print(f"Loaded {len(df)} members from contact list.")
    # Fetch agreement info for each member
    agreement_data = []
    all_keys = set()
    for idx, row in df.iterrows():
        member_id = row[ID_COLUMN]
        if not member_id or pd.isna(member_id):
            agreement_data.append({})
            continue
        agreement = fetch_agreement(member_id, bearer_token)
        if agreement:
            flat = flatten_dict(agreement)
            agreement_data.append(flat)
            all_keys.update(flat.keys())
        else:
            agreement_data.append({})
        if (idx+1) % 25 == 0:
            print(f"Processed {idx+1}/{len(df)} members...")
    print(f"Fetched agreement info for all members. Adding columns...")
    # Add all agreement fields as columns
    for key in all_keys:
        df[f"agreement.{key}"] = [d.get(key, None) for d in agreement_data]
    
    # Save updated contact list with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = os.path.join(OUTPUT_DIR, f"master_contact_list_with_agreements_{timestamp}.csv")
    output_xlsx = os.path.join(OUTPUT_DIR, f"master_contact_list_with_agreements_{timestamp}.xlsx")
    
    print("Saving updated contact list (CSV and XLSX)...")
    df.to_csv(output_csv, index=False)
    df.to_excel(output_xlsx, index=False)
    print(f"Done! Files saved:")
    print(f"- CSV: {output_csv}")
    print(f"- XLSX: {output_xlsx}")

if __name__ == "__main__":
    main() 