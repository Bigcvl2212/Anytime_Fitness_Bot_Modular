# AI Agent Implementation Plan - Anytime Fitness Bot
## Autonomous Gym Management System

**Date**: October 9, 2025  
**Status**: Planning Phase  
**Framework**: Anthropic Claude 3.7 Sonnet with Function Calling

---

## Executive Summary

This document outlines the implementation plan for an autonomous AI agent that will manage daily gym operations including:

1. **Daily Campaign Management** - Automated messaging to prospects, green members, and PPV members
2. **Past Due Collections** - Real-time monitoring, escalation, and collections referrals
3. **Invoice Management** - Automated invoice generation and delivery
4. **Door Access Control** - Intelligent access management based on payment status
5. **Calendar Management** - Event scheduling on ClubOS calendar
6. **Configurable Settings** - Agent behavior customization through settings system

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   AI Agent Core Layer                        │
│            (Claude 3.7 Sonnet + Function Calling)           │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    Tool Registry Layer                       │
│     (Exposes existing infrastructure as AI-callable tools)   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│              Existing Infrastructure (src/)                  │
│  • src/services/database_manager.py                         │
│  • src/services/api/clubhub_api_client.py                   │
│  • src/services/api/clubos_api_client.py                    │
│  • src/services/api/clubos_training_api.py                  │
│  • src/services/api/clubos_real_calendar_api.py             │
│  • src/services/clubos_messaging_client_simple.py           │
│  • src/services/campaign_service.py                         │
│  • src/services/member_access_control.py                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Tool Infrastructure (Week 1-2)

### 1.1 Campaign Management Tools

**Existing Infrastructure:**
- `src/services/campaign_service.py` - CampaignService class
- `src/services/database_manager.py` - get_prospects(), member queries
- `src/services/api/clubhub_api_client.py` - ClubHubAPIClient

**Tools to Create:**

```python
# src/services/ai/agent_tools/campaign_tools.py

@tool
def get_campaign_prospects(filters: Dict = None) -> List[Dict]:
    """Get list of prospects for campaign targeting
    
    Args:
        filters: Optional filters (status, signup_date, etc.)
    
    Returns:
        List of prospect records with contact info
    """
    # Uses DatabaseManager.get_prospects()
    # Returns: [{"id": ..., "name": ..., "email": ..., "phone": ...}]

@tool
def get_green_members(days_since_signup: int = 30) -> List[Dict]:
    """Get recently signed up members (green members)
    
    Args:
        days_since_signup: Number of days since signup (default 30)
    
    Returns:
        List of new member records
    """
    # Query members table WHERE signup_date >= now() - days_since_signup
    # Returns member list with contact info

@tool
def get_ppv_members() -> List[Dict]:
    """Get pre-paid visitor (PPV) members for conversion campaigns
    
    Returns:
        List of PPV member records
    """
    # Query members WHERE membership_type = 'PPV' or similar classification

@tool
def send_bulk_campaign(
    recipient_list: List[str],
    campaign_template: str,
    campaign_name: str,
    channel: str = "sms"
) -> Dict:
    """Send bulk campaign message to recipient list
    
    Args:
        recipient_list: List of member/prospect IDs
        campaign_template: Template name or message content
        campaign_name: Name for tracking
        channel: 'sms' or 'email'
    
    Returns:
        {
            "campaign_id": "...",
            "sent": 145,
            "failed": 3,
            "status": "completed"
        }
    """
    # Uses CampaignService + ClubOSMessagingClient
    # Tracks in campaign_progress table

@tool
def get_campaign_templates() -> List[Dict]:
    """Get available campaign message templates
    
    Returns:
        List of template definitions with placeholders
    """
    # Returns templates from database or config
    # E.g., [{"name": "new_member_welcome", "content": "Hi {name}...", ...}]
```

### 1.2 Collections Management Tools

**Existing Infrastructure:**
- `src/services/database_manager.py` - get_past_due_members()
- `src/services/api/clubos_training_api.py` - training client queries
- `src/services/clubos_messaging_client_simple.py` - send_message()

**Tools to Create:**

```python
# src/services/ai/agent_tools/collections_tools.py

@tool
def get_past_due_members(threshold_days: int = 0, min_amount: float = 0) -> List[Dict]:
    """Get members with past due balances
    
    Args:
        threshold_days: Days past due (0 = any past due)
        min_amount: Minimum past due amount
    
    Returns:
        List of past due member records with amounts and contact info
    """
    # Uses DatabaseManager.get_past_due_members()
    # Returns: [{"member_id": ..., "name": ..., "amount_past_due": ..., "days_past_due": ...}]

@tool
def get_past_due_training_clients(threshold_days: int = 0) -> List[Dict]:
    """Get training clients with past due balances
    
    Args:
        threshold_days: Days past due
    
    Returns:
        List of past due training client records
    """
    # Query training_clients table WHERE amount_past_due > 0
    # Join with funding_status_cache for package details

@tool
def send_payment_reminder(
    member_id: str,
    amount: float,
    reminder_type: str = "friendly"
) -> Dict:
    """Send payment reminder to past due member
    
    Args:
        member_id: Member ID
        amount: Amount past due
        reminder_type: 'friendly', 'firm', or 'final'
    
    Returns:
        {"status": "sent", "message_id": "...", "timestamp": "..."}
    """
    # Uses ClubOSMessagingClient.send_message()
    # Logs to collections_tracking table

@tool
def track_collection_attempt(
    member_id: str,
    attempt_type: str,
    amount: float,
    notes: str = None
) -> Dict:
    """Track a collections attempt for a member
    
    Args:
        member_id: Member ID
        attempt_type: 'reminder', 'escalation', 'referral'
        amount: Amount past due
        notes: Optional notes
    
    Returns:
        {"tracking_id": "...", "attempt_number": 3, "last_attempt": "..."}
    """
    # Insert/update collections_tracking table
    # Returns current attempt count and history

@tool
def get_collection_attempts(member_id: str) -> Dict:
    """Get collection attempt history for a member
    
    Args:
        member_id: Member ID
    
    Returns:
        {
            "member_id": "...",
            "total_attempts": 3,
            "last_attempt_date": "2025-10-05",
            "history": [...]
        }
    """
    # Query collections_tracking table

@tool
def generate_collections_referral_list(min_days_past_due: int = 14) -> Dict:
    """Generate collections referral list for agency
    
    Args:
        min_days_past_due: Minimum days past due to include
    
    Returns:
        {
            "referral_list_id": "...",
            "member_count": 12,
            "total_amount": 4567.89,
            "export_path": "...",
            "members": [...]
        }
    """
    # Query past due members with 3+ contact attempts, 14+ days past due
    # Export to CSV/JSON format
    # Mark accounts as "referred_to_collections"
```

