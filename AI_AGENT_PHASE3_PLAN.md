# Phase 3: Sales AI Dashboard & Workflow Management

**Status:** 🟡 Planning  
**Priority:** HIGH  
**Dependencies:** Phase 1 ✅ Complete | Phase 2 ✅ Complete  
**Goal:** Transform sales AI dashboard into powerful workflow management hub with inbox-style interface

---

## 🎯 Objectives

1. **Redesign Sales AI Dashboard** to showcase Phase 2 autonomous workflows
2. **Inbox-Style Interface** similar to GMN with conversation threading
3. **Real-Time Workflow Monitoring** with live status updates
4. **Manager Notifications** for workflow decisions and escalations
5. **Mobile-Responsive Design** for on-the-go management

---

## 📋 Current State Analysis

### What Exists (sales_ai_dashboard.html)
- ❌ Basic chat interface (not leveraging Phase 2)
- ❌ Static metrics that don't update
- ❌ No workflow status/controls
- ❌ No conversation threading
- ❌ Doesn't show autonomous AI decisions
- ❌ No approval workflow for high-risk actions
- ❌ Poor mobile responsiveness

### What We Built (Phase 2)
- ✅ 6 autonomous workflows running on schedule
- ✅ Agent can execute complex multi-step tasks
- ✅ 17 tools across 4 categories
- ✅ Workflow execution history
- ✅ Rate limiting & error handling

### Inspiration: GMN Inbox
- ✅ Clean conversation view
- ✅ Message threading
- ✅ Real-time updates
- ✅ Mobile-first design
- ✅ Quick action buttons

---

## 🏗️ New Dashboard Architecture

### Layout: 3-Column Design

```
┌────────────────────────────────────────────────────────────────┐
│  🤖 Sales AI Dashboard                    [Workflows] [Tools]  │
├─────────────┬──────────────────────────┬──────────────────────┤
│             │                          │                      │
│  WORKFLOWS  │    AI CONVERSATION       │   WORKFLOW DETAILS   │
│             │                          │                      │
│ ┌─────────┐ │  ┌────────────────────┐ │  ┌────────────────┐ │
│ │Daily    │ │  │Agent: Analyzed     │ │  │ Daily Campaigns│ │
│ │Campaigns│ │  │35 past due members │ │  │ ─────────────  │ │
│ │●Running │ │  │Total: $8,165.26    │ │  │ Status: Active │ │
│ │         │ │  │                    │ │  │ Next: 6:00 AM  │ │
│ │Next:6AM │ │  │Recommendation:     │ │  │ Last: 8m ago   │ │
│ └─────────┘ │  │Send 12 high-value  │ │  │                │ │
│             │  │reminders today     │ │  │ [View History] │ │
│ ┌─────────┐ │  │                    │ │  │ [Run Now]      │ │
│ │Past Due │ │  │[Approve] [Modify]  │ │  │ [Pause]        │ │
│ │Monitor  │ │  └────────────────────┘ │  └────────────────┘ │
│ │○Paused  │ │                          │                      │
│ │         │ │  ┌────────────────────┐ │  ┌────────────────┐ │
│ │Every 1h │ │  │You: Show top 10    │ │  │ TOOLS USED     │ │
│ └─────────┘ │  │past due accounts   │ │  │ ────────────   │ │
│             │  └────────────────────┘ │  │ ✓ get_past_due │ │
│ [+ Manual   │                          │  │ ✓ send_reminder│ │
│    Task]    │  ┌────────────────────┐ │  │ ✓ lock_access  │ │
│             │  │Agent: Retrieved    │ │  └────────────────┘ │
│             │  │35 members...       │ │                      │
│             │  └────────────────────┘ │                      │
└─────────────┴──────────────────────────┴──────────────────────┘
```

---

## 🎨 Design Requirements

### 1. Workflow Panel (Left Sidebar)

**Features:**
- Live status indicators (●Running ○Paused ✓Complete)
- Next run time countdown
- Last execution summary
- Quick controls (Run Now, Pause, View History)
- Workflow health metrics (success rate, avg duration)

**Example Card:**
```
┌──────────────────────────┐
│ 🎯 Daily Campaigns       │
│ ─────────────────────    │
│ Status: ●Running         │
│ Next: 6:00 AM (in 3h)    │
│ Last: 8m ago ✓Success    │
│ Duration: 604s           │
│                          │
│ Recent Actions:          │
│ • Sent 20 SMS campaigns  │
│ • 294 green members      │
│ • 3,832 prospects        │
│                          │
│ [▶️ Run Now] [⏸️ Pause]   │
│ [📊 History] [⚙️ Config] │
└──────────────────────────┘
```

