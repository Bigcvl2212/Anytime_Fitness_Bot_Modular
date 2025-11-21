# ClubOS Message Polling - Gym-Agnostic Configuration

## Overview

The message polling system is **completely gym-agnostic** and requires **no hardcoded values**. It automatically detects the logged-in manager and polls their inbox.

## How It Works

### 1. Auto-Configuration Process

When the system starts:

```python
# main_app.py initializes the polling service
app.message_poller = RealTimeMessageSync(
    clubos_client=app.messaging_client,  # Already authenticated
    db_manager=app.db_manager,
    socketio=socketio,
    poll_interval=10  # 10 seconds
)

# Auto-configuration happens automatically:
# 1. Reads logged_in_user_id from authenticated ClubOS client
# 2. Adds this user ID to polling list
# 3. Starts polling that user's inbox
# 4. Logs configuration for verification
```

### 2. What Gets Auto-Detected

The system automatically detects:
- **Manager User ID** - From `clubos_client.logged_in_user_id`
- **Club ID** - From `clubos_client.club_id`
- **Club Location ID** - From `clubos_client.club_location_id`
- **Club Name** - From authentication response
- **Manager Name** - From user profile

### 3. Zero Configuration Required

**No hardcoded values anywhere:**
- ❌ No hardcoded user IDs (like "187032782")
- ❌ No hardcoded club IDs (like "291")
- ❌ No hardcoded location IDs (like "3586")
- ✅ Everything is dynamically detected from authentication

## Deployment to New Gym

### Prerequisites

1. ClubOS credentials for the gym manager
2. Database setup (SQLite or PostgreSQL)
3. Environment variables or config file

### Steps

1. **Update Credentials File**

```python
# config/clubhub_credentials_clean.py
CLUBOS_USERNAME = "new.gym.manager@email.com"
CLUBOS_PASSWORD = "their_password"
```

2. **Run the Application**

```bash
python run_dashboard.py
```

3. **Verify Auto-Configuration**

Check the logs for:
```
✅ Auto-configured polling for logged-in manager: 123456789
📍 Club ID: 456
📍 Location ID: 7890
🔄 Message polling loop started
```

That's it! The system automatically:
- Authenticates as the gym manager
- Detects their user ID
- Polls their inbox every 10 seconds
- Stores messages in the database
- Broadcasts to connected WebSocket clients

## API Endpoints

### Manual Sync
```bash
POST /api/inbox/polling/sync-now/{owner_id}
```

### Get Polling Status
```bash
GET /api/inbox/polling/status
```

### Start/Stop Polling
```bash
POST /api/inbox/polling/start
POST /api/inbox/polling/stop
```

### Add Additional Owners (Optional)
```bash
POST /api/inbox/polling/add-owner/{owner_id}
```

## Configuration Options

### Poll Interval

Adjust the polling frequency in `main_app.py`:

```python
app.message_poller = RealTimeMessageSync(
    clubos_client=app.messaging_client,
    db_manager=app.db_manager,
    socketio=socketio,
    poll_interval=30  # Poll every 30 seconds (default: 10)
)
```

### Multiple Inboxes (Optional)

If you want to poll multiple user inboxes:

```python
# After initialization, add more owners
app.message_poller.add_owner("additional_user_id_1")
app.message_poller.add_owner("additional_user_id_2")
```

## Testing

### Test Auto-Configuration

```bash
python test_message_polling.py
```

This test verifies:
1. ✅ Authentication with ClubOS
2. ✅ Auto-detection of manager user ID
3. ✅ Automatic polling configuration
4. ✅ Message fetching
5. ✅ Database storage

### Expected Output