### 1.3 Invoice Management Tools

**Existing Infrastructure:**
- `src/services/api/v2_invoice_fetcher.py` - Invoice fetching logic
- ClubOS API for invoice generation

**Tools to Create:**

```python
# src/services/ai/agent_tools/invoice_tools.py

@tool
def send_invoice(member_id: str, amount: float, reason: str = "Past Due") -> Dict:
    """Send invoice to a member via ClubOS
    
    Args:
        member_id: Member ID
        amount: Invoice amount
        reason: Invoice reason/description
    
    Returns:
        {
            "invoice_id": "...",
            "status": "sent",
            "delivery_method": "email",
            "timestamp": "..."
        }
    """
    # Uses ClubOS API invoice endpoints
    # Logs to invoice_tracking table

@tool
def send_batch_invoices(invoice_list: List[Dict]) -> Dict:
    """Send batch of invoices
    
    Args:
        invoice_list: List of {"member_id": ..., "amount": ..., "reason": ...}
    
    Returns:
        {
            "batch_id": "...",
            "sent": 45,
            "failed": 2,
            "total_amount": 12345.67
        }
    """
    # Batch invoice processing
    # Returns summary

@tool
def detect_new_past_due(check_window_hours: int = 1) -> List[Dict]:
    """Detect accounts that recently went past due
    
    Args:
        check_window_hours: Time window to check (hours)
    
    Returns:
        List of newly past due accounts
    """
    # Compare current past_due status vs. cached status
    # Returns accounts that changed to past_due within window
    # [{"member_id": ..., "amount": ..., "went_past_due_at": ...}]

@tool
def get_invoice_status(member_id: str) -> Dict:
    """Check invoice delivery status for member
    
    Args:
        member_id: Member ID
    
    Returns:
        {
            "member_id": "...",
            "pending_invoices": 2,
            "last_invoice_date": "...",
            "invoices": [...]
        }
    """
    # Query invoice_tracking table
```

### 1.4 Door Access Tools

**Existing Infrastructure:**
- `src/services/member_access_control.py` - MemberAccessControl class
- Door access system integration (needs verification)

**Tools to Create:**

```python
# src/services/ai/agent_tools/access_tools.py

@tool
def lock_door_for_member(member_id: str, reason: str) -> Dict:
    """Revoke door access for a member
    
    Args:
        member_id: Member ID
        reason: Reason for access revocation (e.g., "Past Due")
    
    Returns:
        {
            "member_id": "...",
            "access_status": "revoked",
            "reason": "...",
            "timestamp": "..."
        }
    """
    # Uses MemberAccessControl.revoke_access()
    # Logs to access_control_log table

@tool
def unlock_door_for_member(member_id: str, reason: str) -> Dict:
    """Grant door access for a member
    
    Args:
        member_id: Member ID
        reason: Reason for access grant (e.g., "Payment Received")
    
    Returns:
        {
            "member_id": "...",
            "access_status": "granted",
            "reason": "...",
            "timestamp": "..."
        }
    """
    # Uses MemberAccessControl.grant_access()

@tool
def check_member_access_status(member_id: str) -> Dict:
    """Check current door access status for member
    
    Args:
        member_id: Member ID
    
    Returns:
        {
            "member_id": "...",
            "has_access": true/false,
            "status": "active|revoked|suspended",
            "last_access": "...",
            "reason": "..."
        }
    """
    # Query access control system

@tool
def auto_manage_access_by_payment_status(dry_run: bool = False) -> Dict:
    """Automatically manage door access based on payment status
    
    Args:
        dry_run: If True, only report what would change
    
    Returns:
        {
            "scanned": 345,
            "locked": 12,
            "unlocked": 3,
            "unchanged": 330,
            "changes": [...]
        }
    """
    # Check all members
    # Past due → lock door
    # Paid up → unlock door
    # Returns summary of changes
```

### 1.5 Calendar Management Tools

**Existing Infrastructure:**
- `src/services/api/clubos_real_calendar_api.py` - ClubOSRealCalendarAPI class
- `src/ical_calendar_parser.py` - iCal parsing

**Tools to Create:**

