from square.client import Square
from config.secrets_local import get_secret

# Get the production token
token = get_secret("square-production-access-token")
location_id = get_secret("square-production-location-id")

client = Square(token=token)

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

try:
    order_result = client.orders.create(order=order_request)
    print("✅ Order created successfully!")
    print("Response type:", type(order_result))
    print("Response attributes:", [attr for attr in dir(order_result) if not attr.startswith('_')])
    print("Response dict:", order_result.__dict__)
    print("Response str:", str(order_result))
    print("Response repr:", repr(order_result))
    
    # Try to access the order ID
    if hasattr(order_result, 'order'):
        print("Has 'order' attribute:", order_result.order)
    if hasattr(order_result, 'data'):
        print("Has 'data' attribute:", order_result.data)
    if hasattr(order_result, 'body'):
        print("Has 'body' attribute:", order_result.body)
        
except Exception as e:
    print(f"❌ Error: {e}") 