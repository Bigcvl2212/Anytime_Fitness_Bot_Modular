no# Phase 2: AI Agent Integration - Implementation Plan

## Overview

Build an autonomous AI agent that monitors the ClubOS inbox, analyzes incoming messages, and automatically generates appropriate responses using Claude/GPT.

## Prerequisites (✅ Complete from Phase 1)

- ✅ Real-time message polling (10s intervals)
- ✅ Database with AI tracking columns
- ✅ WebSocket broadcasting infrastructure
- ✅ Gym-agnostic configuration
- ✅ Message storage and threading

## Phase 2 Goals

### Core Functionality
1. **Message Classification** - Categorize messages by type and urgency
2. **Context Loading** - Load member data, billing status, appointment history
3. **Response Generation** - Use LLM to generate appropriate responses
4. **Confidence Scoring** - Rate AI confidence before sending
5. **Human Review** - Flag low-confidence responses for staff review
6. **Automatic Sending** - Send high-confidence responses automatically

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Real-Time Message Polling (Phase 1)             │
│  • Fetches new messages every 10s                            │
│  • Stores in database                                        │
│  • Broadcasts via WebSocket                                  │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                 AI Message Processor (NEW)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Message Classification                             │  │
│  │    - Billing/payment questions                        │  │
│  │    - Appointment scheduling                           │  │
│  │    - Cancellation/reschedule                          │  │
│  │    - General inquiry                                  │  │
│  │    - Complaint/issue                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 2. Context Loading                                    │  │
│  │    - Member profile                                   │  │
│  │    - Billing status                                   │  │
│  │    - Past due amount                                  │  │
│  │    - Recent appointments                              │  │
│  │    - Previous messages                                │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 3. Response Generation (Claude/GPT)                   │  │
│  │    - Load prompt template                             │  │
│  │    - Inject member context                            │  │
│  │    - Generate response                                │  │
│  │    - Calculate confidence score                       │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 4. Decision Logic                                     │  │
│  │    - High confidence (>0.8): Auto-send                │  │
│  │    - Medium (0.5-0.8): Queue for review               │  │
│  │    - Low (<0.5): Flag for staff                       │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│              Response Delivery (NEW)                         │
│  • Auto-send via ClubOS API                                  │
│  • Track delivery status                                     │
│  • Update database                                           │
│  • Notify UI via WebSocket                                   │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Steps

### Step 1: AI Message Classifier
**File**: `src/services/ai/message_classifier.py`

```python
class MessageClassifier:
    """Classifies incoming messages by type and urgency"""
    
    CATEGORIES = {
        'billing': ['payment', 'charge', 'bill', 'invoice', 'past due'],
        'scheduling': ['appointment', 'session', 'reschedule', 'cancel', 'confirm'],
        'membership': ['freeze', 'cancel', 'suspend', 'membership'],
        'general': ['question', 'info', 'help'],
        'complaint': ['issue', 'problem', 'unhappy', 'disappointed']
    }
    
    def classify(self, message: str) -> Dict:
        """Returns category, urgency, requires_response"""
```

### Step 2: Context Loader
**File**: `src/services/ai/context_loader.py`

```python
class MemberContextLoader:
    """Loads relevant member context for AI processing"""
    
    def load_context(self, member_id: str) -> Dict:
        """
        Returns:
        - Member profile
        - Billing status
        - Past due amount
        - Recent appointments
        - Recent messages
        """
```

### Step 3: AI Response Generator
**File**: `src/services/ai/response_generator.py`

```python
class AIResponseGenerator:
    """Generates responses using Claude/GPT"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet"):
        self.client = Anthropic(api_key=api_key)
        
    def generate_response(
        self,
        message: str,
        context: Dict,
        category: str
    ) -> Dict:
        """
        Returns:
        - response_text
        - confidence_score
        - reasoning
        - suggested_actions
        """
```

### Step 4: AI Agent Orchestrator
**File**: `src/services/ai/ai_agent.py`

```python
class AutonomousAIAgent:
    """Main AI agent that processes messages end-to-end"""
    
    def __init__(self, db_manager, clubos_client, api_key):
        self.classifier = MessageClassifier()
        self.context_loader = MemberContextLoader(db_manager)
        self.generator = AIResponseGenerator(api_key)
        self.clubos_client = clubos_client
        
    async def process_message(self, message: Dict) -> Dict:
        """
        Complete message processing pipeline:
        1. Classify
        2. Load context
        3. Generate response
        4. Decide action
        5. Execute (send or queue)
        """
```

### Step 5: Integration with Real-Time Sync
**File**: `src/services/real_time_message_sync.py` (UPDATE)

```python
def _trigger_ai_processing(self, messages: List[Dict]) -> None:
    """Send new messages to AI agent for processing"""
    for msg in messages:
        if self._should_ai_respond(msg):
            # Queue for async processing
            asyncio.create_task(
                self.ai_agent.process_message(msg)
            )
```