```python
# src/services/ai/agent_tools/calendar_tools.py

@tool
def create_calendar_event(
    title: str,
    start_datetime: str,
    end_datetime: str,
    event_type: str = "class",
    description: str = None
) -> Dict:
    """Create a new event on ClubOS calendar
    
    Args:
        title: Event title
        start_datetime: ISO format datetime
        end_datetime: ISO format datetime
        event_type: 'class', 'training', 'appointment', 'maintenance'
        description: Optional event description
    
    Returns:
        {
            "event_id": "...",
            "title": "...",
            "status": "created",
            "calendar_url": "..."
        }
    """
    # Uses ClubOSRealCalendarAPI.create_event()

@tool
def update_calendar_event(event_id: str, updates: Dict) -> Dict:
    """Update an existing calendar event
    
    Args:
        event_id: Event ID
        updates: Dictionary of fields to update
    
    Returns:
        {"event_id": "...", "status": "updated", ...}
    """
    # Uses ClubOSRealCalendarAPI.update_event()

@tool
def delete_calendar_event(event_id: str, reason: str) -> Dict:
    """Delete a calendar event
    
    Args:
        event_id: Event ID
        reason: Reason for deletion
    
    Returns:
        {"event_id": "...", "status": "deleted"}
    """
    # Uses ClubOSRealCalendarAPI.delete_event()

@tool
def get_calendar_events(start_date: str, end_date: str) -> List[Dict]:
    """Get calendar events for date range
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        List of event records
    """
    # Query ClubOS calendar API
    # Returns: [{"event_id": ..., "title": ..., "start": ..., "end": ...}]

@tool
def check_calendar_availability(datetime_str: str, duration_minutes: int = 60) -> Dict:
    """Check if a time slot is available
    
    Args:
        datetime_str: ISO format datetime
        duration_minutes: Duration in minutes
    
    Returns:
        {
            "available": true/false,
            "conflicts": [...],
            "suggested_times": [...]
        }
    """
    # Check for conflicts in requested time slot
    # Suggest alternative times if not available
```

### 1.6 Member & Reporting Tools

**Existing Infrastructure:**
- `src/services/database_manager.py` - Comprehensive member queries
- ClubHub/ClubOS API clients

**Tools to Create:**

```python
# src/services/ai/agent_tools/member_tools.py

@tool
def get_member_profile(member_id: str) -> Dict:
    """Get complete member profile
    
    Args:
        member_id: Member ID
    
    Returns:
        {
            "member_id": "...",
            "name": "...",
            "email": "...",
            "phone": "...",
            "membership_type": "...",
            "status": "...",
            "amount_past_due": 0.00,
            "last_checkin": "...",
            "agreements": [...],
            ...
        }
    """
    # Uses DatabaseManager + ClubHub API

@tool
def add_member_note(member_id: str, note: str, category: str) -> Dict:
    """Add a note to member's account
    
    Args:
        member_id: Member ID
        note: Note content
        category: 'billing', 'collections', 'general', 'complaint'
    
    Returns:
        {"note_id": "...", "status": "added"}
    """
    # Insert to member_notes table

@tool
def get_member_messages(member_id: str, limit: int = 10) -> List[Dict]:
    """Get recent message history for member
    
    Args:
        member_id: Member ID
        limit: Number of messages to retrieve
    
    Returns:
        List of message records
    """
    # Query messages table

@tool
def send_message_to_member(
    member_id: str,
    message: str,
    channel: str = "sms"
) -> Dict:
    """Send a message to a member
    
    Args:
        member_id: Member ID
        message: Message content
        channel: 'sms' or 'email'
    
    Returns:
        {"status": "sent", "message_id": "...", "timestamp": "..."}
    """
    # Uses ClubOSMessagingClient

@tool
def get_daily_stats(date: str = "today") -> Dict:
    """Get daily operational statistics
    
    Args:
        date: Date string (YYYY-MM-DD) or 'today'
    
    Returns:
        {
            "date": "...",
            "checkins": 234,
            "new_members": 5,
            "past_due_count": 23,
            "past_due_amount": 4567.89,
            "revenue": 12345.67
        }
    """
    # Aggregate from various tables
```

---

## Phase 2: Agent Configuration System (Week 2-3)

### 2.1 Agent Settings Database Schema

```sql
-- src/services/ai/agent_config_schema.sql

CREATE TABLE agent_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    value_type TEXT NOT NULL,  -- 'string', 'int', 'float', 'bool', 'json'
    category TEXT NOT NULL,  -- 'campaigns', 'collections', 'access', 'calendar', 'general'
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT
);

CREATE TABLE agent_workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_name TEXT UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    schedule_cron TEXT,  -- '0 6 * * *' for 6 AM daily
    priority INTEGER DEFAULT 0,
    config JSON,  -- Workflow-specific configuration
    last_run TIMESTAMP,
    last_status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_execution_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_name TEXT,
    task_description TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT,  -- 'running', 'completed', 'failed'
    tools_called JSON,  -- List of tools used
    results JSON,  -- Execution results
    error_message TEXT
);
```

### 2.2 Configuration Tools

```python
# src/services/ai/agent_tools/config_tools.py

@tool
def get_agent_config(category: str = None) -> Dict:
    """Get agent configuration settings
    
    Args:
        category: Optional category filter
    
    Returns:
        Dictionary of configuration settings
    """
    # Query agent_config table
    # Returns: {"campaigns.daily_run_time": "06:00", ...}

@tool
def update_agent_config(key: str, value: Any, updated_by: str) -> Dict:
    """Update an agent configuration setting
    
    Args:
        key: Config key (e.g., 'collections.escalation_days')
        value: New value
        updated_by: User making change
    
    Returns:
        {"key": "...", "old_value": "...", "new_value": "...", "status": "updated"}
    """
    # Update agent_config table
    # Log configuration change

@tool
def get_workflow_config(workflow_name: str) -> Dict:
    """Get configuration for a specific workflow
    
    Args:
        workflow_name: Name of workflow
    
    Returns:
        {
            "workflow_name": "...",
            "enabled": true,
            "schedule": "0 6 * * *",
            "config": {...}
        }
    """
    # Query agent_workflows table

@tool
def enable_workflow(workflow_name: str) -> Dict:
    """Enable an agent workflow
    
    Args:
        workflow_name: Name of workflow to enable
    
    Returns:
        {"workflow_name": "...", "enabled": true}
    """
    # Update agent_workflows SET enabled = 1

@tool
def disable_workflow(workflow_name: str) -> Dict:
    """Disable an agent workflow
    
    Args:
        workflow_name: Name of workflow to disable
    
    Returns:
        {"workflow_name": "...", "enabled": false}
    """
    # Update agent_workflows SET enabled = 0
```

