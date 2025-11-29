#!/usr/bin/env python3
"""
AI Automation Configuration
Central configuration for autonomous AI system behavior and safety settings
"""

# ============================================================================
# MASTER CONTROLS - Quick enable/disable switches
# ============================================================================

# Master switch for all AI automation
AI_SYSTEM_ENABLED = True

# Enable automatic message responses
AI_AUTO_RESPONSE_ENABLED = True

# Enable proactive outreach (campaigns, reminders)
AI_PROACTIVE_ENABLED = True

# Enable automatic workflow triggers
AI_WORKFLOW_TRIGGERS_ENABLED = True


# ============================================================================
# SAFETY SETTINGS - Rate limits and confidence thresholds
# ============================================================================

# Minimum confidence required for auto-response (0.0 - 1.0)
AI_CONFIDENCE_THRESHOLD = 0.80  # 80% confident

# Maximum auto-responses per hour (prevent spam)
AI_MAX_RESPONSES_PER_HOUR = 50

# Maximum proactive messages per day per member
AI_MAX_PROACTIVE_PER_MEMBER_PER_DAY = 2

# Cooldown period between AI messages to same member (seconds)
AI_MESSAGE_COOLDOWN = 300  # 5 minutes


# ============================================================================
# INTENT ROUTING - Which intents get automatic responses
# ============================================================================

# Intents that get automatic responses (high confidence, low risk)
AUTO_RESPOND_INTENTS = [
    'question_about_membership',
    'question_about_training',
    'question_about_schedule',
    'question_about_hours',
    'general_inquiry',
    'appointment_request',
    'appointment_confirmation'
]

# Intents that require human review (sensitive topics)
HUMAN_REVIEW_INTENTS = [
    'complaint',
    'angry_customer',
    'refund_request',
    'cancel_request',
    'billing_dispute',
    'threatening_language',
    'injury_report',
    'legal_inquiry'
]

# Intents that use Sales AI context (billing/collections)
SALES_AI_INTENTS = [
    'question_about_billing',
    'payment_inquiry',
    'invoice_question',
    'past_due_inquiry',
    'account_balance_question'
]


# ============================================================================
# WORKFLOW TRIGGERS - Automatic workflow execution
# ============================================================================

# Map intents to workflow names
WORKFLOW_TRIGGERS = {
    'question_about_billing': 'collections_workflow',
    'payment_inquiry': 'collections_workflow',
    'past_due_inquiry': 'high_priority_collections',
    'appointment_request': 'scheduling_workflow',
    'training_inquiry': 'training_upsell_workflow',
    'cancel_request': 'retention_workflow'
}

# Minimum past due amount to trigger collections workflow automatically
COLLECTIONS_TRIGGER_THRESHOLD = 50.00  # $50

# Minimum member lifetime value to trigger retention workflow
RETENTION_TRIGGER_LTV_THRESHOLD = 500.00  # $500


# ============================================================================
# PROACTIVE MONITORING - Autonomous outreach settings
# ============================================================================

# Enable daily past due monitoring
PROACTIVE_PAST_DUE_MONITORING = True

# Time to send past due reminders (24-hour format)
PAST_DUE_REMINDER_TIME = "09:00"  # 9 AM

# Days past due before sending reminder
PAST_DUE_REMINDER_DAYS = [3, 7, 14, 30]

# Enable appointment confirmation reminders
PROACTIVE_APPOINTMENT_CONFIRMATIONS = True

# Hours before appointment to send confirmation
APPOINTMENT_CONFIRMATION_HOURS = 24

# Enable inactive member outreach
PROACTIVE_INACTIVE_OUTREACH = True

# Days of inactivity before outreach
INACTIVE_MEMBER_DAYS = 14

# Enable new member welcome messages
PROACTIVE_NEW_MEMBER_WELCOME = True

# Hours after signup to send welcome message
NEW_MEMBER_WELCOME_DELAY_HOURS = 2


# ============================================================================
# ESCALATION RULES - When to alert humans
# ============================================================================

# Keywords that trigger immediate human alert
ESCALATION_KEYWORDS = [
    'lawyer',
    'attorney',
    'sue',
    'lawsuit',
    'police',
    'injured',
    'injury',
    'hurt',
    'emergency',
    'threat',
    'harass'
]

# Notify manager if member messages contain these phrases
ALERT_PHRASES = [
    'cancel my membership',
    'want a refund',
    'this is ridiculous',
    'terrible service',
    'worst gym',
    'report you'
]


# ============================================================================
# MESSAGING CONFIGURATION - Response formatting
# ============================================================================

# Include staff signature in AI responses
INCLUDE_STAFF_SIGNATURE = True

