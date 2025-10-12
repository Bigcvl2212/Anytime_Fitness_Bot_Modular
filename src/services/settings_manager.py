"""
Settings Manager Service
Centralized configuration management for the Gym Bot
"""

import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

# Handle imports for both src.services and direct imports
try:
    from .database_manager import DatabaseManager
except ImportError:
    from services.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class SettingsManager:
    """Centralized settings management with caching and validation"""
    
    # Default settings for all categories
    DEFAULTS = {
        "ai_agent": {
            "model": "claude-3-7-sonnet-20250219",
            "max_iterations": 10,
            "confidence_threshold": "medium",  # low, medium, high
            "dry_run_mode": True,
            "api_rate_limit": 4,  # requests per minute
            "token_limit": 40000,  # tokens per minute
            
            # Custom AI instructions and context
            "custom_system_prompt": "",
            "collections_rules": "",
            "campaign_guidelines": "",
            "tone_and_voice": "",
            "forbidden_actions": "",
            "business_context": "",
            "escalation_triggers": ""
        },
        "workflows": {
            "daily_campaigns_enabled": True,
            "daily_campaigns_time": "06:00",
            "daily_campaigns_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "daily_campaigns_timezone": "America/Chicago",
            
            "past_due_monitoring_enabled": True,
            "past_due_monitoring_frequency": "hourly",  # 30min, hourly, 2hours, 4hours
            "past_due_monitoring_business_hours_only": True,
            
            "collections_escalation_enabled": True,
            "collections_escalation_time": "08:00",
            "collections_escalation_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
            
            "collections_referral_enabled": True,
            "collections_referral_frequency": "biweekly",  # weekly, biweekly, monthly
            "collections_referral_day": "monday",
            "collections_referral_time": "09:00",
            
            "training_compliance_enabled": True,
            "training_compliance_time": "07:00",
            "training_compliance_days": ["monday", "wednesday", "friday"],
            
            "funding_sync_enabled": True,
            "funding_sync_frequency": "6hours"  # 4hours, 6hours, 12hours, daily
        },
        "collections": {
            "min_past_due_amount": 0.01,
            "high_priority_amount": 100.00,
            "urgent_amount": 200.00,
            
            "auto_lock_enabled": False,
            "lock_threshold": 100.00,
            "lock_after_attempts": 4,
            "grace_period_days": 7,
            
            "friendly_reminder_max_amount": 50.00,
            "friendly_reminder_max_attempts": 1,
            
            "firm_reminder_min_amount": 50.01,
            "firm_reminder_max_amount": 100.00,
            "firm_reminder_min_attempts": 2,
            "firm_reminder_max_attempts": 3,
            
            "final_notice_min_amount": 100.01,
            "final_notice_min_attempts": 4,
            
            "referral_min_amount": 50.00,
            "referral_min_attempts": 3,
            "referral_min_days_past_due": 14
        },
        "messaging": {
            "default_channel": "email",  # sms, email, both
            "max_recipients_per_campaign": 100,
            "sending_rate_limit": 10,  # messages per minute
            "retry_failed_messages": True,
            "max_retries": 2,
            "honor_opt_outs": True,
            "auto_add_stop_text": True
        },
        "campaigns": {
            "prospects_enabled": True,
            "prospects_exclude_statuses": ["not_interested"],
            "prospects_max_days_since_contact": 30,
            
            "green_members_enabled": True,
            "green_members_days_since_signup": 30,
            "green_members_exclude_free_trials": False,
            
            "ppv_enabled": True,
            "ppv_min_visits": 3,
            "ppv_max_days_since_visit": 14
        },
        "approvals": {
            "require_approval_lock_multiple": True,
            "require_approval_lock_threshold": 10,
            
            "require_approval_campaign_large": True,
            "require_approval_campaign_threshold": 100,
            
            "require_approval_collections_referral": True,
            "require_approval_workflow_changes": True,
            
            "require_approval_high_amount_reminder": False,
            "high_amount_threshold": 100.00,
            
            "require_approval_individual_lock": True,
            
            "notification_method": "dashboard",  # dashboard, email, sms, all
            "approval_timeout_hours": 4,
            "timeout_action": "deny"  # approve, deny, escalate
        },
        "notifications": {
            "daily_summary_enabled": True,
            "daily_summary_time": "18:00",
            
            "workflow_failures_enabled": True,
            "high_priority_collections_enabled": True,
            "high_priority_threshold": 200.00,
            
            "approval_requests_enabled": True,
            
            "email": "",
            "sms_phone": "",
            "slack_webhook": "",
            "teams_webhook": ""
        },
        "dashboard": {
            "theme": "dark",  # light, dark, auto
            "default_view": "sales_ai",  # overview, members, prospects, training_clients, sales_ai, calendar
            "data_refresh_rate": 30,  # seconds
            "default_date_range": "30days",  # 7days, 30days, 90days
            "currency_symbol": "$"
        },
        "data_sync": {
            "members_auto_sync": True,
            "members_sync_frequency": "6hours",
            
            "prospects_auto_sync": True,
            "prospects_sync_frequency": "6hours",
            
            "training_clients_auto_sync": True,
            "training_clients_sync_frequency": "12hours",
            
            "calendar_sync_enabled": True,
            "calendar_sync_frequency": "15min",
            "calendar_include_past": False,
            "calendar_days_ahead": 30,
            
            "auto_archive_enabled": False,
            "archive_after_days": 365
        },
        "compliance": {
            "mask_pii_in_logs": True,
            "auto_delete_logs_days": 90,
            "require_canspam_compliance": True,
            "require_tcpa_compliance": True,
            "include_physical_address": True,
            "log_all_actions": True,
            "log_ai_decisions": True
        },
        "testing": {
            "test_mode_enabled": False,
            "debug_logging_enabled": False,
            "log_level": "INFO"  # INFO, DEBUG, TRACE
        }
    }
    
    def __init__(self):
        """Initialize settings manager"""
        self.db = DatabaseManager()
        self.cache = {}
        self._init_database()
        self._load_cache()
    
    def _init_database(self):
        """Initialize settings tables in database"""
        try:
            # Create settings table
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS bot_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    setting_key TEXT NOT NULL,
                    setting_value TEXT,
                    data_type TEXT DEFAULT 'string',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT DEFAULT 'system',
                    UNIQUE(category, setting_key)
                )
            """)
            
            # Create settings history table
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS settings_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    setting_key TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    changed_by TEXT DEFAULT 'system',
                    reason TEXT
                )
            """)
            
            logger.info("✅ Settings tables initialized")
            
            # Load defaults if tables are empty
            count_result = self.db.execute_query("SELECT COUNT(*) as count FROM bot_settings", fetch_one=True)
            if count_result and count_result[0] == 0:
                logger.info("📥 Loading default settings...")
                self._load_defaults()
                
        except Exception as e:
            logger.error(f"❌ Error initializing settings database: {e}")
    
    def _load_defaults(self):
        """Load default settings into database"""
        try:
            for category, settings in self.DEFAULTS.items():
                for key, value in settings.items():
                    self._save_to_db(category, key, value, user="system")
            logger.info("✅ Default settings loaded")
        except Exception as e:
            logger.error(f"❌ Error loading defaults: {e}")
    
    def _load_cache(self):
        """Load all settings into memory cache"""
        try:
            rows = self.db.execute_query("SELECT * FROM bot_settings", fetch_all=True)
            if rows:
                for row in rows:
                    cache_key = f"{row[1]}.{row[2]}"  # row[1]=category, row[2]=setting_key
                    self.cache[cache_key] = self._deserialize(row[3], row[4])  # row[3]=setting_value, row[4]=data_type
            logger.info(f"✅ Loaded {len(self.cache)} settings into cache")
        except Exception as e:
            logger.error(f"❌ Error loading cache: {e}")
    
    def get(self, category: str, key: str, default: Any = None) -> Any:
        """
        Get setting value with caching
        
        Args:
            category: Setting category (ai_agent, workflows, etc.)
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        cache_key = f"{category}.{key}"
        
        # Try cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try database
        try:
            row = self.db.execute_query(
                "SELECT setting_value, data_type FROM bot_settings WHERE category = ? AND setting_key = ?",
                (category, key),
                fetch_one=True
            )
            if row:
                value = self._deserialize(row[0], row[1])  # row[0]=setting_value, row[1]=data_type
                self.cache[cache_key] = value
                return value
        except Exception as e:
            logger.error(f"❌ Error getting setting {category}.{key}: {e}")
        
        # Return default
        if default is not None:
            return default
        
        # Return from DEFAULTS
        return self.DEFAULTS.get(category, {}).get(key)
    
    def set(self, category: str, key: str, value: Any, user: str = "system", reason: str = None) -> bool:
        """
        Set setting value and log change
        
        Args:
            category: Setting category
            key: Setting key
            value: New value
            user: User making the change
            reason: Reason for change (optional)
            
        Returns:
            Success status
        """
        try:
            # Get old value for history
            old_value = self.get(category, key)
            
            # Validate setting
            if not self._validate_setting(category, key, value):
                logger.error(f"❌ Invalid value for {category}.{key}: {value}")
                return False
            
            # Save to database
            success = self._save_to_db(category, key, value, user)
            
            if success:
                # Update cache
                cache_key = f"{category}.{key}"
                self.cache[cache_key] = value
                
                # Log to history
                self._log_history(category, key, old_value, value, user, reason)
                
                logger.info(f"✅ Updated {category}.{key} = {value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error setting {category}.{key}: {e}")
            return False
    
    def get_category(self, category: str) -> Dict[str, Any]:
        """
        Get all settings in a category
        
        Args:
            category: Setting category
            
        Returns:
            Dictionary of all settings in category
        """
        try:
            rows = self.db.execute_query(
                "SELECT setting_key, setting_value, data_type FROM bot_settings WHERE category = ?",
                (category,),
                fetch_all=True
            )
            
            result = {}
            if rows:
                for row in rows:
                    result[row[0]] = self._deserialize(row[1], row[2])  # row[0]=setting_key, row[1]=setting_value, row[2]=data_type
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting category {category}: {e}")
            return {}
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all settings grouped by category
        
        Returns:
            Dictionary of all settings grouped by category
        """
        try:
            rows = self.db.execute_query("SELECT * FROM bot_settings", fetch_all=True)
            
            result = {}
            if rows:
                for row in rows:
                    category = row[1]  # row[1]=category
                    if category not in result:
                        result[category] = {}
                    result[category][row[2]] = self._deserialize(row[3], row[4])  # row[2]=setting_key, row[3]=setting_value, row[4]=data_type
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting all settings: {e}")
            return {}
    
    def reset_category(self, category: str, user: str = "system") -> bool:
        """
        Reset category to default values
        
        Args:
            category: Setting category to reset
            user: User making the change
            
        Returns:
            Success status
        """
        try:
            if category not in self.DEFAULTS:
                logger.error(f"❌ Unknown category: {category}")
                return False
            
            defaults = self.DEFAULTS[category]
            success_count = 0
            
            for key, value in defaults.items():
                if self.set(category, key, value, user, reason=f"Reset {category} to defaults"):
                    success_count += 1
            
            logger.info(f"✅ Reset {success_count} settings in {category} to defaults")
            return success_count == len(defaults)
            
        except Exception as e:
            logger.error(f"❌ Error resetting category {category}: {e}")
            return False
    
    def get_history(self, category: str, key: str, limit: int = 10) -> List[Dict]:
        """
        Get change history for a setting
        
        Args:
            category: Setting category
            key: Setting key
            limit: Maximum number of history entries
            
        Returns:
            List of history entries
        """
        try:
            rows = self.db.execute_query("""
                SELECT * FROM settings_history 
                WHERE category = ? AND setting_key = ?
                ORDER BY changed_at DESC
                LIMIT ?
            """, (category, key, limit), fetch_all=True)
            
            # Convert tuple rows to dicts
            history = []
            if rows:
                for row in rows:
                    history.append({
                        'id': row[0],
                        'category': row[1],
                        'setting_key': row[2],
                        'old_value': row[3],
                        'new_value': row[4],
                        'changed_at': row[5],
                        'changed_by': row[6],
                        'reason': row[7]
                    })
            return history
            
        except Exception as e:
            logger.error(f"❌ Error getting history for {category}.{key}: {e}")
            return []
    
    def export_settings(self) -> str:
        """
        Export all settings as JSON
        
        Returns:
            JSON string of all settings
        """
        try:
            all_settings = self.get_all()
            return json.dumps(all_settings, indent=2)
        except Exception as e:
            logger.error(f"❌ Error exporting settings: {e}")
            return "{}"
    
    def import_settings(self, json_str: str, user: str = "system") -> bool:
        """
        Import settings from JSON
        
        Args:
            json_str: JSON string of settings
            user: User making the import
            
        Returns:
            Success status
        """
        try:
            settings = json.loads(json_str)
            success_count = 0
            
            for category, category_settings in settings.items():
                for key, value in category_settings.items():
                    if self.set(category, key, value, user, reason="Settings import"):
                        success_count += 1
            
            logger.info(f"✅ Imported {success_count} settings")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error importing settings: {e}")
            return False
    
    def _validate_setting(self, category: str, key: str, value: Any) -> bool:
        """Validate setting value"""
        # Add validation rules as needed
        # For now, basic type checking
        
        if category == "ai_agent":
            if key == "max_iterations" and (not isinstance(value, int) or value < 5 or value > 20):
                return False
            if key == "confidence_threshold" and value not in ["low", "medium", "high"]:
                return False
            if key == "api_rate_limit" and (not isinstance(value, (int, float)) or value <= 0):
                return False
        
        if category == "collections":
            if "amount" in key and (not isinstance(value, (int, float)) or value < 0):
                return False
        
        return True
    
    def _save_to_db(self, category: str, key: str, value: Any, user: str) -> bool:
        """Save setting to database"""
        try:
            serialized_value, data_type = self._serialize(value)
            
            self.db.execute_query("""
                INSERT OR REPLACE INTO bot_settings 
                (category, setting_key, setting_value, data_type, last_updated, updated_by)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            """, (category, key, serialized_value, data_type, user))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving to database: {e}")
            return False
    
    def _log_history(self, category: str, key: str, old_value: Any, new_value: Any, user: str, reason: str):
        """Log setting change to history"""
        try:
            old_serialized, _ = self._serialize(old_value)
            new_serialized, _ = self._serialize(new_value)
            
            self.db.execute_query("""
                INSERT INTO settings_history 
                (category, setting_key, old_value, new_value, changed_at, changed_by, reason)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
            """, (category, key, old_serialized, new_serialized, user, reason))
            
        except Exception as e:
            logger.error(f"❌ Error logging history: {e}")
    
    def _serialize(self, value: Any) -> tuple:
        """Serialize value for storage"""
        if isinstance(value, bool):
            return (str(value), "bool")
        elif isinstance(value, int):
            return (str(value), "int")
        elif isinstance(value, float):
            return (str(value), "float")
        elif isinstance(value, (list, dict)):
            return (json.dumps(value), "json")
        else:
            return (str(value), "string")
    
    def _deserialize(self, value: str, data_type: str) -> Any:
        """Deserialize value from storage"""
        if data_type == "bool":
            return value.lower() == "true"
        elif data_type == "int":
            return int(value)
        elif data_type == "float":
            return float(value)
        elif data_type == "json":
            return json.loads(value)
        else:
            return value


# Global settings manager instance
_settings_manager = None

def get_settings_manager() -> SettingsManager:
    """Get global settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager
