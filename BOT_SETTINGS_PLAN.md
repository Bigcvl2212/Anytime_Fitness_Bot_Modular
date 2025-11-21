# Gym Bot Settings Page - Complete Plan

**Status:** 🟡 Planning  
**Priority:** HIGH  
**Goal:** Comprehensive settings page for customizing all bot behavior

---

## 🎯 Settings Categories

Based on your bot's actual functionality, here are the key settings categories:

### 1. 🤖 **AI Agent Settings**
Control the autonomous AI agent behavior and performance

#### General AI Configuration
- **AI Model Selection**
  - [ ] Claude 3.7 Sonnet (current default)
  - [ ] Claude 3.5 Sonnet
  - [ ] Claude 3 Opus
  - **Why**: Different models have different costs and capabilities

- **Max Iterations Per Task**
  - Slider: 5-20 iterations (default: 10)
  - **Why**: Prevents infinite loops while allowing complex tasks

- **AI Confidence Threshold**
  - [ ] Low (60%) - More autonomous actions
  - [x] Medium (75%) - Balanced
  - [ ] High (90%) - Requires more approvals
  - **Why**: Controls when AI asks for human confirmation

- **Dry Run Mode**
  - Toggle: Enable/Disable (default: Enabled)
  - **Why**: Test workflows without actually sending messages or making changes

#### Rate Limiting
- **API Rate Limit**
  - Input: Requests per minute (default: 4 for Claude 3.7)
  - **Why**: Prevents hitting Anthropic API limits

- **Tokens Per Minute**
  - Input: Tokens (default: 40,000)
  - **Why**: Budget management and cost control

---

### 2. 📅 **Workflow Schedules**
Customize when autonomous workflows run

#### Daily Campaigns
- **Schedule Time**: Time picker (default: 6:00 AM)
- **Enabled**: Toggle (default: On)
- **Days of Week**: Select days to run
- **Timezone**: Dropdown (default: America/Chicago)
- **Why**: Control when prospects/members receive campaigns

#### Past Due Monitoring
- **Frequency**: Dropdown
  - Every 30 minutes
  - [x] Every hour (default)
  - Every 2 hours
  - Every 4 hours
- **Enabled**: Toggle (default: On)
- **Business Hours Only**: Toggle (default: On)
- **Why**: Balance between responsiveness and not being annoying

#### Collections Escalation
- **Schedule Time**: Time picker (default: 8:00 AM)
- **Enabled**: Toggle (default: On)
- **Days**: Select days (default: Monday-Friday)
- **Why**: Manager availability for urgent cases

#### Collections Referral
- **Frequency**: Dropdown
  - [x] Bi-weekly (default)
  - Weekly
  - Monthly
- **Day of Week**: Dropdown (default: Monday)
- **Time**: Time picker (default: 9:00 AM)
- **Enabled**: Toggle (default: On)
- **Why**: Collections agency coordination

#### Training Compliance Check
- **Schedule Time**: Time picker (default: 7:00 AM)
- **Enabled**: Toggle (default: On)
- **Days**: Select days (default: Monday, Wednesday, Friday)
- **Why**: Keep trainers accountable

#### Funding Status Sync
- **Frequency**: Dropdown
  - Every 4 hours
  - [x] Every 6 hours (default)
  - Every 12 hours
  - Daily
- **Enabled**: Toggle (default: On)
- **Why**: Keep funding data fresh for payment classification

---

### 3. 💰 **Collections Settings**
Fine-tune collections behavior

#### Thresholds
- **Minimum Past Due Amount**: Currency input (default: $0.01)
  - **Why**: Ignore tiny balances

- **High Priority Amount**: Currency input (default: $100.00)
  - **Why**: Flag high-value accounts

- **Urgent Amount**: Currency input (default: $200.00)
  - **Why**: Immediate manager attention

#### Door Access Control
- **Auto-Lock Enabled**: Toggle (default: Off for safety)
- **Lock Threshold**: Currency input (default: $100.00)
- **Lock After X Attempts**: Number input (default: 4)
- **Grace Period Days**: Number input (default: 7)
- **Why**: Automated enforcement vs. manual control

#### Reminder Escalation
- **Friendly Reminder**: 
  - Amount Range: $0.01 - $50.00
  - Attempts: 0-1
- **Firm Reminder**:
  - Amount Range: $50.01 - $100.00
  - Attempts: 2-3
- **Final Notice**:
  - Amount: > $100.00
  - Attempts: 4+
- **Why**: Progressive collection strategy

#### Collections Referral Criteria
- **Minimum Amount**: Currency (default: $50.00)
- **Minimum Attempts**: Number (default: 3)
- **Minimum Days Past Due**: Number (default: 14)
- **Why**: Define when to escalate externally

