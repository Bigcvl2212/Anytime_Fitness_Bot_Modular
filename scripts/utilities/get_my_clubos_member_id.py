from config.secrets_local import get_secret
from src.services.api.clubos_api_client import ClubOSAPIClient
import re

if __name__ == "__main__":
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    print(f"Logging in as {username}...")
    client = ClubOSAPIClient()
    if not client.auth.login(username, password):
        print("❌ Authentication failed")
        exit(1)
    print("✅ Authentication successful")

    # Go to dashboard
    dashboard_url = "https://anytime.club-os.com/action/Dashboard/view"
    print(f"Fetching dashboard: {dashboard_url}")
    resp = client.auth.session.get(dashboard_url, headers=client.auth.get_headers(), timeout=15, verify=False)
    if resp.status_code != 200:
        print(f"❌ Failed to load dashboard: {resp.status_code}")
        exit(1)

    html = resp.text
    # Try to find a member/profile link for the logged-in user
    print("Searching for member/profile links...")
    matches = re.findall(r'href=["\"]/action/Members/profile/(\d+)["\"]', html)
    if matches:
        print(f"✅ Found member profile link(s): {matches}")
        print(f"Your ClubOS member ID (prospectID) is: {matches[0]}")
    else:
        # Try to find data-member-id or similar
        match = re.search(r'data-member-id=["\"](\d+)["\"]', html)
        if match:
            print(f"✅ Found data-member-id: {match.group(1)}")
            print(f"Your ClubOS member ID (prospectID) is: {match.group(1)}")
        else:
            print("❌ Could not find your member ID (prospectID) in the dashboard HTML.") 