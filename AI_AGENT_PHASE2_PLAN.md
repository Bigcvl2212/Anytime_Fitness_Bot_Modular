# AI Agent Phase 2 - Autonomous Workflows

**Status**: In Progress  
**Date Started**: October 10, 2025  
**Prerequisites**: Phase 1 complete ✅

---

## Overview

Phase 2 implements autonomous AI workflows that run on schedules without human intervention. The agent will use Claude 3.7 Sonnet to intelligently chain tools together to complete complex multi-step tasks.

---

## Workflows to Implement

### 1. Daily Morning Campaigns (6 AM)
**Purpose**: Send daily marketing campaigns to prospects, green members, and PPV members

**Workflow:**
```
1. Get campaign prospects from ClubHub API
2. Get green members from database  
3. Get PPV members from database
4. Get appropriate campaign template for each group
5. Send bulk campaigns to each group
6. Log results and notify manager if failures
```

**Agent Task:**
```python
"""
You are the gym marketing manager. Execute daily morning campaigns:

1. Get all active prospects using get_campaign_prospects()
2. Get green members (recently joined) using get_green_members()
3. Get PPV members using get_ppv_members()
4. Get campaign templates using get_campaign_templates()
5. For prospects: Use 'prospect_welcome' or 'monthly_special' template
6. For green members: Use 'green_member_welcome' template
7. For PPV members: Use 'ppv_conversion' template
8. Send bulk campaigns to each group using send_bulk_campaign()
9. Provide summary: total sent, failed, by category

Execute autonomously and provide final report.
"""
```

### 2. Hourly Past Due Monitoring
**Purpose**: Monitor past due members and take immediate action

**Workflow:**
```
1. Get past due members (amount > $0.01)
2. For each member:
   - Get collection attempt history
   - Check door access status
   - Decide action based on amount and attempts:
     * New past due: Send friendly reminder + log attempt
     * $0.01-$50 + 0-1 attempts: Send friendly reminder
     * $50-$100 + 2-3 attempts: Send firm reminder
     * $100+ or 4+ attempts: Send final notice + lock door + urgent note
3. Provide summary report
```

**Agent Task:**
```python
"""
You are the gym collections manager. Monitor and handle past due accounts:

1. Get all past due members using get_past_due_members(min_amount=0.01)
2. For each member:
   a. Get their profile using get_member_profile(member_id)
   b. Get collection attempts using get_collection_attempts(member_id)
   c. Check door access using check_member_access_status(member_id)
   
3. Take appropriate action based on situation:
   - Amount $0.01-$50, 0-1 attempts: send_payment_reminder(type="friendly")
   - Amount $50-$100, 2-3 attempts: send_payment_reminder(type="firm")  
   - Amount $100+, any attempts: send_payment_reminder(type="final")
   - Amount $100+ AND 4+ attempts: ALSO lock_door_for_member() + add_member_note(priority="urgent")
   
4. Provide summary:
   - Total past due members processed
   - Reminders sent by type (friendly/firm/final)
   - Doors locked
   - Total amount past due
   - Urgent cases flagged for manager

Execute autonomously.
"""
```

### 3. Daily Collections Escalation (8 AM)
**Purpose**: Escalate collection cases that need manager attention

**Workflow:**
```
1. Get past due members with high amounts or many attempts
2. Identify cases needing escalation:
   - Past due > $200
   - 5+ collection attempts
   - Past due > 30 days
3. Add urgent notes for manager review
4. Send manager summary via SMS
```

**Agent Task:**
```python
"""
You are the gym collections manager. Perform daily escalation review:

1. Get all past due members using get_past_due_members(min_amount=50)
2. For each member, get_collection_attempts(member_id, days_back=30)
3. Identify escalation cases:
   - Amount past due > $200, OR
   - Collection attempts >= 5, OR
   - Multiple failed payment reminders
   
4. For each escalation case:
   - add_member_note(priority="urgent", category="billing", note="ESCALATION: [reason]")
   - Include: member name, amount, attempts, last contact date
   
5. Compile escalation report with:
   - Total escalation cases
   - Total amount at risk
   - List of urgent cases with details
   - Recommended actions

Provide complete escalation report.
"""
```

