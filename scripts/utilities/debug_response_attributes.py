from square.client import Square
from config.secrets import get_secret
from config.constants import SQUARE_PRODUCTION_ACCESS_TOKEN_SECRET, SQUARE_LOCATION_ID_SECRET

# Use production token and location
token = get_secret(SQUARE_PRODUCTION_ACCESS_TOKEN_SECRET)
location_id = get_secret(SQUARE_LOCATION_ID_SECRET)
client = Square(token=token)

try:
    # Try to create an order
    order_request = {
        "location_id": location_id,
        "line_items": [
            {
                "name": "Test Item",
                "base_price_money": {"amount": 100, "currency": "USD"},
                "quantity": "1"
            }
        ]
    }
    
    resp = client.orders.create(order=order_request)
    print("✅ Order created successfully!")
    print("Response type:", type(resp))
    print("Response attributes:", [attr for attr in dir(resp) if not attr.startswith('_')])
    print("Response dict:", resp.__dict__)
    print("Response str:", str(resp))
    print("Response repr:", repr(resp))
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e)}") 