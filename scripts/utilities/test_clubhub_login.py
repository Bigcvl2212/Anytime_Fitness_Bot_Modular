from services.authentication.clubhub_automated_login import ClubHubAutomatedLogin

try:
    from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
except ImportError:
    print("❌ Could not import ClubHub credentials!")
    exit(1)

print(f"Testing ClubHub login with email: {CLUBHUB_EMAIL}")
print(f"Password (first 2, last 2 chars): {CLUBHUB_PASSWORD[:2]}{'*'*(len(CLUBHUB_PASSWORD)-4)}{CLUBHUB_PASSWORD[-2:]}")

login = ClubHubAutomatedLogin()
success, auth_data = login.login(CLUBHUB_EMAIL, CLUBHUB_PASSWORD)

if success:
    print("✅ ClubHub login successful!")
    print(f"Bearer token: {auth_data.get('bearer_token', '')[:10]}... (length: {len(auth_data.get('bearer_token', ''))})")
else:
    print("❌ ClubHub login failed!")
    print(f"Auth data: {auth_data}") 