### 4. Bi-Weekly Collections Referral (Every 2 weeks, Monday 9 AM)
**Purpose**: Generate collections referral list for external agency

**Workflow:**
```
1. Generate referral list (3+ attempts, 14+ days past due, $50+ amount)
2. Add urgent notes to each referred member
3. Compile referral report
4. Save to file for manager review
```

**Agent Task:**
```python
"""
You are the gym collections manager. Generate bi-weekly collections referral:

1. Generate referral list using generate_collections_referral_list(
      min_attempts=3,
      min_days_past_due=14, 
      min_amount=50
   )
   
2. For each member in referral list:
   - add_member_note(
       priority="urgent",
       category="billing", 
       note="REFERRED TO COLLECTIONS: [details]"
     )
     
3. Compile referral report with:
   - Total members referred
   - Total amount referred
   - Individual member details (name, amount, attempts, contact info)
   - Date referred
   
4. Provide complete report for manager to send to collections agency.
"""
```

### 5. Monthly Batch Invoices (1st of month, 7 AM)
**Purpose**: Send invoices to all past due members

**Workflow:**
```
1. Get all past due members
2. For each member, send invoice message
3. Log invoice sent
4. Provide summary
```

**Agent Task:**
```python
"""
You are the gym billing manager. Send monthly batch invoices:

1. Get all past due members using get_past_due_members(min_amount=0.01)
2. For each member:
   - send_message_to_member(
       member_id=member_id,
       message_text="Invoice: Your account balance is $[amount]. Please update payment method.",
       channel="sms"
     )
   - add_member_note(
       category="billing",
       note="Monthly invoice sent - Amount: $[amount]"
     )
     
3. Provide summary:
   - Total invoices sent
   - Total amount invoiced
   - Failed sends
   - Breakdown by amount range
"""
```

### 6. Hourly Door Access Management
**Purpose**: Automatically lock/unlock doors based on payment status

**Workflow:**
```
1. Run auto_manage_access_by_payment_status()
2. For each member whose access changed:
   - Send notification message
   - Add note to account
3. Provide summary
```

**Agent Task:**
```python
"""
You are the gym access control manager. Manage door access based on payment:

1. Run auto_manage_access_by_payment_status(
      min_past_due_amount=0.01,
      grace_period_days=3
   )
   
2. For each member whose access was LOCKED:
   - send_message_to_member(
       message_text="Your gym access has been suspended due to past due balance of $[amount]. Please update payment.",
       channel="sms"
     )
   - add_member_note(
       category="service",
       note="Access locked - Past due $[amount]"
     )
     
3. For each member whose access was UNLOCKED:
   - send_message_to_member(
       message_text="Your gym access has been restored. Thank you for your payment!",
       channel="sms"
     )
   - add_member_note(
       category="service", 
       note="Access restored - Payment received"
     )
     
4. Provide summary:
   - Members locked
   - Members unlocked  
   - Total notifications sent
   - Any errors
"""
```

---

## Implementation Steps

### Step 1: Create Workflow Runner
File: `src/services/ai/workflow_runner.py`

```python
class WorkflowRunner:
    """Executes autonomous AI workflows"""
    
    def __init__(self, agent_core):
        self.agent = agent_core
        
    def run_daily_campaigns(self):
        """Execute daily morning campaigns"""
        result = self.agent.execute_task(DAILY_CAMPAIGNS_TASK)
        return result
        
    def run_past_due_monitoring(self):
        """Execute hourly past due monitoring"""
        result = self.agent.execute_task(PAST_DUE_MONITORING_TASK)
        return result
        
    # ... other workflows
```

### Step 2: Create Scheduler
File: `src/services/ai/workflow_scheduler.py`

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

