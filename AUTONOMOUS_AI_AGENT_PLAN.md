# Autonomous AI Sales Agent - Complete Rebuild Plan

## Current Problems (Your Assessment)

### 1. **AI Agent Issues**
- ❌ Not autonomous - requires constant direction
- ❌ Sends terrible messages ("payment reminder for past due balance")
- ❌ Doesn't converse naturally with people
- ❌ Doesn't take proactive actions on its own
- ❌ Nothing like GoHighLevel's autonomous AI

### 2. **Inbox/Messaging Issues** ⚠️ **BLOCKING EVERYTHING**
- ❌ Not synced with ClubOS in real-time
- ❌ Doesn't show newest messages
- ❌ Doesn't update as new messages come in (no live polling)
- ❌ Static/stale inbox view

### 3. **Root Cause**
**The inbox foundation is broken, so even if we had the best AI in the world, it wouldn't work because it can't see current conversations.**

---

## Solution Architecture: GoHighLevel-Style Autonomous AI

### Phase 1: Fix Inbox Foundation (MUST DO FIRST)
**Goal:** Real-time ClubOS inbox sync like native ClubOS interface

#### 1.1 Real-Time Message Polling System
```python
# New file: src/services/real_time_message_sync.py

class RealTimeMessageSync:
    """
    Continuously polls ClubOS for new messages
    Similar to how ClubOS web interface works
    """
    
    def __init__(self, clubos_client, db_manager, poll_interval=10):
        self.clubos_client = clubos_client
        self.db_manager = db_manager
        self.poll_interval = poll_interval  # seconds
        self.running = False
        self.last_message_id = None
        
    async def start_polling(self):
        """Start continuous background polling"""
        self.running = True
        
        while self.running:
            try:
                # Fetch latest messages from ClubOS
                new_messages = await self.fetch_new_messages()
                
                if new_messages:
                    # Store in database
                    await self.store_messages(new_messages)
                    
                    # Trigger AI agent to process new messages
                    await self.trigger_ai_processing(new_messages)
                    
                    # Broadcast to web UI (WebSocket/SSE)
                    await self.broadcast_to_ui(new_messages)
                
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Polling error: {e}")
                await asyncio.sleep(30)  # Back off on error
    
    async def fetch_new_messages(self):
        """Fetch only NEW messages since last check"""
        # Use ClubOS API to get messages after last_message_id
        # This is incremental sync, not full refresh
        pass
    
    async def trigger_ai_processing(self, messages):
        """Automatically send new messages to AI agent"""
        for msg in messages:
            # Check if message requires AI response
            if self.should_ai_respond(msg):
                await current_app.ai_agent.process_incoming_message(msg)
```

#### 1.2 WebSocket/Server-Sent Events for Real-Time UI Updates
```python
# New file: src/routes/messaging_realtime.py

from flask_socketio import SocketIO, emit

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    """Client connected to real-time messaging"""
    logger.info("Client connected for real-time inbox")

@socketio.on('request_inbox_sync')
def handle_inbox_sync_request():
    """Client requests latest inbox data"""
    messages = get_latest_messages()
    emit('inbox_update', messages)

def broadcast_new_message(message):
    """Broadcast new message to all connected clients"""
    socketio.emit('new_message', message, broadcast=True)
```