# Staff name for AI responses
AI_STAFF_NAME = "Jeremy"  # Or your gym manager name

# Staff title
AI_STAFF_TITLE = "Manager"

# Response tone
AI_RESPONSE_TONE = "friendly_professional"  # friendly_professional, casual, formal

# Maximum response length (characters)
AI_MAX_RESPONSE_LENGTH = 300

# Use emojis in responses
AI_USE_EMOJIS = False


# ============================================================================
# LOGGING AND AUDITING - Track all AI actions
# ============================================================================

# Log all AI responses to database
AI_LOG_ALL_RESPONSES = True

# Log AI decisions even if no response sent
AI_LOG_ALL_DECISIONS = True

# Retention period for AI logs (days)
AI_LOG_RETENTION_DAYS = 365

# Send daily summary email to manager
AI_DAILY_SUMMARY_ENABLED = True

# Email address for daily summaries
AI_SUMMARY_EMAIL = None  # Set to manager email


# ============================================================================
# TESTING AND ROLLOUT - Gradual deployment
# ============================================================================

# Test mode - AI generates responses but doesn't send
AI_TEST_MODE = False

# If test mode, which member IDs to actually send to (whitelist)
AI_TEST_WHITELIST = []  # ['member_id_1', 'member_id_2']

# Gradual rollout percentage (0-100)
AI_ROLLOUT_PERCENTAGE = 100  # 100% = all members


# ============================================================================
# ADVANCED SETTINGS - Fine-tuning
# ============================================================================

# Use conversation history for context
AI_USE_CONVERSATION_HISTORY = True

# Maximum conversation history messages to include
AI_MAX_HISTORY_MESSAGES = 10

# Re-classify intent if confidence below threshold
AI_RECLASSIFY_ON_LOW_CONFIDENCE = True

# Use member profile data in responses
AI_USE_MEMBER_PROFILE = True

# Cache AI responses for similar questions (minutes)
AI_RESPONSE_CACHE_TTL = 60


# ============================================================================
# MODEL CONFIGURATION - AI service settings
# ============================================================================

# AI model to use (Groq API with Llama)
AI_MODEL = "llama-3.3-70b-versatile"

# Maximum tokens for AI responses
AI_MAX_TOKENS = 500

# Temperature for response generation (0.0 - 1.0)
AI_TEMPERATURE = 0.7


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_ai_enabled() -> bool:
    """Check if AI system is enabled"""
    return AI_SYSTEM_ENABLED


def should_auto_respond(intent: str, confidence: float) -> bool:
    """
    Determine if AI should automatically respond

    Args:
        intent: Classified intent
        confidence: Confidence score (0.0 - 1.0)

    Returns:
        True if should auto-respond, False otherwise
    """
    if not AI_AUTO_RESPONSE_ENABLED:
        return False

    if confidence < AI_CONFIDENCE_THRESHOLD:
        return False

    if intent in HUMAN_REVIEW_INTENTS:
        return False

    if intent in AUTO_RESPOND_INTENTS:
        return True

    if intent in SALES_AI_INTENTS:
        return True

    return False


def should_trigger_workflow(intent: str, member_context: dict = None) -> tuple:
    """
    Determine if workflow should be triggered

    Args:
        intent: Classified intent
        member_context: Optional member data

    Returns:
        (should_trigger: bool, workflow_name: str or None)
    """
    if not AI_WORKFLOW_TRIGGERS_ENABLED:
        return False, None

    workflow_name = WORKFLOW_TRIGGERS.get(intent)

    if not workflow_name:
        return False, None

    # Additional checks for specific workflows
    if workflow_name == 'collections_workflow' and member_context:
        past_due = member_context.get('past_due_amount', 0)
        if past_due < COLLECTIONS_TRIGGER_THRESHOLD:
            return False, None

    if workflow_name == 'retention_workflow' and member_context:
        ltv = member_context.get('lifetime_value', 0)
        if ltv < RETENTION_TRIGGER_LTV_THRESHOLD:
            return False, None

    return True, workflow_name


def needs_human_review(intent: str, content: str) -> tuple:
    """
    Determine if message needs human review

    Args:
        intent: Classified intent
        content: Message content

    Returns:
        (needs_review: bool, reason: str or None)
    """
    # Check intent
    if intent in HUMAN_REVIEW_INTENTS:
        return True, f"sensitive_intent: {intent}"

    # Check escalation keywords
    content_lower = content.lower()
    for keyword in ESCALATION_KEYWORDS:
        if keyword in content_lower:
            return True, f"escalation_keyword: {keyword}"

    # Check alert phrases
    for phrase in ALERT_PHRASES:
        if phrase in content_lower:
            return True, f"alert_phrase: {phrase}"

    return False, None