### 2.3 Default Configuration

```python
# src/services/ai/default_agent_config.py

DEFAULT_AGENT_CONFIG = {
    # Campaign Settings
    "campaigns.daily_run_time": "06:00",
    "campaigns.prospect_enabled": True,
    "campaigns.green_member_enabled": True,
    "campaigns.ppv_enabled": True,
    "campaigns.green_member_days": 30,  # Members signed up within 30 days
    "campaigns.rate_limit_per_hour": 100,
    
    # Collections Settings
    "collections.check_interval_hours": 1,
    "collections.friendly_reminder_days": 1,  # 1 day past due
    "collections.firm_reminder_days": 7,  # 7 days past due
    "collections.final_notice_days": 14,  # 14 days past due
    "collections.referral_threshold_days": 14,
    "collections.referral_min_attempts": 3,
    "collections.referral_schedule": "0 9 * * 1",  # Every Monday 9 AM
    "collections.auto_lock_door": True,
    
    # Invoice Settings
    "invoices.auto_send_on_past_due": True,
    "invoices.batch_day_of_month": 1,  # 1st of month
    "invoices.batch_time": "09:00",
    
    # Door Access Settings
    "access.auto_manage": True,
    "access.lock_on_past_due": True,
    "access.unlock_on_payment": True,
    "access.check_interval_hours": 1,
    
    # Calendar Settings
    "calendar.allow_auto_scheduling": True,
    "calendar.require_approval": False,
    
    # General Settings
    "agent.max_iterations_per_task": 20,
    "agent.log_all_actions": True,
    "agent.require_approval_high_risk": True,
    "agent.notification_email": "manager@gym.com"
}
```

---

## Phase 3: Autonomous Workflows (Week 3-5)

### 3.1 Workflow Definitions