---

### 4. 📨 **Messaging Settings**
Control how messages are sent

#### Campaign Settings
- **Default Channel**: 
  - [ ] SMS (requires phone numbers)
  - [x] Email (more reliable)
  - [ ] Both (prefer SMS, fallback to email)
- **Why**: Delivery preference

- **Max Recipients Per Campaign**: Number (default: 100)
  - **Why**: Prevent spam flags

- **Sending Rate Limit**:
  - Messages per minute (default: 10)
  - **Why**: Avoid ClubOS rate limits

- **Retry Failed Messages**: Toggle (default: On)
  - Max retries: Number (default: 2)
  - **Why**: Improve delivery rates

#### Message Templates
- **Customize Templates**: Link to template editor
  - Prospect Welcome
  - Green Member Welcome
  - PPV Conversion
  - Monthly Special
  - Referral Bonus
  - Past Due Reminders (friendly/firm/final)
- **Why**: Brand voice consistency

#### Opt-Out Management
- **Honor Opt-Outs**: Toggle (default: On - legally required)
- **Auto-Add STOP Text**: Toggle (default: On)
- **Why**: Legal compliance (TCPA, CAN-SPAM)

---

### 5. 🎯 **Campaign Targeting**
Define who gets campaigns

#### Prospect Campaigns
- **Enabled**: Toggle (default: On)
- **Exclude Statuses**: Multi-select
  - [ ] Lost
  - [x] Not Interested
  - [ ] Closed
- **Max Days Since Last Contact**: Number (default: 30)
- **Why**: Don't spam uninterested prospects

#### Green Member Campaigns
- **Enabled**: Toggle (default: On)
- **Days Since Signup**: Slider 7-60 days (default: 30)
- **Exclude Free Trials**: Toggle (default: Off)
- **Why**: Welcome new members at right time

#### PPV Member Campaigns
- **Enabled**: Toggle (default: On)
- **Minimum Visits**: Number (default: 3)
- **Days Since Last Visit**: Number (default: 14)
- **Why**: Convert engaged visitors

---

### 6. ⚠️ **Approval Requirements**
Define what needs human approval

#### High-Risk Actions (Always require approval)
- [x] Lock door access for >10 members
- [x] Send campaigns to >100 recipients
- [x] Generate collections referral list
- [x] Modify workflow schedules
- **Why**: Prevent major mistakes

#### Medium-Risk Actions (Optional approval)
- [ ] Send past due reminders (amount > $100)
- [x] Lock individual door access
- [ ] Send training compliance warnings
- **Why**: Balance automation and control

#### Low-Risk Actions (Auto-execute)
- [x] Get data (members, prospects, etc.)
- [x] Generate reports
- [x] Send friendly reminders (< $50)
- **Why**: Don't slow down routine tasks

#### Approval Notification
- **Notification Method**:
  - [x] In-Dashboard (default)
  - [ ] Email
  - [ ] SMS
  - [ ] All of above
- **Approval Timeout**: Hours (default: 4)
  - Action after timeout:
    - [ ] Auto-approve
    - [x] Auto-deny (safer)
    - [ ] Escalate to backup approver
- **Why**: Timely decisions

---

### 7. 🔔 **Notifications & Alerts**
Control what you get notified about

#### Manager Notifications
- **Daily Summary**: Toggle (default: On)
  - Time: Time picker (default: 6:00 PM)
  - **Why**: End-of-day report

- **Workflow Failures**: Toggle (default: On)
  - **Why**: Immediate awareness of issues

- **High-Priority Collections**: Toggle (default: On)
  - Amount threshold: Currency (default: $200)
  - **Why**: Manager intervention needed

- **Approval Requests**: Toggle (default: On)
  - **Why**: Critical for high-risk actions

#### Notification Channels
- **Email**: Input field (default: manager email)
- **SMS**: Phone number input (optional)
- **Dashboard**: Toggle (always on)
- **Slack/Teams**: Webhook URL (optional)
- **Why**: Get notified where you work

---

### 8. 🔐 **Credentials Management**
Manage API credentials (read-only for security)

#### ClubOS Credentials
- **Email**: Display only (set via env var)
- **Status**: ✅ Connected / ❌ Not Connected
- **Last Verified**: Timestamp
- **Test Connection**: Button

#### ClubHub Credentials
- **Email**: Display only (set via env var)
- **Status**: ✅ Connected / ❌ Not Connected
- **Last Verified**: Timestamp
- **Test Connection**: Button

#### Anthropic API
- **Status**: ✅ Connected / ❌ Not Connected
- **Current Model**: Claude 3.7 Sonnet
- **Token Usage This Month**: Progress bar
- **Est. Cost This Month**: $XX.XX
- **Test Connection**: Button

