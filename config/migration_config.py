"""
Migration Configuration

Central configuration for controlling Selenium to API migration behavior.
This file allows easy switching between migration modes and configuration options.
"""

import os
from typing import Dict, Any

# Migration mode configuration
# Options: "api_only", "hybrid", "selenium_only", "testing"
DEFAULT_MIGRATION_MODE = os.getenv("MIGRATION_MODE", "hybrid")

# Feature flags for gradual migration
MIGRATION_FEATURES = {
    # Core messaging features
    "api_messaging": True,              # Use API for send_clubos_message
    "api_message_retrieval": True,      # Use API for get_last_message_sender
    "api_conversations": True,          # Use API for conversation retrieval
    
    # Member management features  
    "api_member_search": True,          # Use API for member search
    "api_member_profiles": True,        # Use API for member profile access
    
    # Calendar features
    "api_calendar": True,               # Use API for calendar operations
    "api_training_sessions": True,      # Use API for training session management
    
    # Advanced features
    "api_reporting": False,             # Use API for reporting (limited support)
    "api_file_uploads": False,          # Use API for file uploads (not available)
    
    # Fallback configuration
    "selenium_fallback": True,          # Enable Selenium fallback
    "automatic_fallback": True,         # Automatic fallback on API failure
    "fallback_delay": 2,               # Delay before Selenium fallback (seconds)
}

# Performance and reliability settings
MIGRATION_CONFIG = {
    # API settings
    "api_timeout": 30,                  # API request timeout (seconds)
    "api_max_retries": 3,              # Maximum API retry attempts
    "api_retry_delay": 1,              # Delay between retries (seconds)
    
    # Selenium settings
    "selenium_timeout": 60,             # Selenium operation timeout (seconds)
    "selenium_page_load_timeout": 30,   # Page load timeout (seconds)
    "selenium_implicit_wait": 10,       # Implicit wait timeout (seconds)
    
    # Hybrid mode settings
    "enable_comparison": False,         # Enable API vs Selenium comparison
    "comparison_tolerance": 5,          # Time tolerance for comparisons (seconds)
    "log_performance": True,           # Log performance metrics
    
    # Rate limiting
    "api_rate_limit": 10,              # API calls per minute
    "selenium_rate_limit": 5,          # Selenium operations per minute
    
    # Caching
    "enable_api_caching": True,        # Enable API response caching
    "cache_timeout": 300,              # Cache timeout (seconds)
    
    # Error handling
    "max_consecutive_failures": 5,     # Max failures before disabling API
    "failure_cooldown": 60,            # Cooldown period after failures (seconds)
    
    # Logging
    "log_level": "INFO",               # Logging level
    "log_api_calls": True,             # Log all API calls
    "log_selenium_actions": False,     # Log Selenium actions (verbose)
}

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "production":
    # Production settings - prioritize reliability
    MIGRATION_CONFIG.update({
        "api_timeout": 45,
        "api_max_retries": 5,
        "selenium_fallback": True,
        "enable_comparison": False,
        "log_selenium_actions": False,
    })
elif os.getenv("ENVIRONMENT") == "testing":
    # Testing settings - enable all comparison features
    MIGRATION_CONFIG.update({
        "enable_comparison": True,
        "log_api_calls": True,
        "log_selenium_actions": True,
        "log_level": "DEBUG",
    })
elif os.getenv("ENVIRONMENT") == "development":
    # Development settings - optimize for debugging
    MIGRATION_CONFIG.update({
        "api_timeout": 15,
        "enable_comparison": True,
        "log_level": "DEBUG",
        "log_api_calls": True,
    })

# Workflow-specific migration settings
WORKFLOW_MIGRATION_CONFIG = {
    "overdue_payments": {
        "mode": DEFAULT_MIGRATION_MODE,
        "features": {
            "api_messaging": MIGRATION_FEATURES["api_messaging"],
            "api_member_search": MIGRATION_FEATURES["api_member_search"],
            "selenium_fallback": MIGRATION_FEATURES["selenium_fallback"],
        }
    },
    "member_messaging": {
        "mode": DEFAULT_MIGRATION_MODE,
        "features": {
            "api_messaging": MIGRATION_FEATURES["api_messaging"],
            "api_message_retrieval": MIGRATION_FEATURES["api_message_retrieval"],
            "api_conversations": MIGRATION_FEATURES["api_conversations"],
        }
    },
    "calendar_management": {
        "mode": DEFAULT_MIGRATION_MODE,
        "features": {
            "api_calendar": MIGRATION_FEATURES["api_calendar"],
            "api_training_sessions": MIGRATION_FEATURES["api_training_sessions"],
        }
    },
    "data_management": {
        "mode": "api_only",  # Data operations work well with API
        "features": {
            "api_member_search": True,
            "api_member_profiles": True,
        }
    }
}