```python
# src/services/ai/workflows/autonomous_workflows.py

from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AutonomousWorkflows:
    """Defines autonomous AI agent workflows"""
    
    def __init__(self, agent_core, config):
        self.agent = agent_core
        self.config = config
    
    # ============================================================
    # WORKFLOW 1: Daily Morning Campaigns (6 AM)
    # ============================================================
    
    def run_daily_campaigns(self) -> Dict:
        """Execute daily marketing campaigns
        
        Schedule: Daily at 6 AM
        
        Tasks:
        1. Send campaign to prospects
        2. Send campaign to green members
        3. Send campaign to PPV members
        4. Log results and notify manager
        """
        
        task_prompt = f"""
        You are the gym marketing automation agent. Execute daily campaigns:
        
        TASK 1: PROSPECT CAMPAIGN
        - Call get_campaign_prospects() to get active prospects
        - Call get_campaign_templates() to get "daily_prospect_offer" template
        - Call send_bulk_campaign() to send to prospects
        - Track: campaign_name="daily_prospect_{datetime.now().strftime('%Y%m%d')}"
        
        TASK 2: GREEN MEMBER CAMPAIGN (New Members)
        - Call get_green_members(days_since_signup=30)
        - Use template "new_member_engagement"
        - Send campaign to green members
        - Track: campaign_name="green_member_{datetime.now().strftime('%Y%m%d')}"
        
        TASK 3: PPV CONVERSION CAMPAIGN
        - Call get_ppv_members()
        - Use template "ppv_conversion_offer"
        - Send campaign encouraging full membership
        - Track: campaign_name="ppv_conversion_{datetime.now().strftime('%Y%m%d')}"
        
        FINAL STEP:
        - Compile summary report with send counts, delivery status
        - Call add_member_note() for any failures
        - Return complete execution summary
        
        Execute all tasks autonomously. Handle any errors gracefully.
        """
        
        result = self.agent.execute(task_prompt)
        
        logger.info(f"Daily campaigns completed: {result}")
        return result
    
    # ============================================================
    # WORKFLOW 2: Past Due Monitoring (Hourly)
    # ============================================================
    
    def run_past_due_monitoring(self) -> Dict:
        """Monitor for newly past due accounts and take action
        
        Schedule: Every hour
        
        Tasks:
        1. Detect newly past due members
        2. Send invoice + payment reminder
        3. Lock gym door access
        4. Track collection attempt
        """
        
        task_prompt = """
        You are the gym collections monitoring agent. Monitor past due status:
        
        STEP 1: DETECT NEW PAST DUE
        - Call detect_new_past_due(check_window_hours=1)
        - This returns accounts that went past due in last hour
        
        FOR EACH NEW PAST DUE ACCOUNT:
        
        STEP 2: SEND INVOICE
        - Call send_invoice(member_id, amount, reason="Past Due Balance")
        
        STEP 3: SEND PAYMENT REMINDER
        - Call send_payment_reminder(member_id, amount, reminder_type="friendly")
        - First contact should be friendly tone
        
        STEP 4: LOCK DOOR ACCESS
        - Call lock_door_for_member(member_id, reason="Payment Past Due")
        - Only if config.collections.auto_lock_door is True
        
        STEP 5: TRACK ATTEMPT
        - Call track_collection_attempt(member_id, "reminder", amount, notes="First contact - invoice sent")
        
        FINAL REPORT:
        - Summarize: How many new past due found
        - Actions taken per member
        - Any errors or failures
        
        Execute autonomously. Handle all errors gracefully.
        """
        
        result = self.agent.execute(task_prompt)
        
        logger.info(f"Past due monitoring completed: {result}")
        return result
    
    # ============================================================
    # WORKFLOW 3: Collections Escalation (Daily 8 AM)
    # ============================================================
    
    def run_collections_escalation(self) -> Dict:
        """Escalate past due collections based on thresholds
        
        Schedule: Daily at 8 AM
        
        Tasks:
        1. Get all past due members/training clients
        2. Check attempt history
        3. Escalate based on days past due
        4. Track all actions
        """
        
        task_prompt = """
        You are the gym collections escalation agent. Review and escalate past due accounts:
        
        STEP 1: GET PAST DUE MEMBERS
        - Call get_past_due_members(threshold_days=0)
        - This returns ALL past due members
        
        STEP 2: GET PAST DUE TRAINING CLIENTS
        - Call get_past_due_training_clients(threshold_days=0)
        - Training clients have separate tracking
        
        FOR EACH PAST DUE ACCOUNT:
        
        STEP 3: CHECK ATTEMPT HISTORY
        - Call get_collection_attempts(member_id)
        - Get: total_attempts, last_attempt_date, days_past_due
        
        STEP 4: DETERMINE ACTION BASED ON ESCALATION RULES
        
        IF days_past_due <= 7 AND last_attempt > 48 hours ago:
            → Call send_payment_reminder(member_id, amount, "friendly")
            → Track: track_collection_attempt(member_id, "reminder", amount, "Friendly reminder - 1-7 days past due")
        
        ELSE IF 7 < days_past_due <= 14 AND last_attempt > 72 hours ago:
            → Call send_payment_reminder(member_id, amount, "firm")
            → Track: track_collection_attempt(member_id, "escalation", amount, "Firm reminder - 7-14 days past due")
        
        ELSE IF days_past_due > 14 AND total_attempts >= 3:
            → Call send_payment_reminder(member_id, amount, "final")
            → Add note: add_member_note(member_id, "Eligible for collections referral", "collections")
            → Track: track_collection_attempt(member_id, "final_notice", amount, "Final notice - 14+ days past due")
        
        STEP 5: SUMMARY REPORT
        - Total past due accounts reviewed
        - Friendly reminders sent
        - Firm reminders sent
        - Final notices sent
        - Accounts ready for referral
        
        Execute all actions autonomously. Respect time-based throttling.
        """
        
        result = self.agent.execute(task_prompt)
        
        logger.info(f"Collections escalation completed: {result}")
        return result
    
    # ============================================================
    # WORKFLOW 4: Collections Referral (Bi-weekly Monday 9 AM)
    # ============================================================
    
    def run_collections_referral(self) -> Dict:
        """Generate and send collections referral list
        
        Schedule: Every 2 weeks on Monday at 9 AM
        
        Tasks:
        1. Identify accounts 14+ days past due with 3+ attempts
        2. Generate referral list
        3. Export and notify manager
        """
        
        task_prompt = """
        You are the gym collections referral agent. Generate bi-weekly referral list:
        
        STEP 1: GENERATE REFERRAL LIST
        - Call generate_collections_referral_list(min_days_past_due=14)
        - This returns members with:
            * 14+ days past due
            * 3+ collection attempts
            * Still unpaid
        
        STEP 2: REVIEW LIST
        - The function returns:
            * Total member count
            * Total amount owed
            * Export file path
            * Member details
        
        STEP 3: NOTIFY MANAGER
        - Send summary to manager email
        - Include: member count, total amount, file path
        - Note: These accounts are now marked as "referred_to_collections"
        
        STEP 4: UPDATE MEMBER NOTES
        - For each member in referral list:
            → Call add_member_note(member_id, "Referred to collections agency", "collections")
        
        FINAL REPORT:
        - Referral list ID
        - Member count
        - Total debt amount
        - Export location
        - Manager notification status
        
        Execute autonomously.
        """
        
        result = self.agent.execute(task_prompt)
        
        logger.info(f"Collections referral completed: {result}")
        return result
    
    # ============================================================
    # WORKFLOW 5: Batch Invoice Processing (Monthly 1st @ 9 AM)
    # ============================================================
    
    def run_batch_invoice_processing(self) -> Dict:
        """Process and send monthly batch invoices
        
        Schedule: 1st of month at 9 AM
        
        Tasks:
        1. Get members needing invoices
        2. Generate and send batch
        3. Log results
        """
        
        task_prompt = """
        You are the gym billing automation agent. Process monthly batch invoices:
        
        STEP 1: IDENTIFY MEMBERS NEEDING INVOICES
        - Query members with monthly billing
        - Exclude members with recent invoices (within 28 days)
        - Build invoice list: [{"member_id": ..., "amount": ..., "reason": "Monthly Membership"}]
        
        STEP 2: SEND BATCH INVOICES
        - Call send_batch_invoices(invoice_list)
        - This sends invoices via ClubOS to all members
        
        STEP 3: HANDLE FAILURES
        - For any failed invoices:
            → Call add_member_note(member_id, "Invoice send failed - needs manual follow-up", "billing")
        
        STEP 4: SUMMARY REPORT
        - Total invoices sent
        - Total amount invoiced
        - Failures and reasons
        - Success rate
        
        Execute autonomously.
        """
        
        result = self.agent.execute(task_prompt)
        
        logger.info(f"Batch invoice processing completed: {result}")
        return result
    
    # ============================================================
    # WORKFLOW 6: Intelligent Door Access Management (Hourly)
    # ============================================================
    
    def run_intelligent_access_management(self) -> Dict:
        """Intelligently manage door access based on payment status
        
        Schedule: Every hour
        
        Tasks:
        1. Check for payments received → unlock door + thank you
        2. Check for new past due → lock door
        3. Handle edge cases intelligently
        """
        
        task_prompt = """
        You are the gym access control intelligence agent. Manage door access:
        
        STEP 1: RUN AUTO-MANAGEMENT
        - Call auto_manage_access_by_payment_status(dry_run=False)
        - This automatically:
            * Locks doors for past due members
            * Unlocks doors for paid-up members
            * Returns summary of changes
        
        STEP 2: HANDLE UNLOCKED MEMBERS (Payment Received)
        - For each member whose door was unlocked:
            → Call send_message_to_member(member_id, "Thank you for your payment! Your gym access has been restored.", "sms")
        
        STEP 3: HANDLE LOCKED MEMBERS (New Past Due)
        - For each member whose door was locked:
            → Already handled by past_due_monitoring workflow
            → No additional action needed (avoid duplicate messages)
        
        STEP 4: SUMMARY REPORT
        - Total members scanned
        - Doors locked
        - Doors unlocked
        - Thank you messages sent
        
        Execute autonomously.
        """
        
        result = self.agent.execute(task_prompt)
        
        logger.info(f"Intelligent access management completed: {result}")
        return result
```