---

### 2. AI Conversation View (Center - Inbox Style)

**Features:**
- **Threaded Conversations:** Each workflow execution = thread
- **Real-Time Updates:** WebSocket for live agent thinking
- **Message Types:**
  - Workflow notifications
  - AI decisions & reasoning
  - Tool execution results
  - Manager requests (approval needed)
  - Manual commands
- **Rich Formatting:**
  - Tables for data (past due members, etc.)
  - Charts for analytics
  - Action buttons inline
  - Expandable details

**Message Examples:**

```html
<!-- Workflow Notification -->
<div class="ai-message workflow-notification">
  <div class="message-header">
    <span class="badge bg-primary">Daily Campaigns</span>
    <span class="timestamp">8 minutes ago</span>
  </div>
  <div class="message-body">
    <strong>Workflow Completed Successfully</strong>
    <p>Analyzed 3,832 prospects and 294 green members. 
       Sent 20 targeted campaigns via SMS and email.</p>
    <button class="btn btn-sm btn-outline-primary">View Details</button>
  </div>
</div>

<!-- AI Decision Requiring Approval -->
<div class="ai-message approval-request">
  <div class="message-header">
    <span class="badge bg-warning">⚠️ Approval Required</span>
    <span class="timestamp">2 minutes ago</span>
  </div>
  <div class="message-body">
    <strong>Lock Door Access for 34 Members?</strong>
    <p>Found 34 members with past due payments totaling $8,165.26.</p>
    
    <div class="approval-actions">
      <button class="btn btn-success">✓ Approve All</button>
      <button class="btn btn-primary">📋 Review List</button>
      <button class="btn btn-danger">✗ Deny</button>
    </div>
  </div>
</div>

<!-- Tool Execution Result -->
<div class="ai-message tool-result">
  <div class="message-header">
    <span class="badge bg-secondary">🔧 Tool: get_past_due_members</span>
    <span class="timestamp">1 minute ago</span>
  </div>
  <div class="message-body">
    <table class="table table-sm">
      <thead>
        <tr><th>Member</th><th>Amount</th><th>Days</th></tr>
      </thead>
      <tbody>
        <tr><td>John Doe</td><td>$248.43</td><td>45</td></tr>
        <tr><td>Jane Smith</td><td>$236.94</td><td>32</td></tr>
        <!-- ... -->
      </tbody>
    </table>
    <button class="btn btn-sm btn-primary">Export CSV</button>
  </div>
</div>
```

---

### 3. Workflow Details Panel (Right Sidebar)

**Features:**
- Selected workflow configuration
- Execution history (last 10 runs)
- Performance metrics
- Tool usage breakdown
- Error logs
- Quick settings

**Example:**
```
┌──────────────────────────┐
│ Daily Campaigns          │
│ ──────────────────────   │
│ Schedule: Daily at 6 AM  │
│ Status: ●Active          │
│ Success Rate: 94%        │
│ Avg Duration: 598s       │
│                          │
│ EXECUTION HISTORY        │
│ ────────────────────     │
│ Today 6:00 AM   ✓ 604s  │
│ Yesterday       ✓ 592s  │
│ 2 days ago      ✓ 587s  │
│ 3 days ago      ✗ Error │
│                          │
│ TOOLS USED (Today)       │
│ ────────────────────     │
│ • get_campaign_prospects │
│ • get_green_members      │
│ • send_bulk_campaign     │
│                          │
│ SETTINGS                 │
│ ────────────────────     │
│ Dry Run: ☑️ Enabled      │
│ Max Iterations: 10       │
│ Approval: ☑️ Required    │
│                          │
│ [Edit Config]            │
└──────────────────────────┘
```

---

## 🔧 Technical Implementation

### Backend APIs Needed

#### 1. Workflow Management Endpoints
```python
# routes/ai_workflows.py

@blueprint.route('/api/ai/workflows/status', methods=['GET'])
def get_workflows_status():
    """Get status of all scheduled workflows"""
    return {
        "workflows": [
            {
                "id": "daily_campaigns",
                "name": "Daily Campaigns",
                "status": "running",
                "next_run": "2025-10-12T06:00:00",
                "last_run": {
                    "timestamp": "2025-10-11T06:00:00",
                    "duration": 604.35,
                    "success": True,
                    "tool_calls": 8,
                    "iterations": 9
                },
                "stats": {
                    "total_runs": 45,
                    "success_rate": 0.94,
                    "avg_duration": 598.2
                }
            },
            # ... other workflows
        ]
    }

@blueprint.route('/api/ai/workflows/<workflow_id>/history', methods=['GET'])
def get_workflow_history(workflow_id):
    """Get execution history for a workflow"""
    pass

@blueprint.route('/api/ai/workflows/<workflow_id>/run', methods=['POST'])
def run_workflow_now(workflow_id):
    """Manually trigger a workflow"""
    pass

@blueprint.route('/api/ai/workflows/<workflow_id>/pause', methods=['POST'])
def pause_workflow(workflow_id):
    """Pause a scheduled workflow"""
    pass
```

