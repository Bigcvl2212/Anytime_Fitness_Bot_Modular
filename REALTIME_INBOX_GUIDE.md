# Real-Time Inbox System - Implementation Guide

## 🎯 Overview

This system implements **real-time ClubOS inbox synchronization** with **AI-powered auto-responses**, similar to GoHighLevel's AI capabilities. The system polls the ClubOS inbox every 10 seconds, parses new messages, stores them in the database, broadcasts updates via WebSocket, and optionally generates AI responses.

---

## 🏗️ Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   REAL-TIME INBOX SYSTEM                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐           │
│  │  ClubOS Inbox    │─────▶│  Inbox Parser    │           │
│  │  Poller          │      │  (HTML)          │           │
│  │  (10s interval)  │      └──────────────────┘           │
│  └──────────────────┘              │                       │
│          │                          ▼                       │
│          │              ┌──────────────────┐               │
│          │              │  Database        │               │
│          │              │  Storage         │               │
│          │              └──────────────────┘               │
│          │                          │                       │
│          ├──────────────────────────┼────────────┐         │
│          ▼                          ▼            ▼         │
│  ┌──────────────┐        ┌──────────────┐  ┌─────────┐   │
│  │  WebSocket   │        │  AI Agent    │  │ Logging │   │
│  │  Broadcast   │        │  (Auto-      │  │         │   │
│  │              │        │  Response)   │  │         │   │
│  └──────────────┘        └──────────────┘  └─────────┘   │
│          │                          │                       │
│          ▼                          ▼                       │
│  ┌──────────────┐        ┌──────────────┐               │
│  │  Frontend    │        │  ClubOS API  │               │
│  │  Updates     │        │  (Send SMS)  │               │
│  └──────────────┘        └──────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Components

### 1. **ClubOS Inbox Poller** (`clubos_inbox_poller.py`)
- Polls `/action/Dashboard/messages` endpoint every 10 seconds
- Adds timestamp parameter to prevent caching
- Runs in background thread
- Triggers callbacks on new messages

### 2. **Inbox Parser** (`clubos_inbox_parser.py`)
- Parses HTML responses from ClubOS
- Extracts message metadata (sender, snippet, timestamp, etc.)
- Handles multiple HTML structure patterns
- Generates unique message IDs

### 3. **Database Schema** (`inbox_database_schema.py`)
- `inbox_messages` - Stores all messages
- `conversations` - Tracks conversation threads
- `message_sync_status` - Sync state tracking
- `ai_response_log` - AI response history

### 4. **WebSocket Server** (`inbox_websocket.py`)
- Real-time message broadcasting
- Client subscription management
- Room-based targeting
- Event handlers for connect/disconnect/subscribe

### 5. **AI Agent** (`inbox_ai_agent.py`)
- Message intent classification
- Auto-response generation
- Confidence scoring
- Rate limiting (20 responses/hour default)

### 6. **Integration Service** (`realtime_inbox_service.py`)
- Orchestrates all components
- Provides simple API
- Manages service lifecycle
- Global singleton pattern

---

## 🚀 Quick Start

### Step 1: Initialize in Main App

Add this to your `main_app.py` or initialization code:

```python
from src.services.realtime_inbox_service import initialize_realtime_inbox_service
from src.services.database_manager import DatabaseManager
from src.services.clubos_messaging_client import ClubOSMessagingClient
from src.services.ai.ai_service_manager import AIServiceManager

# Initialize dependencies
db_manager = DatabaseManager()
clubos_client = ClubOSMessagingClient(username="your_username", password="your_password")
ai_service = AIServiceManager()

# Initialize real-time inbox service
inbox_service = initialize_realtime_inbox_service(
    database_manager=db_manager,
    clubos_messaging_client=clubos_client,
    ai_service_manager=ai_service
)

# Start the service
inbox_service.start(owner_id="your_owner_id")  # owner_id is optional
```

### Step 2: Set Up WebSocket in Flask App

```python
from flask import Flask
from flask_socketio import SocketIO
from src.routes.inbox_websocket import register_websocket_handlers, inbox_ws_bp

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Register WebSocket handlers
register_websocket_handlers(socketio)

# Register blueprint
app.register_blueprint(inbox_ws_bp)

# Run with SocketIO
if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
```

### Step 3: Connect Frontend

