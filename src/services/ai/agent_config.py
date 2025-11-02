"""
AI Agent Configuration
Configurable settings for autonomous workflows
"""

import os
from typing import Dict, Any

class AgentConfig:
    """Configuration for AI agent autonomous workflows"""
    
    # ============================================
    # WORKFLOW SCHEDULING
    # ============================================
    
    # Daily campaigns workflow (6 AM daily)
    DAILY_CAMPAIGNS_ENABLED = True
    DAILY_CAMPAIGNS_HOUR = 6  # 6 AM
    DAILY_CAMPAIGNS_MINUTE = 0
    
    # Hourly past due monitoring
    PAST_DUE_MONITORING_ENABLED = True
    PAST_DUE_CHECK_INTERVAL_MINUTES = 60  # Every hour
    
    # Daily escalation workflow (8 AM daily)
    DAILY_ESCALATION_ENABLED = True
    DAILY_ESCALATION_HOUR = 8  # 8 AM
    DAILY_ESCALATION_MINUTE = 0
    
    # Bi-weekly referral checks (every other Monday at 9 AM)
    REFERRAL_CHECKS_ENABLED = True
    REFERRAL_CHECK_DAY = 'mon'  # Monday
    REFERRAL_CHECK_HOUR = 9
    REFERRAL_CHECK_MINUTE = 0
    REFERRAL_CHECK_WEEK_INTERVAL = 2  # Every 2 weeks
    
    # Monthly invoice review (1st of month at 10 AM)
    MONTHLY_INVOICE_REVIEW_ENABLED = True
    INVOICE_REVIEW_DAY = 1  # 1st of month
    INVOICE_REVIEW_HOUR = 10
    INVOICE_REVIEW_MINUTE = 0
    
    # Hourly door access management
    DOOR_ACCESS_MANAGEMENT_ENABLED = True
    DOOR_ACCESS_CHECK_INTERVAL_MINUTES = 60  # Every hour
    
    # ============================================
    # WORKFLOW BEHAVIOR SETTINGS
    # ============================================
    
    # Past Due Thresholds
    PAST_DUE_WARNING_DAYS = 7  # Send warning after 7 days
    PAST_DUE_URGENT_DAYS = 30  # Urgent reminder after 30 days
    PAST_DUE_ESCALATION_DAYS = 60  # Escalate to collections after 60 days
    
    # Campaign Settings
    MAX_CAMPAIGN_RECIPIENTS = 1000  # Max recipients per campaign batch
    CAMPAIGN_COOLDOWN_DAYS = 7  # Don't send same campaign within 7 days
    
    # Door Access Settings
    AUTO_LOCK_PAST_DUE_DAYS = 14  # Auto-lock after 14 days past due
    AUTO_UNLOCK_ON_PAYMENT = True  # Auto-unlock when payment received
    
    # Collection Settings
    MIN_PAST_DUE_AMOUNT = 50.00  # Minimum amount to send to collections
    COLLECTIONS_REFERRAL_THRESHOLD = 60  # Days past due for collections
    
    # ============================================
    # AGENT EXECUTION SETTINGS
    # ============================================
    
    # Maximum iterations for agent task execution
    MAX_AGENT_ITERATIONS = 10
    
    # Timeout for agent tasks (seconds)
    AGENT_TASK_TIMEOUT = 300  # 5 minutes
    
    # Retry settings
    MAX_TASK_RETRIES = 3
    RETRY_DELAY_SECONDS = 60
    
    # ============================================
    # SAFETY & CONFIRMATION SETTINGS
    # ============================================
    
    # Require confirmation before destructive actions
    REQUIRE_CONFIRMATION_FOR_BULK_ACTIONS = True
    REQUIRE_CONFIRMATION_FOR_DOOR_LOCK = True
    REQUIRE_CONFIRMATION_FOR_COLLECTIONS_REFERRAL = True
    
    # Dry run mode (test without actual execution)
    DRY_RUN_MODE = os.getenv('AI_AGENT_DRY_RUN', 'false').lower() == 'true'
    
    # Notification settings
    NOTIFY_ON_WORKFLOW_COMPLETION = True
    NOTIFY_ON_WORKFLOW_ERROR = True
    NOTIFICATION_EMAIL = os.getenv('ADMIN_EMAIL', 'mayo.jeremy2212@gmail.com')
    
    # ============================================
    # LOGGING & MONITORING
    # ============================================
    
    # Log workflow execution results
    LOG_WORKFLOW_RESULTS = True
    WORKFLOW_LOG_PATH = 'logs/workflows/'
    
    # Store execution history in database
    STORE_EXECUTION_HISTORY = True
    
    # Performance monitoring
    MONITOR_API_COSTS = True  # Track Claude API costs per workflow
    MONITOR_EXECUTION_TIME = True
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get all config as dictionary"""
        config = {}
        for key in dir(cls):
            if key.isupper() and not key.startswith('_'):
                config[key] = getattr(cls, key)
        return config
    
    @classmethod
    def is_workflow_enabled(cls, workflow_name: str) -> bool:
        """Check if a specific workflow is enabled"""
        enabled_key = f"{workflow_name.upper()}_ENABLED"
        return getattr(cls, enabled_key, False)
    
    @classmethod
    def get_workflow_schedule(cls, workflow_name: str) -> Dict[str, Any]:
        """Get schedule settings for a workflow"""
        schedule = {}
        prefix = workflow_name.upper()
        
        for key in dir(cls):
            if key.startswith(prefix) and key.isupper():
                schedule[key] = getattr(cls, key)
        
        return schedule