#### 2. AI Conversation Endpoints
```python
@blueprint.route('/api/ai/conversation/stream', methods=['GET'])
def stream_conversation():
    """SSE endpoint for real-time AI conversation updates"""
    pass

@blueprint.route('/api/ai/conversation/history', methods=['GET'])
def get_conversation_history():
    """Get recent AI conversation messages"""
    pass

@blueprint.route('/api/ai/command', methods=['POST'])
def execute_ai_command():
    """Execute manual AI command"""
    pass

@blueprint.route('/api/ai/approvals/pending', methods=['GET'])
def get_pending_approvals():
    """Get actions requiring manager approval"""
    pass

@blueprint.route('/api/ai/approvals/<approval_id>/decide', methods=['POST'])
def decide_approval(approval_id):
    """Approve or deny a pending action"""
    pass
```

#### 3. Real-Time Updates
```python
# Use Flask-SocketIO for WebSocket connections

@socketio.on('connect', namespace='/ai')
def handle_connect():
    """Client connected to AI updates"""
    emit('connected', {'status': 'ready'})

@socketio.on('subscribe_workflow', namespace='/ai')
def subscribe_workflow(data):
    """Subscribe to specific workflow updates"""
    workflow_id = data['workflow_id']
    join_room(f'workflow_{workflow_id}')

# Emit updates during workflow execution
def emit_workflow_update(workflow_id, update):
    socketio.emit('workflow_update', update, 
                  room=f'workflow_{workflow_id}',
                  namespace='/ai')
```

---

### Frontend Components

#### 1. Workflow Status Cards
```javascript
// components/WorkflowCard.js

class WorkflowCard {
    constructor(workflowData) {
        this.data = workflowData;
        this.element = this.render();
    }
    
    render() {
        return `
            <div class="workflow-card" data-workflow-id="${this.data.id}">
                <div class="workflow-header">
                    <h6>${this.data.name}</h6>
                    <span class="status-indicator ${this.data.status}">
                        ${this.getStatusIcon()}
                    </span>
                </div>
                <div class="workflow-stats">
                    <div class="stat">
                        <label>Next Run</label>
                        <span>${this.formatNextRun()}</span>
                    </div>
                    <div class="stat">
                        <label>Last Run</label>
                        <span>${this.formatLastRun()}</span>
                    </div>
                    <div class="stat">
                        <label>Success Rate</label>
                        <span>${(this.data.stats.success_rate * 100).toFixed(0)}%</span>
                    </div>
                </div>
                <div class="workflow-actions">
                    <button onclick="runWorkflowNow('${this.data.id}')">
                        ▶️ Run Now
                    </button>
                    <button onclick="pauseWorkflow('${this.data.id}')">
                        ⏸️ Pause
                    </button>
                </div>
            </div>
        `;
    }
    
    update(newData) {
        this.data = newData;
        // Update DOM elements
    }
}
```

#### 2. AI Conversation Feed
```javascript
// components/ConversationFeed.js

class ConversationFeed {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.messages = [];
        this.initializeWebSocket();
    }
    
    initializeWebSocket() {
        this.socket = io('/ai');
        
        this.socket.on('workflow_update', (update) => {
            this.addMessage(update);
        });
        
        this.socket.on('approval_required', (approval) => {
            this.addApprovalRequest(approval);
        });
    }
    
    addMessage(message) {
        const messageElement = this.renderMessage(message);
        this.container.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    renderMessage(message) {
        switch(message.type) {
            case 'workflow_notification':
                return this.renderWorkflowNotification(message);
            case 'tool_result':
                return this.renderToolResult(message);
            case 'approval_request':
                return this.renderApprovalRequest(message);
            case 'ai_thinking':
                return this.renderAIThinking(message);
            default:
                return this.renderGenericMessage(message);
        }
    }
}
```

---

## 📱 Mobile Optimization

### Responsive Breakpoints