### 3.2 Workflow Scheduler

```python
# src/services/ai/workflows/workflow_scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)

class WorkflowScheduler:
    """Manages scheduled execution of autonomous workflows"""
    
    def __init__(self, workflows: AutonomousWorkflows, config):
        self.workflows = workflows
        self.config = config
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        """Start the workflow scheduler"""
        
        # Workflow 1: Daily Campaigns (6 AM)
        if self.config.get("campaigns.prospect_enabled"):
            self.scheduler.add_job(
                self.workflows.run_daily_campaigns,
                CronTrigger.from_crontab("0 6 * * *"),  # 6 AM daily
                id="daily_campaigns",
                name="Daily Marketing Campaigns",
                replace_existing=True
            )
            logger.info("✅ Scheduled: Daily campaigns at 6 AM")
        
        # Workflow 2: Past Due Monitoring (Hourly)
        check_interval = self.config.get("collections.check_interval_hours", 1)
        self.scheduler.add_job(
            self.workflows.run_past_due_monitoring,
            CronTrigger.from_crontab(f"0 */{check_interval} * * *"),
            id="past_due_monitoring",
            name="Past Due Monitoring",
            replace_existing=True
        )
        logger.info(f"✅ Scheduled: Past due monitoring every {check_interval} hour(s)")
        
        # Workflow 3: Collections Escalation (Daily 8 AM)
        self.scheduler.add_job(
            self.workflows.run_collections_escalation,
            CronTrigger.from_crontab("0 8 * * *"),  # 8 AM daily
            id="collections_escalation",
            name="Collections Escalation",
            replace_existing=True
        )
        logger.info("✅ Scheduled: Collections escalation daily at 8 AM")
        
        # Workflow 4: Collections Referral (Bi-weekly Monday 9 AM)
        referral_schedule = self.config.get("collections.referral_schedule", "0 9 * * 1")
        self.scheduler.add_job(
            self.workflows.run_collections_referral,
            CronTrigger.from_crontab(referral_schedule),
            id="collections_referral",
            name="Collections Referral",
            replace_existing=True
        )
        logger.info(f"✅ Scheduled: Collections referral ({referral_schedule})")
        
        # Workflow 5: Batch Invoices (1st of month @ 9 AM)
        batch_day = self.config.get("invoices.batch_day_of_month", 1)
        batch_time = self.config.get("invoices.batch_time", "09:00").split(":")
        self.scheduler.add_job(
            self.workflows.run_batch_invoice_processing,
            CronTrigger(day=batch_day, hour=int(batch_time[0]), minute=int(batch_time[1])),
            id="batch_invoices",
            name="Batch Invoice Processing",
            replace_existing=True
        )
        logger.info(f"✅ Scheduled: Batch invoices on day {batch_day} at {batch_time[0]}:{batch_time[1]}")
        
        # Workflow 6: Intelligent Access Management (Hourly)
        if self.config.get("access.auto_manage"):
            access_interval = self.config.get("access.check_interval_hours", 1)
            self.scheduler.add_job(
                self.workflows.run_intelligent_access_management,
                CronTrigger.from_crontab(f"0 */{access_interval} * * *"),
                id="intelligent_access",
                name="Intelligent Door Access Management",
                replace_existing=True
            )
            logger.info(f"✅ Scheduled: Intelligent access management every {access_interval} hour(s)")
        
        # Start scheduler
        self.scheduler.start()
        logger.info("🚀 Workflow scheduler started")
    
    def stop(self):
        """Stop the workflow scheduler"""
        self.scheduler.shutdown()
        logger.info("🛑 Workflow scheduler stopped")
    
    def get_scheduled_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduler.get_jobs()
```

---

## Phase 4: Agent Core Implementation (Week 4-5)

### 4.1 Agent Core with Claude Function Calling