#### 1.3 Inbox Message Storage Schema
```sql
-- Enhanced message storage with conversation threading

CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,  -- Group messages by conversation
    thread_id TEXT,                 -- Thread within conversation
    
    -- Message content
    content TEXT NOT NULL,
    subject TEXT,
    
    -- Participants
    from_member_id TEXT,
    from_member_name TEXT,
    to_staff_name TEXT,
    
    -- Timestamps
    sent_at TIMESTAMP NOT NULL,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    
    -- Status tracking
    status TEXT DEFAULT 'unread',  -- unread, read, replied, archived
    requires_response BOOLEAN DEFAULT FALSE,
    ai_processed BOOLEAN DEFAULT FALSE,
    ai_responded BOOLEAN DEFAULT FALSE,
    
    -- AI interaction
    ai_response_sent_at TIMESTAMP,
    ai_confidence_score REAL,
    ai_action_taken TEXT,  -- JSON: what the AI did
    
    -- ClubOS metadata
    clubos_message_id TEXT UNIQUE,
    clubos_conversation_id TEXT,
    message_type TEXT,  -- incoming, outgoing, system
    
    -- Indexes for fast queries
    INDEX idx_conversation (conversation_id),
    INDEX idx_status (status),
    INDEX idx_requires_response (requires_response),
    INDEX idx_unread_requires_response (status, requires_response)
);

CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    member_id TEXT,
    member_name TEXT,
    last_message_at TIMESTAMP,
    last_message_preview TEXT,
    unread_count INTEGER DEFAULT 0,
    requires_response BOOLEAN DEFAULT FALSE,
    ai_handling BOOLEAN DEFAULT FALSE,
    conversation_status TEXT DEFAULT 'active',  -- active, resolved, archived
    tags TEXT  -- JSON: ['payment_issue', 'scheduling', etc.]
);
```

---

### Phase 2: Autonomous AI Agent (After Inbox is Fixed)