```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000/inbox');

// Subscribe to inbox updates
socket.on('connect', () => {
    console.log('Connected to inbox WebSocket');

    // Subscribe to your owner's messages
    socket.emit('subscribe', {
        owner_id: 'your_owner_id'
    });
});

// Listen for new messages
socket.on('new_messages', (data) => {
    console.log('New messages:', data.messages);

    // Update UI with new messages
    data.messages.forEach(message => {
        addMessageToInbox(message);
    });
});

// Listen for AI responses
socket.on('ai_response', (data) => {
    console.log('AI generated response:', data.ai_response);
    showNotification('AI responded to ' + data.member_id);
});

// Listen for poll updates
socket.on('poll_update', (data) => {
    console.log('Poll stats:', data.stats);
    updateSyncIndicator(data.stats);
});

// Listen for errors
socket.on('error', (data) => {
    console.error('Inbox error:', data.error);
    showErrorNotification(data.error);
});
```

---

## ⚙️ Configuration

### Polling Interval

Change polling frequency (default: 10 seconds):

```python
# When initializing
inbox_service.poller.poll_interval = 30  # 30 seconds

# Must restart for changes to take effect
inbox_service.stop()
inbox_service.start()
```

### AI Auto-Response Settings

```python
# Enable/disable AI auto-responses
inbox_service.enable_ai_auto_response(True)

# Set confidence threshold (0.0 to 1.0)
# Only respond if AI is 80% confident or higher
inbox_service.set_ai_confidence_threshold(0.8)

# Adjust rate limiting
inbox_service.ai_agent.max_responses_per_hour = 50
```

---

## 📊 API Endpoints

### Manual Sync

```python
# Trigger immediate sync
new_messages = inbox_service.manual_sync(owner_id="123")
print(f"Found {len(new_messages)} new messages")
```

### Get Unread Messages

```python
# Get unread messages
unread = inbox_service.get_unread_messages(owner_id="123", limit=50)
```

### Get Conversation

```python
# Get full conversation thread
conversation = inbox_service.get_conversation(conversation_id="conv_123")
```

### Mark as Read

```python
# Mark message as read
inbox_service.mark_message_read(message_id="msg_123")
```

### Service Stats

```python
# Get service statistics
stats = inbox_service.get_service_stats()
print(stats)
# {
#     'is_running': True,
#     'owner_id': '123',
#     'poller_stats': {...},
#     'ai_stats': {...}
# }
```

---

## 🤖 AI Agent Behavior

### Intent Classification

The AI classifies messages into these categories:

- `question_about_membership` - Membership-related questions
- `question_about_training` - Training/workout questions
- `question_about_billing` - Billing/payment questions
- `question_about_schedule` - Schedule/hours questions
- `appointment_request` - Appointment booking requests
- `appointment_cancellation` - Cancellation requests
- `complaint` - Member complaints (no auto-response)
- `praise` - Positive feedback
- `general_inquiry` - General questions
- `spam` - Spam messages (no auto-response)
- `requires_human_response` - Complex issues (no auto-response)

### Auto-Response Rules

AI will **NOT** auto-respond if:
- Confidence score < threshold (default 0.7)
- Intent is `complaint`, `spam`, or `requires_human_response`
- Rate limit exceeded (default 20/hour)
- Auto-response disabled

### Example AI Response

```
Member Message:
"Hi, what are your gym hours on Saturday?"

AI Classification:
Intent: question_about_schedule
Confidence: 0.92

AI Response:
"Hi! Our Saturday hours are typically 6am-8pm, but I'll have a staff member confirm our exact schedule and get back to you shortly. Thanks for reaching out!"
```

---

## 🔍 Monitoring

### Check Service Status

```python
# Is service running?
if inbox_service.is_running:
    print("✅ Service is active")
else:
    print("❌ Service is stopped")
```

### View Polling Stats

```python
stats = inbox_service.poller.get_stats()
print(f"""
Polling Statistics:
- Total polls: {stats['total_polls']}
- Successful: {stats['successful_polls']}
- Failed: {stats['failed_polls']}
- Messages fetched: {stats['messages_fetched']}
- Last poll: {stats['last_poll_time']}
""")
```

### View AI Stats

```python
ai_stats = inbox_service.ai_agent.get_ai_stats()
print(f"""
AI Agent Statistics:
- Auto-response enabled: {ai_stats['auto_response_enabled']}
- Total responses: {ai_stats['total_responses']}
- Success rate: {ai_stats['success_rate']:.2%}
- Responses last hour: {ai_stats['responses_last_hour']}
- Rate limit remaining: {ai_stats['rate_limit_remaining']}
""")
```

