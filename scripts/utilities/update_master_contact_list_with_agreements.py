import os
import json
import requests
import pandas as pd
from datetime import datetime

# --- CONFIG ---
CONTACT_LIST_CSV = "master_contact_list_20250715_181714.csv"
CONTACT_LIST_XLSX = "master_contact_list_20250715_181714.xlsx"
TOKEN_FILE = "data/clubhub_tokens.json"
API_BASE = "https://clubhub-ios-api.anytimefitness.com"
ID_COLUMN = "ProspectID"

# --- HELPERS ---
def get_latest_bearer_token(token_file=TOKEN_FILE):
    with open(token_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Find the latest entry by extracted_at or extraction_timestamp
    latest_key = max(data, key=lambda k: data[k]["tokens"].get("extraction_timestamp", ""))
    token = data[latest_key]["tokens"].get("bearer_token")
    if not token:
        raise ValueError("No bearer_token found in latest token entry!")
    return token

def fetch_agreement(member_id, bearer_token):
    url = f"{API_BASE}/api/members/{member_id}/agreement"  # Ensure no /v0/
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Accept": "application/json",
        "API-version": "1"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"[WARN] {member_id}: HTTP {resp.status_code} - {resp.text}")
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
    # Load as DataFrame
    if os.path.exists(CONTACT_LIST_XLSX):
        df = pd.read_excel(CONTACT_LIST_XLSX, dtype=str)
    else:
        df = pd.read_csv(CONTACT_LIST_CSV, dtype=str)
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
    # Save updated contact list
    print("Saving updated contact list (CSV and XLSX)...")
    df.to_csv(CONTACT_LIST_CSV, index=False)
    df.to_excel(CONTACT_LIST_XLSX, index=False)
    print("Done! Master contact list updated with agreement info.")

if __name__ == "__main__":
    main() 