#### 2.1 AI Agent Architecture - GoHighLevel Style
```python
# New file: src/services/ai/autonomous_sales_agent.py

class AutonomousSalesAgent:
    """
    Fully autonomous AI agent that monitors inbox and takes actions
    Similar to GoHighLevel's AI assistant
    """
    
    def __init__(self, ai_service, messaging_client, db_manager, square_client):
        self.ai_service = ai_service
        self.messaging = messaging_client
        self.db = db_manager
        self.square = square_client
        
        # Agent personality and rules
        self.agent_config = {
            'name': 'Anytime Fitness AI Assistant',
            'personality': 'friendly, professional, helpful gym staff member',
            'autonomy_level': 'high',
            'auto_respond_to': [
                'questions',
                'scheduling_requests',
                'general_inquiries',
                'appointment_confirmations'
            ],
            'require_approval_for': [
                'payment_processing',
                'cancellations',
                'refunds',
                'contract_changes'
            ]
        }
    
    async def process_incoming_message(self, message: Dict) -> Dict:
        """
        Main processing loop for new messages
        This runs AUTOMATICALLY when new messages arrive
        """
        try:
            logger.info(f"🤖 AI Agent processing message from {message['from_member_name']}")
            
            # Step 1: Classify message intent
            intent = await self.classify_message_intent(message)
            
            # Step 2: Retrieve conversation context
            conversation = await self.get_conversation_context(message['conversation_id'])
            
            # Step 3: Get member data for personalization
            member_data = await self.get_member_data(message['from_member_id'])
            
            # Step 4: Decide if AI should respond automatically
            should_respond = self.should_auto_respond(intent, conversation, member_data)
            
            if should_respond:
                # Step 5: Generate contextual response
                response = await self.generate_response(message, intent, conversation, member_data)
                
                # Step 6: Send response automatically
                await self.send_message(
                    to_member_id=message['from_member_id'],
                    content=response['message'],
                    conversation_id=message['conversation_id']
                )
                
                # Step 7: Log AI action
                await self.log_ai_action(message, response, 'auto_responded')
                
            else:
                # Flag for human review
                await self.flag_for_human_review(message, intent)
            
            return {'success': True, 'action': 'processed'}
            
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def classify_message_intent(self, message: Dict) -> Dict:
        """
        Use AI to understand what the person wants
        Returns intent category and confidence
        """
        system_prompt = """You are a message classifier for a gym. Classify the intent:

Categories:
- question: General questions about gym, hours, services
- scheduling: Booking, rescheduling, canceling appointments
- payment_inquiry: Questions about billing, charges, invoices
- complaint: Issues, problems, dissatisfaction
- praise: Positive feedback, compliments
- confirmation: Confirming an appointment or action
- opt_out: Unsubscribe, stop messages
- other: Anything else

Return JSON: {"category": "question", "confidence": 0.95, "sub_intent": "hours"}"""
        
        user_message = f"""Message Content: {message['content']}
From: {message['from_member_name']}

Classify this message intent."""
        
        ai_response = await self.ai_service.send_message(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt
        )
        
        try:
            return json.loads(ai_response['response'])
        except:
            return {'category': 'other', 'confidence': 0.5}
    
    async def generate_response(self, message: Dict, intent: Dict, 
                              conversation: Dict, member_data: Dict) -> Dict:
        """
        Generate highly contextual, natural response
        Uses full conversation history and member data
        """
        system_prompt = f"""You are an AI assistant for Anytime Fitness gym. 

YOUR ROLE:
- Friendly, professional gym staff member
- Help members with questions, scheduling, and basic issues
- Never make promises about things you can't control
- If you don't know something, say so and offer to connect them with staff

CONVERSATION CONTEXT:
- Member: {member_data.get('name', 'Unknown')}
- Member Status: {member_data.get('status', 'Active')}
- Past Due Balance: ${member_data.get('amount_past_due', 0)}
- Last Visit: {member_data.get('last_check_in', 'Never')}

CONVERSATION HISTORY:
{json.dumps(conversation.get('messages', [])[-5:], indent=2)}

MESSAGE INTENT: {intent['category']} (confidence: {intent['confidence']})

RULES:
1. Be natural and conversational (like texting a friend)
2. Use their name occasionally
3. Keep responses concise (2-3 sentences max unless explaining something complex)
4. If they're past due, mention it GENTLY if relevant to conversation
5. Always end with clear next step or question

Generate a response that feels human, not robotic."""
        
        user_message = f"""Their message: "{message['content']}"

Generate your response."""
        
        ai_response = await self.ai_service.send_message(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt
        )
        
        return {
            'message': ai_response['response'],
            'intent_category': intent['category'],
            'confidence': intent['confidence']
        }
    
    def should_auto_respond(self, intent: Dict, conversation: Dict, member_data: Dict) -> bool:
        """
        Decide if AI should respond automatically or flag for human
        """
        # High confidence + safe categories = auto respond
        if intent['confidence'] >= 0.8 and intent['category'] in self.agent_config['auto_respond_to']:
            return True
        
        # Payment issues = flag for human (unless just asking a question)
        if intent['category'] == 'payment_inquiry' and 'past_due' not in member_data.get('status', '').lower():
            return True
        
        # Complaints = always flag for human
        if intent['category'] == 'complaint':
            return False
        
        # Low confidence = flag for human
        if intent['confidence'] < 0.6:
            return False
        
        return False
    
    async def proactive_outreach(self):
        """
        AI takes PROACTIVE actions (not just reactive)
        Runs on schedule (daily, weekly, etc.)
        """
        # Example: Payment reminders
        past_due_members = await self.get_past_due_members()
        
        for member in past_due_members:
            # Check if we already sent reminder recently
            if await self.should_send_payment_reminder(member):
                # Generate personalized message
                message = await self.generate_payment_reminder(member)
                
                # Send automatically
                await self.send_message(
                    to_member_id=member['id'],
                    content=message,
                    conversation_id=f"payment_reminder_{member['id']}"
                )
                
                # Log action
                await self.log_proactive_action('payment_reminder', member['id'])
    
    async def generate_payment_reminder(self, member: Dict) -> str:
        """Generate GOOD payment reminders (not "payment reminder for past due balance")"""
        system_prompt = """You are a friendly gym staff member sending a payment reminder.

RULES FOR PAYMENT REMINDERS:
1. Be friendly and understanding (not demanding)
2. Mention their name
3. State the amount clearly
4. Offer easy payment options
5. Thank them for being a member
6. Keep it brief but warm

BAD EXAMPLE:
"payment reminder for past due balance"

GOOD EXAMPLE:
"Hi Sarah! Just a quick heads up - we show a balance of $45.50 on your account from last month's training sessions. You can pay online anytime at our member portal, or just reply here and I'll help you get it sorted. Thanks for being an awesome member! 💪"

Generate a natural, friendly payment reminder."""
        
        user_message = f"""Member Info:
- Name: {member['name']}
- Amount Past Due: ${member['amount_past_due']}
- Last Payment: {member.get('last_payment_date', 'Unknown')}
- Membership Type: {member.get('membership_type', 'Standard')}

Generate the payment reminder message."""
        
        ai_response = await self.ai_service.send_message(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt
        )
        
        return ai_response['response']
```

