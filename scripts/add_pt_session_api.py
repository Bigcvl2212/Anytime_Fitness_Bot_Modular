import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
try:
    from services.api.enhanced_clubos_client import EnhancedClubOSAPIClient
    from services.api.clubos_api_client import ClubOSAPIAuthentication
    from config.secrets import get_clubos_credentials
except Exception as e:
    print(f"[IMPORT ERROR] {e}")
    sys.exit(1)

print("[DEBUG] Starting ClubOS API session creation script...")

# Step 1: Authenticate
try:
    creds = get_clubos_credentials()
    username = creds["username"]
    password = creds["password"]
    print(f"[DEBUG] Loaded credentials for user: {username}")
except Exception as e:
    print(f"[ERROR] Failed to load credentials: {e}")
    sys.exit(1)

try:
    auth = ClubOSAPIAuthentication()
    if not auth.login(username, password):
        print("❌ ClubOS authentication failed")
        sys.exit(1)
    print("[DEBUG] Authenticated with ClubOS API")
except Exception as e:
    print(f"[ERROR] Authentication error: {e}")
    sys.exit(1)

try:
    client = EnhancedClubOSAPIClient(auth)
    print("[DEBUG] EnhancedClubOSAPIClient initialized")
except Exception as e:
    print(f"[ERROR] Failed to initialize EnhancedClubOSAPIClient: {e}")
    sys.exit(1)

# Step 2: Use Grace Sphatt's ProspectID directly
member_id = '62987140'
print(f"[INFO] Using Grace Sphatt's ProspectID (member_id): {member_id}")

# Step 3: Create a session for tomorrow at 9am
try:
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    session_data = {
        "title": "Personal Training Session (API)",
        "date": tomorrow.strftime("%Y-%m-%d"),
        "start_time": "09:00",
        "end_time": "10:00",
        "description": "PT session for Jeremy Mayo",
        "schedule": "My schedule"
    }
    print(f"[DEBUG] Creating session: {session_data}")
    create_result = client.create_calendar_session(session_data)
    print(f"[INFO] Session creation result: {create_result}")
    # Print and save full response for debugging
    full_response = create_result.get('response', '')
    print(f"[DEBUG] Full session creation response (first 1000 chars):\n{full_response[:1000]}\n")
    with open('session_creation_response.html', 'w', encoding='utf-8') as f:
        f.write(full_response)
    print("[DEBUG] Full session creation response saved to session_creation_response.html")
    if not create_result.get("success"):
        print("❌ Failed to create session")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Session creation error: {e}")
    sys.exit(1)

# Step 4: Find the new session's ID (fetch sessions for tomorrow)
try:
    print(f"[DEBUG] Fetching sessions for {tomorrow.strftime('%Y-%m-%d')}")
    sessions = client.get_calendar_sessions(date=tomorrow.strftime("%Y-%m-%d"))
    print(f"[DEBUG] Sessions found: {sessions}")
    created_session = None
    for s in sessions:
        if s.get("title") == session_data["title"] and s.get("start_time", "09:00").startswith("09"):
            created_session = s
            break
    if not created_session:
        print("❌ Could not find the created session for tomorrow at 9am")
        sys.exit(1)
    session_id = created_session.get("id")
    print(f"[INFO] Created session_id: {session_id}")
except Exception as e:
    print(f"[ERROR] Session lookup error: {e}")
    sys.exit(1)

# Step 5: Add Jeremy Mayo to the session
try:
    print(f"[DEBUG] Adding member {member_id} to session {session_id}")
    add_result = client.add_member_to_session(session_id, member_id)
    print(f"[INFO] Add member result: {add_result}")
    if add_result.get("success"):
        print("✅ Jeremy Mayo added to session via API!")
    else:
        print("❌ Failed to add Jeremy Mayo to session")
except Exception as e:
    print(f"[ERROR] Add member error: {e}")
    sys.exit(1) 