# API endpoint configuration
API_ENDPOINTS = {
    "clubos": {
        "base_url": "https://anytime.club-os.com",
        "endpoints": {
            "messages": "/api/messages",
            "members": "/api/members",
            "calendar": "/api/calendar",
            "training": "/api/training",
        }
    },
    "clubhub": {
        "base_url": "https://clubhub-ios-api.anytimefitness.com",
        "endpoints": {
            "members": "/api/v1.0/clubs/1156/members",
            "prospects": "/api/v1.0/clubs/1156/prospects",
        }
    }
}

# Feature compatibility matrix
FEATURE_COMPATIBILITY = {
    "send_message": {
        "api_support": "full",          # full, partial, none
        "selenium_support": "full",
        "fallback_recommended": True,
    },
    "get_last_message_sender": {
        "api_support": "full",
        "selenium_support": "full", 
        "fallback_recommended": True,
    },
    "member_search": {
        "api_support": "full",
        "selenium_support": "full",
        "fallback_recommended": False,  # API is more reliable
    },
    "calendar_sessions": {
        "api_support": "partial",       # Some UI-dependent features
        "selenium_support": "full",
        "fallback_recommended": True,
    },
    "file_upload": {
        "api_support": "none",          # No API endpoint available
        "selenium_support": "full",
        "fallback_recommended": True,
    },
    "pdf_reports": {
        "api_support": "none",          # Generated via UI only
        "selenium_support": "full",
        "fallback_recommended": True,
    }
}


def get_migration_mode(workflow: str = None) -> str:
    """
    Get the migration mode for a specific workflow or global default.
    
    Args:
        workflow: Optional workflow name
        
    Returns:
        Migration mode string
    """
    if workflow and workflow in WORKFLOW_MIGRATION_CONFIG:
        return WORKFLOW_MIGRATION_CONFIG[workflow]["mode"]
    return DEFAULT_MIGRATION_MODE


def is_feature_enabled(feature: str, workflow: str = None) -> bool:
    """
    Check if a specific feature is enabled for migration.
    
    Args:
        feature: Feature name
        workflow: Optional workflow name
        
    Returns:
        True if feature is enabled for API migration
    """
    if workflow and workflow in WORKFLOW_MIGRATION_CONFIG:
        workflow_features = WORKFLOW_MIGRATION_CONFIG[workflow]["features"]
        if feature in workflow_features:
            return workflow_features[feature]
    
    return MIGRATION_FEATURES.get(feature, False)


def get_feature_compatibility(feature: str) -> Dict[str, Any]:
    """
    Get compatibility information for a feature.
    
    Args:
        feature: Feature name
        
    Returns:
        Compatibility information
    """
    return FEATURE_COMPATIBILITY.get(feature, {
        "api_support": "unknown",
        "selenium_support": "unknown",
        "fallback_recommended": True
    })


def should_use_api(feature: str, workflow: str = None) -> bool:
    """
    Determine if API should be used for a specific feature.
    
    Args:
        feature: Feature name
        workflow: Optional workflow name
        
    Returns:
        True if API should be used
    """
    if not is_feature_enabled(feature, workflow):
        return False
    
    compatibility = get_feature_compatibility(feature)
    return compatibility["api_support"] in ["full", "partial"]


def should_enable_fallback(feature: str) -> bool:
    """
    Determine if Selenium fallback should be enabled for a feature.
    
    Args:
        feature: Feature name
        
    Returns:
        True if fallback should be enabled
    """
    if not MIGRATION_FEATURES["selenium_fallback"]:
        return False
    
    compatibility = get_feature_compatibility(feature)
    return compatibility["fallback_recommended"]


# Export configuration for easy importing
__all__ = [
    'DEFAULT_MIGRATION_MODE',
    'MIGRATION_FEATURES', 
    'MIGRATION_CONFIG',
    'WORKFLOW_MIGRATION_CONFIG',
    'API_ENDPOINTS',
    'FEATURE_COMPATIBILITY',
    'get_migration_mode',
    'is_feature_enabled',
    'get_feature_compatibility', 
    'should_use_api',
    'should_enable_fallback'
]