---

### Phase 3: Implementation Roadmap

#### Week 1: Inbox Foundation
- [ ] Build real-time message polling service
- [ ] Implement WebSocket/SSE for UI updates
- [ ] Create enhanced message storage schema
- [ ] Build conversation threading logic
- [ ] Test real-time sync with ClubOS

#### Week 2: Basic Autonomous AI
- [ ] Build message intent classification
- [ ] Implement auto-respond decision logic
- [ ] Create contextual response generation
- [ ] Add conversation history to AI prompts
- [ ] Test AI responses for quality

#### Week 3: Proactive Actions
- [ ] Build scheduled proactive outreach system
- [ ] Implement payment reminder generation
- [ ] Add follow-up sequences
- [ ] Create AI action logging/analytics
- [ ] Test end-to-end autonomous behavior

#### Week 4: Polish & Monitoring
- [ ] Build AI performance dashboard
- [ ] Add human override/approval system
- [ ] Implement escalation rules
- [ ] Create AI training/improvement loop
- [ ] User testing & refinement

---

## Key Differences from Current System

### Current System (Broken)
- ❌ AI requires manual commands for every action
- ❌ Inbox is static, doesn't update in real-time
- ❌ AI generates terrible messages
- ❌ No proactive actions
- ❌ No conversation context

### New System (GoHighLevel-Style)
- ✅ AI monitors inbox automatically
- ✅ Real-time message sync (10-second polls)
- ✅ AI generates natural, contextual messages
- ✅ Proactive actions (payment reminders, follow-ups)
- ✅ Full conversation history in AI context
- ✅ Smart auto-respond vs. human escalation
- ✅ AI learns from interactions

---

## Technical Requirements

### Infrastructure
- **Background Workers**: Celery or similar for polling
- **WebSockets**: Flask-SocketIO for real-time UI
- **Database**: Enhanced schema for conversations
- **API Rate Limits**: Respect ClubOS API limits (polling frequency)

### AI Service
- **Claude API**: For natural language processing
- **Prompt Engineering**: High-quality prompts for natural responses
- **Context Windows**: Full conversation history in prompts
- **Confidence Scoring**: Know when to escalate to humans

### Monitoring
- **AI Action Logs**: Track every AI decision and message
- **Performance Metrics**: Response quality, auto-respond rate
- **Error Tracking**: Failed messages, API errors
- **Human Feedback Loop**: Staff can rate AI responses

---

## Next Steps

### Immediate (Do First)
1. **Fix inbox real-time sync** - Without this, nothing else matters
2. **Test ClubOS API polling** - Confirm we can fetch incremental messages
3. **Build WebSocket infrastructure** - Enable real-time UI updates

### Short-Term (After Inbox Works)
1. **Implement basic autonomous AI** - Auto-respond to simple questions
2. **Generate better messages** - Use context and personality
3. **Add proactive payment reminders** - Replace terrible current messages

### Long-Term (Once Core Works)
1. **AI learning system** - Improve from staff feedback
2. **Multi-channel support** - Email, SMS, ClubOS unified
3. **Advanced workflows** - Complex sequences and campaigns

---

## Success Metrics

### Inbox System
- ✅ New messages appear within 10 seconds
- ✅ Conversation threads are organized
- ✅ UI updates without page refresh
- ✅ No missed messages from ClubOS

### AI Agent
- ✅ Auto-responds to 70%+ of simple questions
- ✅ Staff rate AI messages 4/5+ stars
- ✅ Zero complaints about "robotic" messages
- ✅ Members engage naturally with AI (back-and-forth)
- ✅ Payment reminder response rate increases 50%+

---

**Bottom Line:** We need to build the inbox foundation FIRST, then layer on the autonomous AI. Right now we're trying to build a house on a broken foundation.