**Why**: Visibility into authentication status without exposing secrets

---

### 9. 🎨 **Dashboard Preferences**
Customize dashboard appearance

#### Theme
- [ ] Light
- [x] Dark (default)
- [ ] Auto (system preference)

#### Default View
- [ ] Overview Dashboard
- [ ] Members
- [ ] Prospects
- [ ] Training Clients
- [x] Sales AI Dashboard
- [ ] Calendar

#### Data Refresh Rate
- Slider: 10s - 120s (default: 30s)
- **Why**: Balance freshness and performance

#### Chart Preferences
- **Default Date Range**: 
  - Last 7 days
  - [x] Last 30 days
  - Last 90 days
- **Currency Display**: USD (with $ symbol)

---

### 10. 📊 **Data Sync Settings**
Control data synchronization

#### ClubHub Sync
- **Auto-Sync Members**: Toggle (default: On)
  - Frequency: Every 6 hours
- **Auto-Sync Prospects**: Toggle (default: On)
  - Frequency: Every 6 hours
- **Auto-Sync Training Clients**: Toggle (default: On)
  - Frequency: Every 12 hours
- **Last Sync**: Timestamp with "Sync Now" button
- **Why**: Keep data fresh without manual intervention

#### ClubOS Calendar Sync
- **Enabled**: Toggle (default: On)
- **Sync Frequency**: Every 15 minutes
- **Include Past Events**: Toggle (default: Off)
- **Days Ahead**: Number (default: 30)
- **Why**: Keep calendar current

#### Database Cleanup
- **Auto-Archive Old Data**: Toggle (default: Off)
- **Archive After Days**: Number (default: 365)
- **Why**: Performance and privacy

---

### 11. 🛡️ **Safety & Compliance**
Legal and safety settings

#### Data Privacy
- **Mask PII in Logs**: Toggle (default: On)
- **Auto-Delete Logs After**: Days (default: 90)
- **Why**: Privacy compliance

#### Message Compliance
- **Require CAN-SPAM Compliance**: Toggle (default: On)
- **Require TCPA Compliance (SMS)**: Toggle (default: On)
- **Include Physical Address**: Toggle (default: On)
- **Why**: Legal requirements

#### Audit Trail
- **Log All Actions**: Toggle (default: On)
- **Log AI Decisions**: Toggle (default: On)
- **Export Logs**: Button
- **Why**: Accountability and debugging

---

### 12. 🧪 **Testing & Development**
Settings for testing and development

#### Test Mode
- **Enable Test Mode**: Toggle (default: Off)
- **What it does**:
  - No real messages sent
  - No door access changes
  - All actions logged but not executed
- **Why**: Safe testing environment

#### Debug Logging
- **Enable Debug Logs**: Toggle (default: Off)
- **Log Level**: Dropdown (INFO/DEBUG/TRACE)
- **Why**: Troubleshooting issues

#### Simulate Workflows
- **Run Daily Campaigns (Test)**: Button
- **Run Past Due Monitoring (Test)**: Button
- **Run Collections Escalation (Test)**: Button
- **Why**: Test without waiting for schedule

---

## 📱 Settings Page Layout

### Sidebar Navigation (Left)
```
⚙️ Settings
├── 🤖 AI Agent
├── 📅 Workflows
├── 💰 Collections
├── 📨 Messaging
├── 🎯 Campaigns
├── ⚠️ Approvals
├── 🔔 Notifications
├── 🔐 Credentials
├── 🎨 Appearance
├── 📊 Data Sync
├── 🛡️ Compliance
└── 🧪 Testing
```

### Main Content Area (Center-Right)
```
┌─────────────────────────────────────────────────────────────────┐
│  ⚙️ Settings > AI Agent                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  General AI Configuration                                        │
│  ────────────────────────────────────────────────────────────   │
│                                                                   │
│  AI Model          [Claude 3.7 Sonnet ▼]                        │
│  Max Iterations    [10 ═══════●════════ 20]                     │
│  Confidence        ○ Low  ● Medium  ○ High                       │
│  Dry Run Mode      [✓] Enabled                                   │
│                                                                   │
│  Rate Limiting                                                   │
│  ────────────────────────────────────────────────────────────   │
│                                                                   │
│  API Rate Limit    [4] requests/minute                           │
│  Token Limit       [40000] tokens/minute                         │
│                                                                   │
│  [💾 Save Changes]  [🔄 Reset to Defaults]                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Save Behavior
- **Auto-save**: Toggle at top (default: Off)
- **Save Button**: Confirms all changes
- **Discard Button**: Reverts to last saved state
- **Validation**: Real-time validation with error messages

---

## 🗄️ Backend Implementation

### Database Schema
```sql
CREATE TABLE bot_settings (
    id INTEGER PRIMARY KEY,
    category VARCHAR(50) NOT NULL,  -- 'ai_agent', 'workflows', 'collections', etc.
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT,  -- JSON for complex values
    data_type VARCHAR(20),  -- 'string', 'int', 'bool', 'json'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),  -- User who made change
    UNIQUE(category, setting_key)
);

