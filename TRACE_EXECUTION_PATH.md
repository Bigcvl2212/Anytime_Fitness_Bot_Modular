# Code Execution Trace: How Flask Gets Wrong Credentials

## Timeline: What Happens When Flask Starts

### 1. Application Factory Starts
```
File: src/main_app.py
Line: 231-238

def create_app():
    """Application factory pattern for creating Flask app"""
    # Load environment variables
    load_environment_variables()  # <-- STEP 1
```

### 2. Environment Variables Are Loaded From .env
```
File: src/config/environment_setup.py
Lines: 16-35

def load_environment_variables() -> bool:
    try:
        from dotenv import load_dotenv
        
        # Look for .env file in project root
        project_root = Path(__file__).parent.parent.parent
        env_file = project_root / '.env'
        
        if env_file.exists():
            load_dotenv(env_file)  # <-- STEP 2: Loads .env file
            logger.info(f"✅ Environment variables loaded from {env_file}")
            return True

RESULT:
  os.environ['CLUBOS_PASSWORD'] = 'W-!R6Bv9FgPnuB4'  # ← WRONG PASSWORD IS NOW IN os.environ
```

### 3. ClubOSMessagingClient Needs Credentials
```
File: src/main_app.py
Lines: 327-368

with app.app_context():
    # Initialize ClubOS Messaging Client
    try:
        try:
            from .services.clubos_messaging_client_simple import ClubOSMessagingClient
            from .services.authentication.secure_secrets_manager import SecureSecretsManager
        except ImportError:
            from services.clubos_messaging_client_simple import ClubOSMessagingClient
            from services.authentication.secure_secrets_manager import SecureSecretsManager

        secrets_manager = SecureSecretsManager()
        username = secrets_manager.get_secret('clubos-username')  # <-- STEP 3: Get username
        password = secrets_manager.get_secret('clubos-password')  # <-- STEP 4: Get password
        
        app.messaging_client = ClubOSMessagingClient(username, password)

EXECUTION PATH:
  secrets_manager.get_secret('clubos-password')
    ↓
  SecureSecretsManager.get_secret() at line 325
    ↓
  calls self.get_legacy_secret('clubos-password') at line 336
```

### 4. SecureSecretsManager.get_legacy_secret() Looks For Credentials
```
File: src/services/authentication/secure_secrets_manager.py
Lines: 338-373

def get_legacy_secret(self, secret_name: str, version: str = "latest") -> Optional[str]:
    """
    Get secret using the legacy format (for backwards compatibility)
    """
    
    # PRIORITY 1: ALWAYS try environment variables first (for local development)
    env_var_name = secret_name.upper().replace('-', '_')
    env_value = os.environ.get(env_var_name)
    
    # For 'clubos-password':
    # env_var_name = 'CLUBOS_PASSWORD'
    # env_value = os.environ.get('CLUBOS_PASSWORD')
    #           = 'W-!R6Bv9FgPnuB4'  ← FOUND IT (from .env file)

    if env_value:
        # Check if env value is a placeholder
        placeholder_values = [
            'your_clubos_username_here',
            'your_clubos_password_here',
            ...
        ]

        if env_value:
            # Don't use placeholder values
            if any(placeholder.lower() in env_value.lower() for placeholder in placeholder_values):
                logger.warning(f"⚠️ Placeholder value detected for {secret_name}, skipping")
                env_value = None
            else:
                logger.info(f"ℹ️ Using environment variable for {secret_name}")  # <-- THIS LOG
                return env_value  # <-- RETURNS WRONG PASSWORD
```

### 5. Wrong Password Is Used For Authentication
```
File: src/main_app.py
Lines: 346

app.messaging_client = ClubOSMessagingClient(username, password)
# username = 'j.mayo'
# password = 'W-!R6Bv9FgPnuB4'  ← WRONG PASSWORD!

# Later:
if app.messaging_client.authenticate():
    logger.info("✅ ClubOS messaging client authenticated successfully on startup")
else:
    logger.warning("⚠️ ClubOS messaging client authentication failed on startup - will retry on first use")
    # ← FAILS BECAUSE PASSWORD IS WRONG
```