```python
# src/services/ai/agent_core.py

from anthropic import Anthropic
from typing import Dict, List, Any
import logging
import json
import os

logger = logging.getLogger(__name__)

class GymAgentCore:
    """Core AI agent using Claude 3.7 Sonnet with function calling"""
    
    def __init__(self, tools_registry, config):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.tools_registry = tools_registry
        self.config = config
        self.model = "claude-3-7-sonnet-20250219"
    
    def execute(self, task_prompt: str, max_iterations: int = None) -> Dict:
        """Execute an autonomous task
        
        Args:
            task_prompt: Natural language task description
            max_iterations: Max tool calling iterations (default from config)
        
        Returns:
            {
                "status": "completed|failed",
                "result": "...",
                "tools_called": [...],
                "iterations": 5,
                "execution_time": 12.34
            }
        """
        
        if max_iterations is None:
            max_iterations = self.config.get("agent.max_iterations_per_task", 20)
        
        start_time = time.time()
        tools_called = []
        
        messages = [
            {
                "role": "user",
                "content": task_prompt
            }
        ]
        
        try:
            for iteration in range(max_iterations):
                logger.info(f"[Agent] Iteration {iteration + 1}/{max_iterations}")
                
                # Call Claude with tools
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    tools=self.tools_registry.get_tool_schemas(),
                    messages=messages
                )
                
                # Check if Claude wants to use tools
                if response.stop_reason == "tool_use":
                    # Extract tool calls
                    tool_use_blocks = [
                        block for block in response.content
                        if block.type == "tool_use"
                    ]
                    
                    # Execute each tool
                    tool_results = []
                    for tool_use in tool_use_blocks:
                        tool_name = tool_use.name
                        tool_input = tool_use.input
                        
                        logger.info(f"[Agent] 🔧 Calling tool: {tool_name}")
                        logger.debug(f"[Agent] Input: {tool_input}")
                        
                        # Execute tool
                        try:
                            result = self.tools_registry.execute_tool(tool_name, tool_input)
                            
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": json.dumps(result, default=str)
                            })
                            
                            tools_called.append({
                                "tool": tool_name,
                                "input": tool_input,
                                "result": result,
                                "status": "success"
                            })
                            
                            logger.info(f"[Agent] ✅ Tool result: {result}")
                            
                        except Exception as e:
                            error_msg = str(e)
                            logger.error(f"[Agent] ❌ Tool error: {error_msg}")
                            
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": f"Error: {error_msg}",
                                "is_error": True
                            })
                            
                            tools_called.append({
                                "tool": tool_name,
                                "input": tool_input,
                                "error": error_msg,
                                "status": "error"
                            })
                    
                    # Add assistant response and tool results to conversation
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                
                else:
                    # No more tools to call, task complete
                    final_text = next(
                        (block.text for block in response.content if hasattr(block, "text")),
                        "Task completed"
                    )
                    
                    execution_time = time.time() - start_time
                    
                    logger.info(f"[Agent] ✅ Task completed in {iteration + 1} iterations ({execution_time:.2f}s)")
                    
                    return {
                        "status": "completed",
                        "result": final_text,
                        "tools_called": tools_called,
                        "iterations": iteration + 1,
                        "execution_time": execution_time
                    }
            
            # Max iterations reached
            execution_time = time.time() - start_time
            logger.warning(f"[Agent] ⚠️  Max iterations ({max_iterations}) reached")
            
            return {
                "status": "incomplete",
                "result": "Max iterations reached without completion",
                "tools_called": tools_called,
                "iterations": max_iterations,
                "execution_time": execution_time
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"[Agent] ❌ Fatal error: {str(e)}")
            
            return {
                "status": "failed",
                "result": str(e),
                "tools_called": tools_called,
                "iterations": iteration + 1 if 'iteration' in locals() else 0,
                "execution_time": execution_time
            }
```

### 4.2 Tools Registry

```python
# src/services/ai/tools_registry.py

from typing import Dict, List, Callable, Any
import logging

logger = logging.getLogger(__name__)

class ToolsRegistry:
    """Central registry for AI agent tools"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: List[Dict] = []
    
    def register_tool(self, name: str, func: Callable, schema: Dict):
        """Register a tool with the agent
        
        Args:
            name: Tool name
            func: Tool function
            schema: Claude-compatible tool schema
        """
        self.tools[name] = func
        self.schemas.append(schema)
        logger.info(f"✅ Registered tool: {name}")
    
    def execute_tool(self, name: str, input_params: Dict) -> Any:
        """Execute a registered tool
        
        Args:
            name: Tool name
            input_params: Tool input parameters
        
        Returns:
            Tool execution result
        """
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        
        tool_func = self.tools[name]
        return tool_func(**input_params)
    
    def get_tool_schemas(self) -> List[Dict]:
        """Get all tool schemas for Claude"""
        return self.schemas
    
    def list_tools(self) -> List[str]:
        """List registered tool names"""
        return list(self.tools.keys())
```

---

## Phase 5: Safety & Monitoring (Week 5-6)

### 5.1 Permission Levels

```python
# src/services/ai/safety/permission_manager.py

class PermissionManager:
    """Manage tool permission levels and approvals"""
    
    SAFE_TOOLS = [
        "get_member_profile",
        "get_past_due_members",
        "get_campaign_prospects",
        "get_daily_stats",
        "check_member_access_status",
        "get_calendar_events",
    ]
    
    MODERATE_RISK = [
        "send_message_to_member",
        "send_bulk_campaign",
        "send_payment_reminder",
        "add_member_note",
        "create_calendar_event",
    ]
    
    HIGH_RISK = [
        "lock_door_for_member",
        "unlock_door_for_member",
        "send_invoice",
        "send_batch_invoices",
        "generate_collections_referral_list",
        "delete_calendar_event",
    ]
    
    def check_permission(self, tool_name: str, require_approval: bool = True) -> bool:
        """Check if tool execution requires approval
        
        Args:
            tool_name: Name of tool
            require_approval: Whether high-risk tools need approval
        
        Returns:
            True if approved, False if needs manual approval
        """
        if tool_name in self.SAFE_TOOLS:
            return True
        
        if tool_name in self.MODERATE_RISK:
            return True
        
        if tool_name in self.HIGH_RISK:
            if not require_approval:
                return True
            # In production, implement approval workflow here
            logger.warning(f"⚠️  HIGH RISK tool called: {tool_name}")
            return True  # For autonomous operation
        
        return True
```

### 5.2 Audit Logging

```python
# src/services/ai/safety/audit_logger.py

class AgentAuditLogger:
    """Log all agent actions for audit trail"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def log_workflow_execution(self, workflow_name: str, result: Dict):
        """Log workflow execution"""
        self.db.execute("""
            INSERT INTO agent_execution_log
            (workflow_name, task_description, started_at, completed_at, status, tools_called, results)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            workflow_name,
            result.get("task", ""),
            result.get("start_time"),
            result.get("end_time"),
            result.get("status"),
            json.dumps(result.get("tools_called", [])),
            json.dumps(result.get("result", {}))
        ))
    
    def log_tool_execution(self, tool_name: str, input_params: Dict, result: Any, success: bool):
        """Log individual tool execution"""
        # Detailed tool logging
        pass
    
    def get_execution_history(self, days: int = 7) -> List[Dict]:
        """Get recent execution history"""
        # Query agent_execution_log
        pass
```