class WorkflowScheduler:
    """Schedules and manages autonomous workflows"""
    
    def __init__(self, workflow_runner):
        self.runner = workflow_runner
        self.scheduler = BackgroundScheduler()
        
    def start(self):
        # Daily campaigns at 6 AM
        self.scheduler.add_job(
            self.runner.run_daily_campaigns,
            CronTrigger(hour=6, minute=0),
            id='daily_campaigns'
        )
        
        # Hourly past due monitoring
        self.scheduler.add_job(
            self.runner.run_past_due_monitoring,
            CronTrigger(minute=0),
            id='past_due_monitoring'
        )
        
        # Daily escalation at 8 AM
        self.scheduler.add_job(
            self.runner.run_collections_escalation,
            CronTrigger(hour=8, minute=0),
            id='collections_escalation'
        )
        
        # Bi-weekly referral (Mondays at 9 AM, every 2 weeks)
        self.scheduler.add_job(
            self.runner.run_collections_referral,
            CronTrigger(day_of_week='mon', hour=9, minute=0, week='*/2'),
            id='collections_referral'
        )
        
        # Monthly invoices (1st of month at 7 AM)
        self.scheduler.add_job(
            self.runner.run_batch_invoices,
            CronTrigger(day=1, hour=7, minute=0),
            id='batch_invoices'
        )
        
        # Hourly door access
        self.scheduler.add_job(
            self.runner.run_door_access_management,
            CronTrigger(minute=0),
            id='door_access'
        )
        
        self.scheduler.start()
```

### Step 3: Create Agent Settings/Config
File: `src/services/ai/agent_config.py`

```python
class AgentConfig:
    """Configuration for AI agent behavior"""
    
    # Workflows enabled/disabled
    ENABLE_DAILY_CAMPAIGNS = True
    ENABLE_PAST_DUE_MONITORING = True
    ENABLE_COLLECTIONS_ESCALATION = True
    ENABLE_COLLECTIONS_REFERRAL = True
    ENABLE_BATCH_INVOICES = True
    ENABLE_DOOR_ACCESS_MANAGEMENT = True
    
    # Collections thresholds
    FRIENDLY_REMINDER_MAX_AMOUNT = 50.0
    FIRM_REMINDER_MAX_AMOUNT = 100.0
    DOOR_LOCK_MIN_AMOUNT = 100.0
    COLLECTIONS_REFERRAL_MIN_AMOUNT = 50.0
    
    # Manager notifications
    MANAGER_PHONE = os.getenv('MANAGER_PHONE', '+1234567890')
    NOTIFY_ON_ESCALATION = True
    NOTIFY_ON_REFERRAL = True
    
    # Timing
    CAMPAIGN_HOUR = 6  # 6 AM
    ESCALATION_HOUR = 8  # 8 AM
    REFERRAL_DAY = 'mon'  # Monday
    REFERRAL_HOUR = 9  # 9 AM
```

---

## Testing Plan

### Manual Testing (Without API Key)
1. Test workflow task definitions
2. Test workflow runner initialization
3. Test scheduler setup
4. Verify cron triggers are correct

### With Anthropic API Key
1. Run single workflow manually
2. Verify tool calls are correct
3. Check result summaries
4. Test error handling
5. Verify logging

### Production Testing
1. Enable one workflow at a time
2. Monitor for 24 hours
3. Review agent decisions
4. Check tool call logs
5. Verify results match expectations

---

## Next Steps

1. ✅ Install APScheduler: `pip install apscheduler`
2. ✅ Install Anthropic SDK: `pip install anthropic`
3. ✅ Set ANTHROPIC_API_KEY environment variable
4. ⬜ Create workflow_runner.py
5. ⬜ Create workflow_scheduler.py
6. ⬜ Create agent_config.py
7. ⬜ Test single workflow manually
8. ⬜ Set up scheduled workflows
9. ⬜ Monitor and validate
10. ⬜ Phase 3: Manager dashboard and notifications

---

**Ready to proceed?** Let's build the workflow infrastructure!