---

## The Credential Lookup Chain

When Flask calls `secrets_manager.get_secret('clubos-password')`:

```
Entry Point:
  SecureSecretsManager.get_secret('clubos-password')
  ├─ Calls: get_legacy_secret('clubos-password')

Priority 1: Environment Variables
  ├─ Check: os.environ.get('CLUBOS_PASSWORD')
  ├─ Found: 'W-!R6Bv9FgPnuB4' (from .env file)
  ├─ Validate: Not a placeholder
  ├─ Log: "ℹ️ Using environment variable for clubos-password"
  └─ Return: 'W-!R6Bv9FgPnuB4'  ← STOPS HERE (WRONG!)

Priority 2 (Never Reached):
  ├─ Check: secrets_local.py
  ├─ Would Find: 'Ls$gpZ98L!hht.G' (CORRECT!)
  └─ But we never get here...

Priority 3 (Never Reached):
  ├─ Check: Google Secret Manager
  └─ Would Find: Nothing...
```

---

## Why secrets_local.py Isn't Used

The credential loading priority is:
1. **Environment variables** ← Flask always finds CLUBOS_PASSWORD from .env here and STOPS
2. Secrets_local.py ← Never reached because Step 1 found something
3. Google Secret Manager ← Never reached

This is by design in `secure_secrets_manager.py` line 349-373:
```python
# ALWAYS try environment variables first (for local development)
env_var_name = secret_name.upper().replace('-', '_')
env_value = os.environ.get(env_var_name)

# Check if env value is a placeholder
if env_value:
    # ... validation ...
    logger.info(f"ℹ️ Using environment variable for {secret_name}")
    return env_value  # <-- RETURNS IMMEDIATELY, doesn't check secrets_local.py
```

---

## Where Each File Gets Credentials

### 1. `.env` file (LOADED INTO os.environ)
```
CLUBOS_PASSWORD=W-!R6Bv9FgPnuB4  ← Flask finds this first
```

### 2. `secrets_local.py` (IGNORED because .env is found first)
```python
local_secrets = {
    "clubos-password": "Ls$gpZ98L!hht.G",  ← Never checked!
}
```

### 3. `src/config/clubhub_credentials.py` (ALSO IGNORED)
```python
CLUBOS_PASSWORD = os.getenv('CLUBOS_PASSWORD', "Ls$gpZ98L!hht.G")
# os.getenv('CLUBOS_PASSWORD') returns 'W-!R6Bv9FgPnuB4' from .env
# So this file also gets the wrong password
```

### 4. `config/clubhub_credentials.py` (ALSO IGNORED)
```python
CLUBOS_PASSWORD = os.getenv('CLUBOS_PASSWORD', "Ls$gpZ98L!hht.G")
# Same as above - gets wrong password from .env
```

---

## The Critical Moment

**File:** `src/services/authentication/secure_secrets_manager.py`
**Line:** 366-373
**Function:** `get_legacy_secret()`

```python
if env_value:  # ← env_value is 'W-!R6Bv9FgPnuB4'
    # Don't use placeholder values
    if any(placeholder.lower() in env_value.lower() for placeholder in placeholder_values):
        logger.warning(f"⚠️ Placeholder value detected for {secret_name}, skipping")
        env_value = None
    else:
        logger.info(f"ℹ️ Using environment variable for {secret_name}")
        return env_value  # ← RETURNS WRONG PASSWORD HERE
```

This is where Flask picks the WRONG password instead of continuing to check `secrets_local.py`.

---

## The Misleading Log

When you see in the logs:
```
ℹ️ Using environment variable for clubos-password
```

This comes from `secure_secrets_manager.py` line 372.

It looks like Flask is using system environment variables, but actually it's using the `.env` file that was loaded into `os.environ` during startup.

The log doesn't say "from .env file" - it just says "environment variable".

---

## The Fix: Update .env File

**Before:**
```
CLUBOS_PASSWORD=W-!R6Bv9FgPnuB4
```

**After:**
```
CLUBOS_PASSWORD=Ls$gpZ98L!hht.G
```

Then restart Flask, and the correct password will be found and used.