---

## Phase 6: Dashboard Integration (Week 6)

### 6.1 Agent Status Dashboard

```python
# src/routes/agent_dashboard.py

@app.route('/agent/status')
def agent_status():
    """Agent status dashboard"""
    
    # Get scheduled workflows
    workflows = scheduler.get_scheduled_jobs()
    
    # Get recent executions
    recent_executions = audit_logger.get_execution_history(days=7)
    
    # Get current config
    config = agent_config_manager.get_all_config()
    
    return render_template('agent_status.html',
        workflows=workflows,
        executions=recent_executions,
        config=config
    )

@app.route('/agent/config', methods=['GET', 'POST'])
def agent_config():
    """Agent configuration interface"""
    
    if request.method == 'POST':
        # Update config
        key = request.form.get('key')
        value = request.form.get('value')
        updated_by = session.get('user')
        
        agent_config_manager.update_config(key, value, updated_by)
        
        return jsonify({"status": "updated"})
    
    # GET: return config form
    config = agent_config_manager.get_all_config()
    return render_template('agent_config.html', config=config)

@app.route('/agent/trigger/<workflow_name>', methods=['POST'])
def trigger_workflow(workflow_name):
    """Manually trigger a workflow"""
    
    # Execute workflow immediately
    result = workflows.execute_workflow(workflow_name)
    
    return jsonify(result)
```

---

## Implementation Timeline

| Week | Phase | Tasks | Deliverables |
|------|-------|-------|--------------|
| 1-2 | Tool Infrastructure | Create all agent tools, schemas, registry | 25+ working tools |
| 2-3 | Configuration System | Database schema, config tools, defaults | Agent config system |
| 3-4 | Workflows | Define 6 autonomous workflows | Workflow definitions |
| 4-5 | Agent Core | Claude integration, orchestration loop | Working agent core |
| 5-6 | Safety & Monitoring | Permissions, audit logging, rate limiting | Safety layer |
| 6 | Dashboard Integration | Status dashboard, config UI, triggers | Management UI |
| 7 | Testing & Validation | End-to-end workflow testing | Test reports |
| 8 | Production Deployment | Deploy to production, monitor | Live system |

---

## File Structure

```
src/
├── services/
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── agent_core.py                    # Core agent with Claude
│   │   ├── tools_registry.py                # Tool registration system
│   │   ├── default_agent_config.py          # Default configuration
│   │   ├── agent_tools/
│   │   │   ├── __init__.py
│   │   │   ├── campaign_tools.py            # Campaign management tools
│   │   │   ├── collections_tools.py         # Collections tools
│   │   │   ├── invoice_tools.py             # Invoice tools
│   │   │   ├── access_tools.py              # Door access tools
│   │   │   ├── calendar_tools.py            # Calendar tools
│   │   │   ├── member_tools.py              # Member management tools
│   │   │   └── config_tools.py              # Configuration tools
│   │   ├── workflows/
│   │   │   ├── __init__.py
│   │   │   ├── autonomous_workflows.py      # Workflow definitions
│   │   │   └── workflow_scheduler.py        # APScheduler integration
│   │   └── safety/
│   │       ├── __init__.py
│   │       ├── permission_manager.py        # Tool permissions
│   │       └── audit_logger.py              # Audit logging
│   └── ... (existing services)
├── routes/
│   ├── agent_dashboard.py                   # Agent UI routes
│   └── ... (existing routes)
└── templates/
    ├── agent_status.html                    # Agent status dashboard
    ├── agent_config.html                    # Configuration UI
    └── ... (existing templates)
```

---

## Cost Estimate

### Claude 3.7 Sonnet Pricing
- Input: $3 per million tokens
- Output: $15 per million tokens

### Estimated Daily Usage
- **6 Workflows/day** (campaigns, monitoring, escalation, access management)
- **Avg 2,000 input tokens per workflow** = 12,000 input tokens/day
- **Avg 800 output tokens per workflow** = 4,800 output tokens/day

### Monthly Costs
- Input: 12,000 tokens/day × 30 days = 360,000 tokens = $1.08/month
- Output: 4,800 tokens/day × 30 days = 144,000 tokens = $2.16/month
- **Total: ~$3.24/month**

*Note: This is for autonomous scheduled workflows. Interactive agent usage would be additional.*

---

## Next Steps

1. **Review this plan** - Confirm requirements and approach
2. **Set up Anthropic API key** - `ANTHROPIC_API_KEY` in environment
3. **Create database tables** - Agent config, workflows, execution log
4. **Start with Phase 1** - Build first 5 tools (campaign tools)
5. **Test tool execution** - Validate each tool works with existing infrastructure
6. **Build agent core** - Implement Claude function calling loop
7. **Test first workflow** - Start with daily campaigns workflow
8. **Iterate and expand** - Add more tools and workflows

---

## Questions to Clarify

1. **Door Access System** - What system controls gym door access? Do we have API integration?
2. **Campaign Templates** - Where are campaign templates stored? Database or config files?
3. **PPV Member Classification** - How do we identify PPV (pre-paid visitor) members in the database?
4. **Collections Agency** - What format does the collections referral list need to be in?
5. **Manager Notifications** - Email? Dashboard? Both?
6. **Approval Workflow** - For high-risk actions, what approval mechanism do you want?

---

**Ready to begin implementation?** Let's start with Phase 1: Building the campaign management tools.
