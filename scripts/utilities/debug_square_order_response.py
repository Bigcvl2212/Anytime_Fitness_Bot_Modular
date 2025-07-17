from square.client import Square
from config.secrets import get_secret
from config.constants import SQUARE_SANDBOX_ACCESS_TOKEN_SECRET, SQUARE_ENVIRONMENT, SQUARE_PRODUCTION_ACCESS_TOKEN_SECRET, SQUARE_LOCATION_ID_SECRET

print(f"SQUARE_ENVIRONMENT: {SQUARE_ENVIRONMENT}")

# Get token
if SQUARE_ENVIRONMENT == 'sandbox':
    token_name = SQUARE_SANDBOX_ACCESS_TOKEN_SECRET
else:
    token_name = SQUARE_PRODUCTION_ACCESS_TOKEN_SECRET
access_token = get_secret(token_name)

if not access_token:
    print(f"ERROR: No Square access token found for secret: {token_name}")
    exit(1)
else:
    print(f"Square token starts with: {access_token[:6]}... (length: {len(access_token)})")

client = Square(token=access_token)
orders_api = client.orders
location_id = get_secret(SQUARE_LOCATION_ID_SECRET)

if not location_id:
    print(f"ERROR: No Square location ID found for secret: {SQUARE_LOCATION_ID_SECRET}")
    exit(1)
else:
    print(f"Square location ID: {location_id}")

order_request = {
    "location_id": location_id,
    "line_items": [
        {
            "name": "Debug Item",
            "base_price_money": {"amount": 100, "currency": "USD"},
            "quantity": "1"
        }
    ]
}

try:
    resp = orders_api.create(order=order_request)
    print("Attributes:", dir(resp))
    print("__dict__:", resp.__dict__)
    print("repr:", repr(resp))
    print("str:", str(resp))
except Exception as e:
    print("Exception:", e) 