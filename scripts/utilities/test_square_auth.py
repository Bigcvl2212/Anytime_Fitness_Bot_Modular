from square.client import Square
from config.secrets import get_secret
from config.constants import SQUARE_SANDBOX_ACCESS_TOKEN_SECRET

token = get_secret(SQUARE_SANDBOX_ACCESS_TOKEN_SECRET)
client = Square(token=token)

try:
    # Try to list locations first (simpler API call)
    locations = client.locations.list()
    print("✅ Authentication successful!")
    print(f"Found {len(locations.body.get('locations', []))} locations")
    for loc in locations.body.get('locations', []):
        print(f"  - {loc.get('name', 'Unknown')} (ID: {loc.get('id', 'Unknown')})")
except Exception as e:
    print(f"❌ Authentication failed: {e}") 