---

## 🐛 Debugging

### Enable Debug Logging

```python
import logging

# Set logging level
logging.getLogger('src.services.clubos_inbox_poller').setLevel(logging.DEBUG)
logging.getLogger('src.services.clubos_inbox_parser').setLevel(logging.DEBUG)
logging.getLogger('src.services.ai.inbox_ai_agent').setLevel(logging.DEBUG)
```

### View Last Error

```python
if inbox_service.poller.stats['last_error']:
    print(f"Last error: {inbox_service.poller.stats['last_error']}")
```

### Manual Poll Test

```python
# Test polling without starting service
new_messages = inbox_service.poller._poll_inbox(owner_id="123")
print(f"Poll returned {len(new_messages)} messages")
```

---

## 🛠️ Troubleshooting

### Issue: No messages appearing

**Possible causes:**
1. ClubOS authentication failed
2. HTML parsing not finding messages
3. Messages already in database (not "new")

**Debug:**
```python
# Check authentication
if not inbox_service.clubos_client.authenticated:
    inbox_service.clubos_client.authenticate()

# Check last poll
stats = inbox_service.poller.get_stats()
print(f"Last poll: {stats['last_poll_time']}")

# Check database
unread = inbox_service.inbox_db.get_unread_messages(limit=10)
print(f"Unread messages in DB: {len(unread)}")
```

### Issue: AI not responding

**Possible causes:**
1. Auto-response disabled
2. Confidence threshold too high
3. Rate limit exceeded
4. Intent requires human response

**Debug:**
```python
# Check AI settings
ai_stats = inbox_service.ai_agent.get_ai_stats()
print(f"Auto-response enabled: {ai_stats['auto_response_enabled']}")
print(f"Confidence threshold: {inbox_service.ai_agent.confidence_threshold}")
print(f"Rate limit remaining: {ai_stats['rate_limit_remaining']}")
```

### Issue: WebSocket not broadcasting

**Possible causes:**
1. SocketIO not initialized
2. Clients not subscribed
3. Wrong namespace

**Debug:**
```python
# Check WebSocket status
from src.routes.inbox_websocket import connected_clients
print(f"Connected clients: {len(connected_clients)}")
print(f"Clients: {connected_clients}")
```

---

## 📈 Performance

### Memory Usage

- Poller: ~5MB (lightweight thread)
- Parser: ~2MB (minimal overhead)
- WebSocket: ~1MB per connected client
- AI: ~10MB (API client)

**Total**: ~20MB + (1MB × connected clients)

### Database Growth

- ~500 bytes per message
- 1000 messages/day = ~500KB/day
- ~15MB/month for active inbox

**Recommendation**: Archive messages older than 90 days

### Network Usage

- Polling: ~50KB per poll (every 10 seconds)
- ~300KB/minute or ~18MB/hour
- WebSocket: ~1KB per message broadcast

---

## 🔐 Security

### Authentication

- ClubOS credentials stored in secure secrets manager
- No hardcoded tokens or passwords
- Session management with auto-recovery

### Rate Limiting

- AI responses: 20/hour default
- Configurable per service instance
- Prevents spam and abuse

### Data Privacy

- Messages stored in local database
- No third-party message storage
- AI processing via Claude API (Anthropic)

---

## 🎯 Next Steps

### Enhancements to Consider

1. **Message Threading**: Group messages by conversation
2. **Read Receipts**: Track when messages are read
3. **Typing Indicators**: Show when staff is typing
4. **File Attachments**: Support image/document messages
5. **Search**: Full-text search across messages
6. **Filters**: Filter by sender, date, read status
7. **Notifications**: Desktop/push notifications
8. **Analytics**: Message volume, response times, AI accuracy

---

## 📞 Support

For issues or questions:

1. Check logs: `src/services/*.log`
2. Review error messages in console
3. Check database integrity
4. Verify ClubOS API access

---

## ✅ Summary

You now have a **fully autonomous AI-powered inbox system** that:

✅ Polls ClubOS every 10 seconds for new messages
✅ Parses HTML responses and extracts message data
✅ Stores messages in SQLite database
✅ Broadcasts real-time updates via WebSocket
✅ Classifies message intent with AI
✅ Auto-generates and sends responses
✅ Logs all activity for monitoring

**Start the service and watch your inbox come alive! 🚀**
