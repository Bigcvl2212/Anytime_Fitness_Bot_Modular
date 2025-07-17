from config.secrets import get_secret
from config.constants import SQUARE_SANDBOX_ACCESS_TOKEN_SECRET

token = get_secret(SQUARE_SANDBOX_ACCESS_TOKEN_SECRET)
print('Token format check:')
print(f'  Starts with EAAA: {token.startswith("EAAA")}')
print(f'  Length: {len(token)}')
print(f'  First 10 chars: {token[:10]}')
print(f'  Last 10 chars: {token[-10:]}')
print(f'  Contains only alphanumeric: {token.isalnum()}') 