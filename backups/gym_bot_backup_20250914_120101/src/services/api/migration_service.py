"""
Selenium to API Migration Service

This service handles the transition from Selenium-based workflows to API-based workflows.
It provides hybrid functionality and gradual migration capabilities.
"""

import time
import json
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime
from pathlib import Path
import logging

from src.services.api.enhanced_clubos_service import ClubOSAPIService
from src.services.authentication.clubhub_token_capture import get_valid_clubhub_tokens
from config.constants import CLUBOS_USERNAME_SECRET, CLUBOS_PASSWORD_SECRET
from config.secrets import get_secret


class SeleniumToAPIMigrationService:
    """
    Service to handle gradual migration from Selenium to API-based operations.
    Provides hybrid functionality and testing capabilities.
    """
    
    def __init__(self, migration_mode: str = "hybrid"):
        """
        Initialize migration service
        
        Args:
            migration_mode: "api_only", "selenium_only", "hybrid", or "testing"
        """
        self.migration_mode = migration_mode
        self.api_service = None
        self.selenium_fallback_enabled = migration_mode in ["hybrid", "testing"]
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Migration statistics
        self.stats = {
            "api_attempts": 0,
            "api_successes": 0,
            "selenium_fallbacks": 0,
            "total_operations": 0,
            "start_time": datetime.now()
        }
        
        # Configuration
        self.config = {
            "api_timeout": 30,
            "max_retries": 3,
            "fallback_delay": 2,
            "enable_comparison": migration_mode == "testing"
        }
        
        # Initialize API service if needed
        if migration_mode in ["api_only", "hybrid", "testing"]:
            self._initialize_api_service()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for migration tracking"""
        logger = logging.getLogger("SeleniumToAPIMigration")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create handler
        handler = logging.FileHandler(logs_dir / "selenium_to_api_migration.log")
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        
        return logger
    
    def _initialize_api_service(self) -> bool:
        """Initialize the API service with authentication"""
        try:
            username = get_secret(CLUBOS_USERNAME_SECRET)
            password = get_secret(CLUBOS_PASSWORD_SECRET)
            
            if not username or not password:
                self.logger.error("ClubOS credentials not available")
                return False
            
            self.api_service = ClubOSAPIService(username, password)
            self.logger.info("API service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize API service: {e}")
            return False
    
    def send_message(self, member_name: str, subject: str, body: str) -> Union[bool, str]:
        """
        Unified message sending that can use API or Selenium based on configuration
        
        Args:
            member_name: Name of the member to send message to
            subject: Message subject
            body: Message content
            
        Returns:
            True if successful, False if failed, "OPTED_OUT" if member opted out
        """
        self.stats["total_operations"] += 1
        operation_start = time.time()
        
        self.logger.info(f"Sending message to {member_name} via {self.migration_mode} mode")
        
        try:
            # API-first approach
            if self.migration_mode in ["api_only", "hybrid", "testing"]:
                result = self._send_message_api(member_name, subject, body)
                
                if result is not False:  # Success or OPTED_OUT
                    operation_time = time.time() - operation_start
                    self.logger.info(f"API message successful for {member_name} in {operation_time:.2f}s")
                    return result
                
                # If API failed and we're in hybrid mode, try Selenium
                if self.selenium_fallback_enabled:
                    self.logger.warning(f"API failed for {member_name}, trying Selenium fallback")
                    time.sleep(self.config["fallback_delay"])
                    return self._send_message_selenium(member_name, subject, body)
                else:
                    return False
            
            # Selenium-only mode
            elif self.migration_mode == "selenium_only":
                return self._send_message_selenium(member_name, subject, body)
            
            else:
                raise ValueError(f"Unknown migration mode: {self.migration_mode}")
                
        except Exception as e:
            self.logger.error(f"Error sending message to {member_name}: {e}")
            return False
    
    def _send_message_api(self, member_name: str, subject: str, body: str) -> Union[bool, str]:
        """Send message using API"""
        try:
            self.stats["api_attempts"] += 1
            
            if not self.api_service:
                raise Exception("API service not initialized")
            
            result = self.api_service.send_clubos_message(member_name, subject, body)
            
            if result is not False:
                self.stats["api_successes"] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"API send_message error for {member_name}: {e}")
            return False
    
    def _send_message_selenium(self, member_name: str, subject: str, body: str) -> Union[bool, str]:
        """Send message using Selenium fallback"""
        try:
            self.stats["selenium_fallbacks"] += 1
            
            # Import here to avoid circular imports
            from ...core.driver import setup_driver_and_login
            from ...services.clubos.messaging import send_clubos_message
            
            # Setup driver
            driver = setup_driver_and_login()
            if not driver:
                raise Exception("Failed to setup Selenium driver")
            
            try:
                result = send_clubos_message(driver, member_name, subject, body)
                self.logger.info(f"Selenium fallback successful for {member_name}")
                return result
            finally:
                driver.quit()
                
        except Exception as e:
            self.logger.error(f"Selenium fallback error for {member_name}: {e}")
            return False
    
    def get_last_message_sender(self) -> Optional[str]:
        """
        Get last message sender using API or Selenium based on configuration
        
        Returns:
            Member name of the most recent message sender, or None if failed
        """
        self.stats["total_operations"] += 1
        
        try:
            # API-first approach
            if self.migration_mode in ["api_only", "hybrid", "testing"]:
                result = self._get_last_message_sender_api()
                
                if result:
                    self.logger.info(f"API get_last_message_sender successful: {result}")
                    return result
                
                # Selenium fallback
                if self.selenium_fallback_enabled:
                    self.logger.warning("API failed, trying Selenium fallback for get_last_message_sender")
                    return self._get_last_message_sender_selenium()
                else:
                    return None
            
            # Selenium-only mode
            elif self.migration_mode == "selenium_only":
                return self._get_last_message_sender_selenium()
            
            else:
                raise ValueError(f"Unknown migration mode: {self.migration_mode}")
                
        except Exception as e:
            self.logger.error(f"Error getting last message sender: {e}")
            return None
    
    def _get_last_message_sender_api(self) -> Optional[str]:
        """Get last message sender using API"""
        try:
            self.stats["api_attempts"] += 1
            
            if not self.api_service:
                raise Exception("API service not initialized")
            
            result = self.api_service.get_last_message_sender()
            
            if result:
                self.stats["api_successes"] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"API get_last_message_sender error: {e}")
            return None
    
    def _get_last_message_sender_selenium(self) -> Optional[str]:
        """Get last message sender using Selenium"""
        try:
            self.stats["selenium_fallbacks"] += 1
            
            # Import here to avoid circular imports
            from ...core.driver import setup_driver_and_login
            from ...services.clubos.messaging import get_last_message_sender
            
            # Setup driver
            driver = setup_driver_and_login()
            if not driver:
                raise Exception("Failed to setup Selenium driver")
            
            try:
                result = get_last_message_sender(driver)
                self.logger.info(f"Selenium get_last_message_sender successful: {result}")
                return result
            finally:
                driver.quit()
                
        except Exception as e:
            self.logger.error(f"Selenium get_last_message_sender error: {e}")
            return None
    
    def get_member_conversation(self, member_name: str) -> List[Dict[str, Any]]:
        """
        Get member conversation using API or Selenium based on configuration
        
        Args:
            member_name: Name of the member
            
        Returns:
            List of conversation messages
        """
        self.stats["total_operations"] += 1
        
        try:
            # API-first approach
            if self.migration_mode in ["api_only", "hybrid", "testing"]:
                result = self._get_member_conversation_api(member_name)
                
                if result:
                    self.logger.info(f"API conversation retrieval successful for {member_name}: {len(result)} messages")
                    return result
                
                # Selenium fallback
                if self.selenium_fallback_enabled:
                    self.logger.warning(f"API failed, trying Selenium fallback for {member_name} conversation")
                    return self._get_member_conversation_selenium(member_name)
                else:
                    return []
            
            # Selenium-only mode
            elif self.migration_mode == "selenium_only":
                return self._get_member_conversation_selenium(member_name)
            
            else:
                raise ValueError(f"Unknown migration mode: {self.migration_mode}")
                
        except Exception as e:
            self.logger.error(f"Error getting conversation for {member_name}: {e}")
            return []
    
    def _get_member_conversation_api(self, member_name: str) -> List[Dict[str, Any]]:
        """Get member conversation using API"""
        try:
            self.stats["api_attempts"] += 1
            
            if not self.api_service:
                raise Exception("API service not initialized")
            
            result = self.api_service.scrape_conversation_for_contact(member_name)
            
            if result:
                self.stats["api_successes"] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"API get_member_conversation error for {member_name}: {e}")
            return []
    
    def _get_member_conversation_selenium(self, member_name: str) -> List[Dict[str, Any]]:
        """Get member conversation using Selenium"""
        try:
            self.stats["selenium_fallbacks"] += 1
            
            # Import here to avoid circular imports
            from ...core.driver import setup_driver_and_login
            # Note: Need to implement this function in the original messaging module
            # For now, return empty list
            
            self.logger.warning(f"Selenium conversation retrieval not yet implemented for {member_name}")
            return []
            
        except Exception as e:
            self.logger.error(f"Selenium get_member_conversation error for {member_name}: {e}")
            return []
    
    def calendar_operations(self, operation: str, **kwargs) -> Union[bool, Dict[str, Any], List[str]]:
        """
        Handle calendar operations using API or Selenium fallback.
        
        Args:
            operation: Calendar operation to perform
            **kwargs: Operation-specific parameters
            
        Returns:
            Operation result
        """
        self.stats["total_operations"] += 1      
        try:
            # API-first approach
            if self.migration_mode in ["api_only", "hybrid", "testing"]:
                result = self._calendar_operation_api(operation, **kwargs)
                
                if result is not None:
                    self.logger.info(f"API calendar operation '{operation}' successful")
                    return result
                
                # Selenium fallback
                if self.selenium_fallback_enabled:
                    self.logger.warning(f"API calendar operation '{operation}' failed, trying Selenium fallback")
                    return self._calendar_operation_selenium(operation, **kwargs)
                else:
                    return None
            
            # Selenium-only mode
            elif self.migration_mode == "selenium_only":
                return self._calendar_operation_selenium(operation, **kwargs)
            
            else:
                raise ValueError(f"Unknown migration mode: {self.migration_mode}")
                
        except Exception as e:
            self.logger.error(f"Error in calendar operation '{operation}': {e}")
            return None
    
    def _calendar_operation_api(self, operation: str, **kwargs):
        """Calendar operation using API"""
        try:
            from .calendar_api_service import ClubOSCalendarAPIService
            
            username = get_secret(CLUBOS_USERNAME_SECRET)
            password = get_secret(CLUBOS_PASSWORD_SECRET)
            
            if not username or not password:
                raise Exception("ClubOS credentials not available")
            
            calendar_service = ClubOSCalendarAPIService(username, password)
            
            if operation == "navigate_calendar_week":
                return calendar_service.navigate_calendar_week(kwargs.get('direction', 'next'))
            elif operation == "get_calendar_view_details":
                return calendar_service.get_calendar_view_details(kwargs.get('schedule_name', 'My schedule'))
            elif operation == "book_appointment":
                return calendar_service.book_appointment(kwargs)
            elif operation == "add_to_group_session":
                return calendar_service.add_to_group_session(kwargs)
            elif operation == "get_available_slots":
                return calendar_service.get_available_slots(kwargs.get('schedule_name', 'My schedule'))
            else:
                raise ValueError(f"Unknown calendar operation: {operation}")
                
        except Exception as e:
            self.logger.error(f"API calendar operation error: {e}")
            return None
    
    def _calendar_operation_selenium(self, operation: str, **kwargs):
        """Calendar operation using Selenium fallback"""
        try:
            self.stats["selenium_fallbacks"] += 1
            
            # Import here to avoid circular imports
            from ...core.driver import setup_driver_and_login
            from ...workflows.calendar_workflow import (
                navigate_calendar_week, get_calendar_view_details,
                book_appointment, add_to_group_session, get_available_slots
            )
            
            # Setup driver
            driver = setup_driver_and_login()
            if not driver:
                raise Exception("Failed to setup Selenium driver")
            
            try:
                if operation == "navigate_calendar_week":
                    return navigate_calendar_week(driver, kwargs.get('direction', 'next'))
                elif operation == "get_calendar_view_details":
                    return get_calendar_view_details(driver, kwargs.get('schedule_name', 'My schedule'))
                elif operation == "book_appointment":
                    return book_appointment(driver, kwargs)
                elif operation == "add_to_group_session":
                    return add_to_group_session(driver, kwargs)
                elif operation == "get_available_slots":
                    return get_available_slots(driver, kwargs.get('schedule_name', 'My schedule'))
                else:
                    raise ValueError(f"Unknown calendar operation: {operation}")
            finally:
                driver.quit()
                
        except Exception as e:
            self.logger.error(f"Selenium calendar operation error: {e}")
            return None
    
    def compare_api_vs_selenium(self, operation: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Run the same operation with both API and Selenium and compare results
        
        Args:
            operation: Name of the operation to compare
            *args, **kwargs: Arguments for the operation
            
        Returns:
            Comparison results
        """
        if self.migration_mode != "testing":
            raise ValueError("Comparison mode only available in testing mode")
        
        comparison_result = {
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "api_result": None,
            "selenium_result": None,
            "api_time": None,
            "selenium_time": None,
            "results_match": False,
            "errors": []
        }
        
        try:
            # Run API version
            api_start = time.time()
            try:
                if operation == "send_message":
                    comparison_result["api_result"] = self._send_message_api(*args, **kwargs)
                elif operation == "get_last_message_sender":
                    comparison_result["api_result"] = self._get_last_message_sender_api()
                elif operation == "get_member_conversation":
                    comparison_result["api_result"] = self._get_member_conversation_api(*args, **kwargs)
                else:
                    raise ValueError(f"Unknown operation: {operation}")
                
                comparison_result["api_time"] = time.time() - api_start
                
            except Exception as e:
                comparison_result["errors"].append(f"API error: {e}")
                comparison_result["api_time"] = time.time() - api_start
            
            # Run Selenium version
            selenium_start = time.time()
            try:
                if operation == "send_message":
                    comparison_result["selenium_result"] = self._send_message_selenium(*args, **kwargs)
                elif operation == "get_last_message_sender":
                    comparison_result["selenium_result"] = self._get_last_message_sender_selenium()
                elif operation == "get_member_conversation":
                    comparison_result["selenium_result"] = self._get_member_conversation_selenium(*args, **kwargs)
                
                comparison_result["selenium_time"] = time.time() - selenium_start
                
            except Exception as e:
                comparison_result["errors"].append(f"Selenium error: {e}")
                comparison_result["selenium_time"] = time.time() - selenium_start
            
            # Compare results
            comparison_result["results_match"] = self._compare_results(
                comparison_result["api_result"],
                comparison_result["selenium_result"]
            )
            
            # Log comparison
            self.logger.info(f"Comparison completed for {operation}: API={comparison_result['api_result']}, Selenium={comparison_result['selenium_result']}, Match={comparison_result['results_match']}")
            
            return comparison_result
            
        except Exception as e:
            comparison_result["errors"].append(f"Comparison error: {e}")
            return comparison_result
    
    def _compare_results(self, api_result: Any, selenium_result: Any) -> bool:
        """Compare API and Selenium results for equivalence"""
        try:
            # Direct comparison for simple types
            if type(api_result) == type(selenium_result):
                if isinstance(api_result, (str, bool, int, float)):
                    return api_result == selenium_result
                elif isinstance(api_result, list):
                    return len(api_result) == len(selenium_result)
                elif api_result is None and selenium_result is None:
                    return True
            
            # Consider both None and False as equivalent for some operations
            if api_result in [None, False] and selenium_result in [None, False]:
                return True
            
            # Consider both truthy results as equivalent for success operations
            if api_result and selenium_result:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error comparing results: {e}")
            return False
    
    def get_migration_stats(self) -> Dict[str, Any]:
        """Get migration statistics"""
        current_time = datetime.now()
        elapsed_time = (current_time - self.stats["start_time"]).total_seconds()
        
        stats = self.stats.copy()
        stats.update({
            "elapsed_time_seconds": elapsed_time,
            "api_success_rate": (self.stats["api_successes"] / max(self.stats["api_attempts"], 1)) * 100,
            "selenium_fallback_rate": (self.stats["selenium_fallbacks"] / max(self.stats["total_operations"], 1)) * 100,
            "current_time": current_time.isoformat()
        })
        
        return stats
    
    def save_migration_report(self, filename: Optional[str] = None) -> bool:
        """Save migration statistics and report"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"migration_report_{timestamp}.json"
            
            # Create reports directory
            reports_dir = Path("docs/migration_reports")
            reports_dir.mkdir(exist_ok=True)
            
            report_file = reports_dir / filename
            
            report_data = {
                "migration_mode": self.migration_mode,
                "statistics": self.get_migration_stats(),
                "configuration": self.config,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            self.logger.info(f"Migration report saved to {report_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving migration report: {e}")
            return False


# Global migration service instance
_migration_service = None


def get_migration_service(mode: str = "hybrid") -> SeleniumToAPIMigrationService:
    """Get or create global migration service instance"""
    global _migration_service
    
    if _migration_service is None or _migration_service.migration_mode != mode:
        _migration_service = SeleniumToAPIMigrationService(mode)
    
    return _migration_service


# Convenience functions that can be used as drop-in replacements
def send_clubos_message_migrated(member_name: str, subject: str, body: str) -> Union[bool, str]:
    """Drop-in replacement for send_clubos_message with migration support"""
    service = get_migration_service()
    return service.send_message(member_name, subject, body)


def get_last_message_sender_migrated() -> Optional[str]:
    """Drop-in replacement for get_last_message_sender with migration support"""
    service = get_migration_service()
    return service.get_last_message_sender()


def get_member_conversation_migrated(member_name: str) -> List[Dict[str, Any]]:
    """Drop-in replacement for member conversation retrieval with migration support"""
    service = get_migration_service()
    return service.get_member_conversation(member_name)


# Calendar API migration functions
def navigate_calendar_week_migrated(direction: str = "next") -> bool:
    """Drop-in replacement for calendar navigation with migration support"""
    service = get_migration_service()
    return service.calendar_operations("navigate_calendar_week", direction=direction)


def get_calendar_view_details_migrated(schedule_name: str = "My schedule") -> Dict[str, List[Dict]]:
    """Drop-in replacement for calendar view details with migration support"""
    service = get_migration_service()
    return service.calendar_operations("get_calendar_view_details", schedule_name=schedule_name)


def book_appointment_migrated(details: Dict[str, Any]) -> bool:
    """Drop-in replacement for appointment booking with migration support"""
    service = get_migration_service()
    return service.calendar_operations("book_appointment", **details)


def add_to_group_session_migrated(details: Dict[str, Any]) -> bool:
    """Drop-in replacement for adding to group session with migration support"""
    service = get_migration_service()
    return service.calendar_operations("add_to_group_session", **details)


def get_available_slots_migrated(schedule_name: str = "My schedule") -> List[str]:
    """Drop-in replacement for getting available slots with migration support"""
    service = get_migration_service()
    return service.calendar_operations("get_available_slots", schedule_name=schedule_name)