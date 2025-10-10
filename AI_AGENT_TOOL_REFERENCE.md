# AI Agent Tool Reference

Quick reference for all 17 AI agent tools

## Campaign Tools (5)

### get_campaign_prospects
**Purpose:** Get all prospects for campaign targeting  
**Risk:** Safe  
**Returns:** List of prospects with contact info  
**Example Use:** Daily prospect campaigns

```python
{
    "filters": {}  # Optional
}
→ {"success": True, "prospects": [...], "count": 103320}
```

### get_green_members
**Purpose:** Get recently signed up members  
**Risk:** Safe  
**Returns:** List of new members in good standing  
**Example Use:** Welcome campaigns, engagement

```python
{
    "days_since_signup": 30  # Optional
}
→ {"success": True, "members": [...], "count": 294}
```

### get_ppv_members
**Purpose:** Get pay-per-visit members  
**Risk:** Safe  
**Returns:** List of PPV members for conversion  
**Example Use:** Conversion campaigns to full membership

```python
{}
→ {"success": True, "members": [...], "count": 117}
```

### send_bulk_campaign
**Purpose:** Send campaign to recipient list  
**Risk:** Moderate  
**Returns:** Campaign results with sent/failed counts  
**Example Use:** Execute daily campaigns

```python
{
    "recipient_list": [...],
    "message_text": "Hi {name}! Welcome...",
    "campaign_name": "Daily Prospect Welcome",
    "channel": "sms"
}
→ {"success": True, "sent": 145, "failed": 3}
```

### get_campaign_templates
**Purpose:** Get pre-built campaign templates  
**Risk:** Safe  
**Returns:** List of templates with variables  
**Example Use:** Choose appropriate message template

```python
{}
→ {"success": True, "templates": [...], "count": 5}
```

---

## Collections Tools (5)

### get_past_due_members
**Purpose:** Get members with past due balances  
**Risk:** Safe  
**Returns:** List with amounts, contact info  
**Example Use:** Collections workflow start

```python
{
    "min_amount": 0.01
}
→ {"success": True, "members": [...], "count": 23, "total_amount": 1234.56}
```

### get_past_due_training_clients
**Purpose:** Get training clients with past due  
**Risk:** Safe  
**Returns:** Training clients list  
**Example Use:** PT collections tracking

```python
{
    "min_amount": 0.01
}
→ {"success": True, "clients": [...], "count": 5}
```

### send_payment_reminder
**Purpose:** Send escalating payment reminder  
**Risk:** Moderate  
**Returns:** Message sent confirmation  
**Example Use:** Collections escalation

```python
{
    "member_id": "47641439",
    "amount_past_due": 89.99,
    "reminder_type": "friendly",  # or "firm", "final"
    "channel": "sms"
}
→ {"success": True, "message_id": "...", "sent_at": "..."}
```

### get_collection_attempts
**Purpose:** Get attempt history for member  
**Risk:** Safe  
**Returns:** List of past attempts  
**Example Use:** Escalation decision logic

```python
{
    "member_id": "47641439",
    "days_back": 30
}
→ {"success": True, "attempts": [...], "count": 3}
```

### generate_collections_referral_list
**Purpose:** Generate external collections referral  
**Risk:** High ⚠️  
**Returns:** List ready for collections agency  
**Example Use:** Bi-weekly collections referral

```python
{
    "min_attempts": 3,
    "min_days_past_due": 14,
    "min_amount": 50.0
}
→ {"success": True, "referrals": [...], "count": 12, "total_amount": 3456.78}
```

---

## Access Control Tools (4)

### lock_door_for_member
**Purpose:** Lock gym door access (ClubHub ban)  
**Risk:** High ⚠️  
**Returns:** Lock confirmation  
**Example Use:** Past due access restriction

```python
{
    "member_id": "47641439",
    "reason": "Payment Issue"
}
→ {"success": True, "action": "locked", "member_id": "..."}
```

### unlock_door_for_member
**Purpose:** Unlock gym door access (ClubHub unban)  
**Risk:** High ⚠️  
**Returns:** Unlock confirmation  
**Example Use:** Payment resolved, restore access

```python
{
    "member_id": "47641439",
    "reason": "Payment Resolved"
}
→ {"success": True, "action": "unlocked", "member_id": "..."}
```

### check_member_access_status
**Purpose:** Check current door access status  
**Risk:** Safe  
**Returns:** Current access state  
**Example Use:** Verify access before action

```python
{
    "member_id": "47641439"
}
→ {"success": True, "access_status": "unlocked", "reason": "..."}
```

### auto_manage_access_by_payment_status
**Purpose:** Automatically manage all member access  
**Risk:** High ⚠️  
**Returns:** Summary of locked/unlocked members  
**Example Use:** Hourly automated access control