```css
/* Desktop: 3-column layout */
@media (min-width: 1200px) {
    .dashboard-layout {
        display: grid;
        grid-template-columns: 280px 1fr 320px;
    }
}

/* Tablet: 2-column (workflows + conversation) */
@media (min-width: 768px) and (max-width: 1199px) {
    .dashboard-layout {
        display: grid;
        grid-template-columns: 240px 1fr;
    }
    .workflow-details {
        position: absolute;
        right: -320px;
        transition: right 0.3s;
    }
    .workflow-details.open {
        right: 0;
    }
}

/* Mobile: Single column with tabs */
@media (max-width: 767px) {
    .dashboard-layout {
        display: flex;
        flex-direction: column;
    }
    .tab-navigation {
        position: fixed;
        bottom: 0;
        width: 100%;
        background: white;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
}
```

---

## 🔔 Manager Notifications

### Approval System

**High-Risk Actions Requiring Approval:**
1. Locking door access for >10 members
2. Sending campaigns to >100 recipients
3. Generating collections referral list
4. Modifying workflow schedules

**Notification Channels:**
- ✅ In-dashboard notifications (primary)
- ✅ Email notifications (optional)
- ✅ SMS alerts (critical only)
- ✅ Mobile push (future)

**Approval Workflow:**
```python
class ApprovalRequest:
    id: str
    workflow_id: str
    action: str  # "lock_members", "send_campaign", etc.
    details: dict
    created_at: datetime
    expires_at: datetime
    status: str  # "pending", "approved", "denied"
    decided_by: str = None
    decided_at: datetime = None
    
    def approve(self, manager_id: str):
        """Approve and execute the action"""
        self.status = "approved"
        self.decided_by = manager_id
        self.decided_at = datetime.now()
        
        # Execute the pending action
        execute_approved_action(self.workflow_id, self.action, self.details)
        
    def deny(self, manager_id: str, reason: str = None):
        """Deny the action"""
        self.status = "denied"
        self.decided_by = manager_id
        self.decided_at = datetime.now()
        
        # Log the denial
        log_denied_action(self.workflow_id, self.action, reason)
```

---

## 🎯 Implementation Phases

### Phase 3A: Backend Infrastructure (Week 1) ✅ COMPLETE
- [x] Create workflow management API endpoints
- [x] Set up WebSocket for real-time updates (Flask-SocketIO)
- [x] Build approval system backend
- [x] Create conversation history storage
- [x] Add workflow execution tracking
- [x] Integrate with Phase 2 workflows
- [x] Register routes in main app

**Files Created:**
- `routes/ai_workflows.py` - Workflow management APIs
- `routes/ai_conversation.py` - Conversation & approval APIs
- `test_phase3a_backend.py` - Backend API test script

### Phase 3B: Core Dashboard (Week 2) 🟡 IN PROGRESS
- [ ] Build 3-column layout structure
- [ ] Implement workflow status cards
- [ ] Create AI conversation feed
- [ ] Add workflow details panel
- [ ] Integrate with Phase 2 workflows

### Phase 3C: Advanced Features (Week 3)
- [ ] Real-time updates via WebSocket
- [ ] Approval workflow UI
- [ ] Mobile responsive design
- [ ] Rich message formatting (tables, charts)
- [ ] Keyboard shortcuts

### Phase 3D: Polish & Testing (Week 4)
- [ ] Performance optimization
- [ ] Error handling
- [ ] Loading states
- [ ] Animations & transitions
- [ ] Cross-browser testing
- [ ] User acceptance testing

---

## 🔍 Success Metrics

### User Experience
- Dashboard load time < 2s
- Real-time updates latency < 500ms
- Mobile usability score > 90/100
- Zero layout shift (CLS)

### Functionality
- 100% workflow visibility
- < 5s to approve/deny actions
- All 17 tools represented in UI
- Conversation history persistent

### Business Impact
- Manager engagement with AI decisions
- Approval turnaround time
- Workflow override frequency
- User satisfaction score

---

## 🚀 Quick Start (After Phase 3 Complete)

```bash
# Start the enhanced dashboard
python run_dashboard.py

# Visit http://localhost:5000/ai/sales-dashboard
```

**First-Time Setup:**
1. Review 6 autonomous workflows
2. Configure approval preferences
3. Subscribe to notifications
4. Test manual AI commands

---

## 📚 Related Documents

- [Phase 1 Complete](AI_AGENT_PHASE1_COMPLETE.md) - 17 tools implementation
- [Phase 2 Plan](AI_AGENT_PHASE2_PLAN.md) - Autonomous workflows
- [Phase 2 Bug Fixes](PHASE2_BUG_FIXES.md) - Testing & fixes
- [GMN Inbox Requirements](CLUBOS_INBOX_REQUIREMENTS.md) - Design inspiration

---

**Status:** 🟡 Ready to implement  
**Estimated Effort:** 3-4 weeks  
**Dependencies:** None (Phase 2 complete)  
**Next Step:** Start Phase 3A - Backend Infrastructure
