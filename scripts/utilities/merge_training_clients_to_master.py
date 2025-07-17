import pandas as pd
import os
import re

# Paths
TRAINING_CLIENTS_CSV = r"C:\Users\mayoj\Downloads\Clients_1752687122248.csv"
MASTER_CONTACT_LIST_XLSX = "master_contact_list_20250715_181714.xlsx"
MASTER_CONTACT_LIST_CSV = "master_contact_list_20250715_181714.csv"
OUTPUT_XLSX = "master_contact_list_20250715_181714.xlsx"  # Overwrite
OUTPUT_CSV = "master_contact_list_20250715_181714.csv"    # Overwrite
AUDIT_LOG = "training_merge_audit_log.txt"

# Load files
def load_csv(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"[ERROR] Could not read {path}: {e}")
        return None

def extract_prospect_id(profile_url):
    # Extract the last number from the profile URL
    match = re.search(r'/action/Delegate/(\d+)', str(profile_url))
    return match.group(1) if match else None

def main():
    # Load training clients
    training_df = load_csv(TRAINING_CLIENTS_CSV)
    if training_df is None:
        return
    # Extract ProspectID from Profile URL
    training_df['ProspectID'] = training_df['Profile'].apply(extract_prospect_id)
    # Load master contact list
    if os.path.exists(MASTER_CONTACT_LIST_XLSX):
        master_df = pd.read_excel(MASTER_CONTACT_LIST_XLSX)
    elif os.path.exists(MASTER_CONTACT_LIST_CSV):
        master_df = pd.read_csv(MASTER_CONTACT_LIST_CSV)
    else:
        print("[ERROR] Master contact list not found.")
        return
    # Convert ProspectID columns to string for merge
    training_df['ProspectID'] = training_df['ProspectID'].astype(str)
    master_df['ProspectID'] = master_df['ProspectID'].astype(str)
    # Merge on ProspectID
    if 'ProspectID' not in master_df.columns:
        print("[ERROR] 'ProspectID' column not found in master contact list.")
        return
    merged = pd.merge(master_df, training_df, on='ProspectID', how='outer', suffixes=('', '_training'))
    # Audit: log new/unmatched entries
    new_entries = merged[merged['ProspectID'].isin(training_df['ProspectID']) & ~merged['ProspectID'].isin(master_df['ProspectID'])]
    with open(AUDIT_LOG, 'w', encoding='utf-8') as f:
        f.write(f"New/unmatched training clients ({len(new_entries)}):\n")
        f.write(new_entries.to_string(index=False))
    # Save updated master contact list
    merged.to_excel(OUTPUT_XLSX, index=False)
    merged.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Merged training clients into master contact list. Audit log: {AUDIT_LOG}")

if __name__ == "__main__":
    main() 