CREATE TABLE settings_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_id INTEGER REFERENCES bot_settings(id),
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100),
    reason TEXT
);
```

### Settings API Endpoints
```python
# routes/settings.py

@blueprint.route('/api/settings', methods=['GET'])
def get_all_settings():
    """Get all settings grouped by category"""
    pass

@blueprint.route('/api/settings/<category>', methods=['GET'])
def get_settings_by_category(category):
    """Get settings for a specific category"""
    pass

@blueprint.route('/api/settings/<category>/<key>', methods=['GET'])
def get_setting(category, key):
    """Get a single setting value"""
    pass

@blueprint.route('/api/settings/<category>/<key>', methods=['PUT'])
def update_setting(category, key):
    """Update a single setting"""
    pass

@blueprint.route('/api/settings/<category>', methods=['PUT'])
def update_category_settings(category):
    """Bulk update settings in a category"""
    pass

@blueprint.route('/api/settings/reset/<category>', methods=['POST'])
def reset_category_to_defaults(category):
    """Reset category to default values"""
    pass

@blueprint.route('/api/settings/export', methods=['GET'])
def export_settings():
    """Export all settings as JSON"""
    pass

@blueprint.route('/api/settings/import', methods=['POST'])
def import_settings():
    """Import settings from JSON"""
    pass
```

### Settings Manager Service
```python
# services/settings_manager.py

class SettingsManager:
    """Centralized settings management"""
    
    def __init__(self):
        self.cache = {}
        self.load_defaults()
    
    def get(self, category: str, key: str, default: Any = None) -> Any:
        """Get setting value with caching"""
        pass
    
    def set(self, category: str, key: str, value: Any, user: str = "system") -> bool:
        """Set setting value and log change"""
        pass
    
    def get_category(self, category: str) -> Dict[str, Any]:
        """Get all settings in a category"""
        pass
    
    def reset_category(self, category: str) -> bool:
        """Reset category to defaults"""
        pass
    
    def validate_setting(self, category: str, key: str, value: Any) -> bool:
        """Validate setting value"""
        pass
    
    def get_history(self, category: str, key: str, limit: int = 10) -> List[Dict]:
        """Get change history for a setting"""
        pass
```

---

## 🎯 Priority Implementation Order

### Phase 1: Core Settings (Week 1)
1. ✅ Settings database schema
2. ✅ Settings API endpoints
3. ✅ Settings manager service
4. ✅ Basic settings page UI (AI Agent, Workflows)

### Phase 2: Operations Settings (Week 2)
5. ✅ Collections settings
6. ✅ Messaging settings
7. ✅ Campaign targeting
8. ✅ Approval requirements

### Phase 3: Monitoring & Admin (Week 3)
9. ✅ Notifications settings
10. ✅ Credentials status
11. ✅ Data sync settings
12. ✅ Testing tools

### Phase 4: Polish & UX (Week 4)
13. ✅ Settings import/export
14. ✅ Settings history/audit trail
15. ✅ In-app help tooltips
16. ✅ Mobile responsive design

---

## 🚀 Usage Examples

### Example 1: Changing Workflow Schedule
1. Navigate to Settings > Workflows
2. Find "Daily Campaigns"
3. Change time from 6:00 AM to 7:00 AM
4. Click "Save Changes"
5. System validates and updates APScheduler
6. Confirmation: "✅ Daily Campaigns now scheduled for 7:00 AM"

### Example 2: Adjusting Collections Thresholds
1. Navigate to Settings > Collections
2. Increase "High Priority Amount" from $100 to $150
3. Increase "Lock Threshold" from $100 to $200
4. Click "Save Changes"
5. System updates collection logic
6. Next collections run uses new thresholds

### Example 3: Enabling Test Mode
1. Navigate to Settings > Testing
2. Toggle "Enable Test Mode" to ON
3. Click "Run Daily Campaigns (Test)"
4. System simulates workflow without sending real messages
5. View test results in dashboard
6. Toggle Test Mode OFF when done

---

## 📚 Documentation Needs

- **User Guide**: How to use settings page
- **Admin Guide**: What each setting does
- **API Docs**: Settings endpoints for developers
- **Best Practices**: Recommended settings for different gym sizes

---

**Ready to implement!** This comprehensive settings system gives you full control over every aspect of the bot's behavior. 🎉