```
🧪 Testing ClubOS Message Polling Auto-Configuration
================================================================================
📋 Step 1: Authenticating with ClubOS...
✅ Authentication successful
   - Logged-in User ID: 187032782
   - Club ID: 291
   - Club Location ID: 3586

📋 Step 2: Initializing database manager...
✅ Database manager initialized

📋 Step 3: Initializing message sync (should auto-configure)...
✅ Auto-configured polling for logged-in manager: 187032782
📍 Club ID: 291
📍 Location ID: 3586

📋 Step 4: Verifying auto-configuration...
✅ Polling Status:
   - Running: False
   - Poll Interval: 10s
   - Owner Count: 1
   - Owners: ['187032782']

📋 Step 5: Testing manual message sync...
✅ Manual sync successful
   - Messages fetched: 15
   - Timestamp: 2025-10-06T...

================================================================================
📊 TEST SUMMARY
================================================================================
✅ Authentication: SUCCESS
✅ Auto-Configuration: SUCCESS
✅ Manager Inbox Detection: SUCCESS
✅ Message Sync: SUCCESS

🎯 System is ready to poll manager inbox automatically
📬 Monitoring inbox for: User ID 187032782
🏢 Club: 291, Location: 3586
================================================================================
```

## Troubleshooting

### No Auto-Configuration

**Symptom:**
```
⚠️ Could not auto-detect logged-in user - polling will need manual configuration
```

**Cause:** Authentication failed or ClubOS client not properly initialized

**Solution:**
1. Verify credentials in `config/clubhub_credentials_clean.py`
2. Check ClubOS authentication logs
3. Ensure `clubos_client.authenticate()` is called before creating `RealTimeMessageSync`

### Empty Owner List

**Symptom:**
```
Owner Count: 0
Owners: []
```

**Cause:** Auto-configuration failed to detect user ID

**Solution:**
1. Check authentication succeeded
2. Verify `clubos_client.logged_in_user_id` is set
3. Manually add owner: `message_poller.add_owner(user_id)`

### No Messages Fetched

**Symptom:**
```
Messages fetched: 0
```

**Possible Causes:**
1. No new messages in inbox (expected)
2. Authentication expired
3. Incorrect endpoint or payload

**Solution:**
1. Send a test message to the manager's inbox
2. Check ClubOS API response in logs
3. Verify endpoint is accessible

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              main_app.py                              │  │
│  │  1. Initialize ClubOS client                          │  │
│  │  2. Authenticate (auto-detects user ID)               │  │
│  │  3. Initialize RealTimeMessageSync                    │  │
│  │  4. Start polling (10s intervals)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        RealTimeMessageSync                            │  │
│  │  • Auto-configures from clubos_client                 │  │
│  │  • Polls manager inbox every 10s                      │  │
│  │  • Detects new messages (incremental)                 │  │
│  │  • Stores in database                                 │  │
│  │  • Broadcasts via WebSocket                           │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↓                    ↓                    ↓          │
│  ┌──────────┐        ┌──────────┐        ┌──────────┐     │
│  │ Database │        │ WebSocket│        │  Phase 2 │     │
│  │  SQLite  │        │ Clients  │        │ AI Agent │     │
│  └──────────┘        └──────────┘        └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

Messages are stored with full ClubOS metadata:

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT UNIQUE,
    content TEXT,
    subject TEXT,
    from_user TEXT,
    recipient_name TEXT,
    timestamp TEXT,
    status TEXT,
    message_type TEXT,
    owner_id TEXT,              -- Auto-detected manager ID
    member_id TEXT,
    conversation_id TEXT,
    channel TEXT,
    delivery_status TEXT,
    
    -- AI Agent columns (Phase 1)
    ai_processed INTEGER DEFAULT 0,
    ai_responded INTEGER DEFAULT 0,
    ai_confidence_score REAL,
    ai_action_taken TEXT,
    ai_response_sent_at TIMESTAMP,
    
    -- Threading
    thread_id TEXT,
    requires_response INTEGER DEFAULT 0,
    
    -- ClubOS metadata
    clubos_message_id TEXT,
    clubos_conversation_id TEXT,
    from_member_id TEXT,
    from_member_name TEXT,
    to_staff_name TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Next Steps (Phase 2)

- [ ] AI agent integration for automatic responses
- [ ] Sentiment analysis of messages
- [ ] Priority scoring for urgent messages
- [ ] Automatic categorization (billing, scheduling, general)
- [ ] Smart routing to appropriate staff members
- [ ] Template-based response generation

## Support

For questions or issues:
1. Check application logs
2. Run `test_message_polling.py` for diagnostics
3. Review this documentation
4. Check Phase 1 implementation status in `PHASE_1_SUMMARY.md`