```python
{
    "min_past_due_amount": 0.01,
    "grace_period_days": 3
}
→ {"success": True, "locked": 5, "unlocked": 2}
```

---

## Member Management Tools (3)

### get_member_profile
**Purpose:** Get complete member profile  
**Risk:** Safe  
**Returns:** Full member details with billing/access  
**Example Use:** Context before taking action

```python
{
    "member_id": "47641439"
}
→ {
    "success": True,
    "profile": {
        "name": "John Smith",
        "amount_past_due": 89.99,
        "door_access": {"status": "unlocked"},
        "collection_attempts": 2
    }
}
```

### add_member_note
**Purpose:** Add note to member account  
**Risk:** Safe  
**Returns:** Note ID confirmation  
**Example Use:** Log agent actions, manager alerts

```python
{
    "member_id": "47641439",
    "note_text": "Past due account - sent 3rd reminder",
    "category": "billing",  # or "service", "complaint", "general"
    "priority": "high"  # or "low", "normal", "urgent"
}
→ {"success": True, "note_id": "123"}
```

### send_message_to_member
**Purpose:** Send individual message  
**Risk:** Moderate  
**Returns:** Message sent confirmation  
**Example Use:** Personalized follow-up

```python
{
    "member_id": "47641439",
    "message_text": "Hi John, your payment...",
    "channel": "sms"  # or "email"
}
→ {"success": True, "message_id": "...", "sent_at": "..."}
```

---

## Risk Levels

### 🟢 Safe
- Read-only operations
- No state changes
- Safe to execute autonomously

**Tools:** get_campaign_prospects, get_green_members, get_ppv_members, get_campaign_templates, get_past_due_members, get_past_due_training_clients, get_collection_attempts, check_member_access_status, get_member_profile, add_member_note

### 🟡 Moderate
- Send messages
- Create campaigns
- Trackable actions
- Can be reversed

**Tools:** send_bulk_campaign, send_payment_reminder, send_message_to_member

### 🔴 High
- Modify member access
- External referrals
- Cannot be easily reversed
- Should require confirmation

**Tools:** lock_door_for_member, unlock_door_for_member, auto_manage_access_by_payment_status, generate_collections_referral_list

---

## Tool Categories

### Campaigns (5 tools)
Focus: Marketing, engagement, conversion  
Use: Daily campaigns to prospects, green members, PPV

### Collections (5 tools)
Focus: Payment follow-up, escalation, referral  
Use: Daily past due monitoring, escalation logic

### Access (4 tools)
Focus: Door access control based on payment  
Use: Hourly automated access management

### Members (3 tools)
Focus: Profile access, notes, individual messaging  
Use: Context gathering, action logging

---

## Common Workflows

### Daily Morning Campaign
1. `get_campaign_prospects()` → Get targets
2. `get_campaign_templates()` → Get message template
3. `send_bulk_campaign()` → Execute campaign

### Collections Escalation
1. `get_past_due_members(min_amount=0.01)` → Get list
2. For each member:
   - `get_collection_attempts(member_id)` → Check history
   - If 0-1 attempts: `send_payment_reminder(type="friendly")`
   - If 2-3 attempts: `send_payment_reminder(type="firm")`
   - If 4+ attempts: `send_payment_reminder(type="final")` + `add_member_note(priority="urgent")`

### Hourly Access Management
1. `auto_manage_access_by_payment_status()` → Lock past due
2. For each locked: `send_message_to_member()` → Notify member
3. `add_member_note()` → Log action

### Bi-Weekly Collections Referral
1. `generate_collections_referral_list(min_attempts=3)` → Generate list
2. `add_member_note(priority="urgent")` → Log referral
3. Export list to CSV → Send to collections agency

---

## Error Handling

All tools return consistent format:

**Success:**
```python
{
    "success": True,
    "data_field": ...,
    ...
}
```

**Error:**
```python
{
    "success": False,
    "error": "Error message details"
}
```

---

## Logging

All tool executions are logged:
```
INFO:tools_registry:🔧 Executing tool: send_payment_reminder
INFO:tools_registry:✅ Tool completed successfully
```

Audit trail includes:
- Tool name
- Input parameters
- Execution timestamp
- Result summary
- Success/failure status

---

## Next: Autonomous Workflows

Combine tools into intelligent workflows:

```python
agent.execute_task("""
Handle collections for all past due members:
1. Get past due members over $50
2. Check attempt history for each
3. Send appropriate reminder based on attempts
4. If 4+ attempts, add urgent note for manager
5. Lock door access if past due > $100
6. Provide summary report
""")
```

Agent will autonomously:
- Call `get_past_due_members(min_amount=50)`
- For each member: Call `get_collection_attempts()`
- Decide appropriate `send_payment_reminder()` type
- Call `add_member_note()` for high-priority cases
- Call `lock_door_for_member()` for high amounts
- Compile and return summary

**This is the power of tool-based AI agents!** 🚀