### Step 6: Review Dashboard
**File**: `templates/ai_review.html` (NEW)

- View pending AI responses
- See confidence scores
- Approve/reject/edit responses
- Manual override controls

### Step 7: API Endpoints
**File**: `src/routes/ai_agent.py` (NEW)

```python
# GET /api/ai/pending-reviews - Get responses awaiting review
# POST /api/ai/approve/{message_id} - Approve and send
# POST /api/ai/reject/{message_id} - Reject and flag for manual
# POST /api/ai/edit/{message_id} - Edit and send
# GET /api/ai/stats - AI performance metrics
# POST /api/ai/toggle - Enable/disable AI agent
```

## Configuration

### Environment Variables
```bash
# AI Configuration
AI_ENABLED=true
AI_MODEL=claude-3-sonnet-20240229
AI_API_KEY=your_anthropic_api_key
AI_AUTO_SEND_THRESHOLD=0.8
AI_REVIEW_THRESHOLD=0.5

# Safety Settings
AI_MAX_MESSAGES_PER_HOUR=50
AI_REQUIRE_APPROVAL_FOR_BILLING=true
AI_REQUIRE_APPROVAL_FOR_CANCELLATION=true
```

## Database Schema Updates

### New Tables

```sql
-- AI responses awaiting review
CREATE TABLE ai_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT,
    response_text TEXT,
    confidence_score REAL,
    category TEXT,
    reasoning TEXT,
    suggested_actions TEXT,
    status TEXT, -- pending, approved, rejected, sent
    reviewed_by TEXT,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI performance metrics
CREATE TABLE ai_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    messages_processed INTEGER,
    auto_sent INTEGER,
    reviewed INTEGER,
    rejected INTEGER,
    avg_confidence REAL,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Prompt Templates

### Base System Prompt
```
You are an AI assistant helping manage an Anytime Fitness gym.
You respond to member messages professionally and helpfully.

RULES:
- Be friendly but professional
- Keep responses concise (2-3 sentences)
- For billing issues, provide specific amounts and dates
- For scheduling, offer 2-3 available time slots
- Always include manager's name: Jeremy Mayo
- Never make promises about refunds without approval
- Flag urgent issues for immediate staff attention

CONTEXT:
{member_context}

MESSAGE TO RESPOND TO:
{member_message}

Generate a response that:
1. Addresses the member's concern
2. Is factually accurate based on the context
3. Maintains a helpful tone
4. Includes clear next steps if needed
```

## Testing Strategy

### Unit Tests
- Message classification accuracy
- Context loading completeness
- Response generation quality
- Confidence scoring reliability

### Integration Tests
- End-to-end message processing
- Database updates
- ClubOS API sending
- WebSocket notifications

### Manual Testing
- Review AI responses for tone
- Verify factual accuracy
- Test edge cases
- Measure response times

## Success Metrics

### Performance
- **Response Time**: <5 seconds from message receipt to response generation
- **Accuracy**: >90% of responses factually correct
- **Confidence**: Average confidence score >0.75
- **Auto-Send Rate**: >60% of messages auto-sent (high confidence)

### Quality
- **Member Satisfaction**: Track positive/negative responses
- **Staff Workload**: 50% reduction in manual message responses
- **Error Rate**: <5% of AI responses require correction

## Rollout Plan

### Stage 1: Read-Only (Week 1)
- AI processes messages
- Generates responses
- Stores in database
- NO automatic sending
- Staff reviews all responses

### Stage 2: Limited Auto-Send (Week 2)
- Auto-send only for:
  - Appointment confirmations
  - General info requests
  - Simple scheduling questions
- Require approval for:
  - Billing issues
  - Cancellations
  - Complaints

### Stage 3: Full Automation (Week 3+)
- Auto-send for all high-confidence responses
- Continuous monitoring
- Regular review sessions
- A/B testing of prompt variations

## Risk Mitigation

### Safety Measures
1. **Confidence Thresholds**: Never auto-send below 0.8
2. **Category Restrictions**: Always require approval for billing/cancellations
3. **Rate Limiting**: Max 50 messages per hour
4. **Human Oversight**: Daily review of all AI responses
5. **Kill Switch**: Instant disable via dashboard toggle

### Monitoring
- Real-time AI response dashboard
- Alert on confidence drops
- Track member feedback
- Log all AI decisions

## Timeline

- **Week 1**: Build classifier, context loader, response generator
- **Week 2**: Integrate with real-time sync, create review dashboard
- **Week 3**: Testing, prompt refinement, safety checks
- **Week 4**: Stage 1 rollout (read-only mode)
- **Week 5**: Stage 2 rollout (limited auto-send)
- **Week 6+**: Full automation with monitoring

## Next Steps

1. Set up Claude/GPT API access
2. Create message classification rules
3. Build context loading system
4. Implement response generator
5. Create review dashboard
6. Begin Stage 1 testing

---

**Ready to begin Phase 2 implementation?** Let's start with the AI message classifier!
