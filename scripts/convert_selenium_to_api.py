from datetime import datetime, timedelta
from services.api.enhanced_clubos_client import EnhancedClubOSAPIClient
from services.api.clubos_api_client import ClubOSAPIAuthentication
from config.secrets import get_clubos_credentials

creds = get_clubos_credentials()
username = creds["username"]
password = creds["password"]

auth = ClubOSAPIAuthentication()
if not auth.login(username, password):
    print("❌ ClubOS authentication failed")
    exit(1)

client = EnhancedClubOSAPIClient(auth)

# 1. Search for Jeremy Mayo
search_results = client.search_members("Jeremy Mayo")
if not search_results:
    print("❌ Could not find member 'Jeremy Mayo'")
    exit(1)

member = search_results[0]
member_id = member.get("id") or member.get("memberId")
if not member_id:
    print(f"❌ Could not extract member ID from search result: {member}")
    exit(1)
print(f"[INFO] Found Jeremy Mayo with member ID: {member_id}")

# 2. Create a personal training session for tomorrow at 9am
now = datetime.now()
tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
session_data = {
    "title": "Personal Training",
    "date": tomorrow,
    "start_time": "09:00",
    "end_time": "10:00",
    "description": "Personal training session for Jeremy Mayo",
    "schedule": "My schedule",
    "member_id": member_id
}

result = client.create_calendar_session(session_data)
print("API create_calendar_session result:", result) 