import pandas as pd
from services.api.clubos_api_client import ClubOSAPIClient
# Remove the import for CONTACT_LIST_XLSX, CONTACT_LIST_CSV
# from config.constants import CONTACT_LIST_XLSX, CONTACT_LIST_CSV
CONTACT_LIST_XLSX = "master_contact_list_20250715_181714.xlsx"
CONTACT_LIST_CSV = "master_contact_list_20250715_181714.csv"
from bs4 import BeautifulSoup
import re

OUTPUT_CSV = "training_clients_list.csv"
OUTPUT_XLSX = "training_clients_list.xlsx"


def fetch_training_clients():
    client = ClubOSAPIClient()
    if not client.authenticate():
        print("❌ Failed to authenticate to ClubOS")
        return
    print("✅ Authenticated to ClubOS")
    # Fetch the Personal Training dashboard page
    url = f"{client.base_url}/action/Dashboard/PersonalTraining"
    resp = client.session.get(url, headers=client.auth.get_headers(), timeout=30, verify=False)
    if not resp.ok:
        print(f"❌ Failed to fetch Personal Training dashboard: {resp.status_code}")
        return
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Find all member rows/links
    members = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Look for member profile links
        match = re.search(r'/action/Members/(?:profile|view)/(\d+)', href)
        if match:
            member_id = match.group(1)
            name = link.get_text(strip=True)
            if name and member_id:
                members.append({
                    'Name': name,
                    'ProspectID': member_id
                })
    print(f"✅ Found {len(members)} training/single club clients.")
    df = pd.DataFrame(members)
    df.to_csv(OUTPUT_CSV, index=False)
    df.to_excel(OUTPUT_XLSX, index=False)
    # Merge with master contact list if possible
    try:
        master = pd.read_excel(CONTACT_LIST_XLSX)
        merged = pd.merge(master, df, on='ProspectID', how='outer', suffixes=('', '_training'))
        merged.to_excel(CONTACT_LIST_XLSX, index=False)
        merged.to_csv(CONTACT_LIST_CSV, index=False)
        print(f"✅ Updated master contact list with training clients.")
    except Exception as e:
        print(f"⚠️ Could not update master contact list: {e}")
    print(f"✅ Saved training client list to {OUTPUT_CSV} and {OUTPUT_XLSX}")

if __name__ == "__main__":
    fetch_training_clients() 