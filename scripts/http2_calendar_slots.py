import json
from datetime import datetime
import sys

try:
    import httpx
except ImportError:
    print("You need to install httpx: pip install httpx[http2]")
    sys.exit(1)

HAR_PATH = "charles_session.chls/Calendar_Endpoints.har"
BASE_URL = "https://anytime.club-os.com"

print(f"[DEBUG] Loading HAR file: {HAR_PATH}")
with open(HAR_PATH, "r", encoding="utf-8") as f:
    har_data = json.load(f)

headers = None
# Find the last /api/calendar/events request and extract all headers
for entry in reversed(har_data.get("log", {}).get("entries", [])):
    req = entry.get("request", {})
    url = req.get("url", "")
    if "/api/calendar/events" in url:
        headers = {h["name"]: h["value"] for h in req.get("headers", [])}
        break
if not headers:
    print("❌ No /api/calendar/events request with headers found in HAR file. Cannot authenticate.")
    sys.exit(1)
# Remove HTTP/2 pseudo-headers and problematic headers
for h in list(headers.keys()):
    if h.startswith(":") or h in ["Content-Length", "Host"]:
        headers.pop(h, None)

# Extract cookies
cookies = {}
if "cookie" in headers:
    cookie_str = headers["cookie"]
    for part in cookie_str.split(';'):
        if '=' in part:
            k, v = part.strip().split('=', 1)
            cookies[k] = v
    headers.pop("cookie")

print(f"[DEBUG] Using headers: {json.dumps({k: (v[:40]+'...') if len(v)>40 else v for k,v in headers.items()}, indent=2)}")
print(f"[DEBUG] Using cookies: {cookies}")

today = datetime.now().strftime('%Y-%m-%d')

with httpx.Client(http2=True, headers=headers, cookies=cookies, base_url=BASE_URL, timeout=15) as client:
    # Step 1: Prime the session by visiting /action/Calendar
    print("[DEBUG] Priming session with /action/Calendar ...")
    resp = client.get("/action/Calendar")
    print(f"[DEBUG] /action/Calendar status: {resp.status_code}")
    # Step 2: Make the API call
    print(f"[DEBUG] Fetching available slots for today ({today}) via /api/calendar/events ...")
    resp = client.get("/api/calendar/events", params={"date": today})
    print(f"[DEBUG] /api/calendar/events status: {resp.status_code}")
    if resp.status_code == 200:
        events = resp.json()
        available_slots = [e for e in events if e.get('status', '').lower() == 'available']
        print(f"\nAvailable slots for today ({today}):")
        if available_slots:
            for slot in available_slots:
                print(f"  - {slot.get('time')} | {slot}")
        else:
            print("  No available slots for today.")
    else:
        print(f"❌ Failed to fetch events: {resp.status_code}")
        print(f"Response: {resp.text}") 