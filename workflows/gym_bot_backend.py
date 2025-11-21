"""
Gym Bot Backend Module
Main backend interface for the Anytime Fitness Bot Modular system.

This module provides a unified interface to all the modular components
and handles proper package structure for imports.
"""

import sys
import os
import logging
from typing import Optional, Dict, Any, List

# Add the current directory to Python path for proper imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CORE BACKEND COMPONENTS
# =============================================================================

class GymBotCore:
    """Core functionality for driver and authentication management."""
    
    def __init__(self):
        self._driver = None
        self._initialized = False
    
    def get_driver(self, headless: bool = True):
        """Get or create WebDriver instance."""
        try:
            from core.driver import setup_chrome_driver
            if not self._driver:
                self._driver = setup_chrome_driver()
            return self._driver
        except Exception as e:
            logger.error(f"Failed to setup driver: {e}")
            return None
    
    def login_to_clubos(self, driver=None):
        """Login to ClubOS system."""
        try:
            if driver is None:
                driver = self.get_driver()
            
            from core.driver import login_to_clubos as _login
            return _login(driver)
        except Exception as e:
            logger.error(f"Failed to login to ClubOS: {e}")
            return False
    
    def close_driver(self):
        """Close WebDriver and cleanup."""
        try:
            if self._driver:
                self._driver.quit()
                self._driver = None
        except Exception as e:
            logger.error(f"Error closing driver: {e}")

class GymBotServices:
    """Service layer for AI, payments, messaging, etc."""
    
    def __init__(self):
        self._services = {}
    
    def get_gemini_client(self):
        """Get Gemini AI client."""
        try:
            if 'gemini' not in self._services:
                from src.services.ai.gemini import get_gemini_client
                self._services['gemini'] = get_gemini_client()
            return self._services['gemini']
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            return None
    
    def get_square_client(self):
        """Get Square payment client."""
        try:
            if 'square' not in self._services:
                from src.services.payments.square_client_fixed import get_square_client
                client = get_square_client()
                if client is not None:
                    self._services['square'] = client
                else:
                    logger.warning("Square client returned None - credentials may be missing")
                    return None
            return self._services['square']
        except Exception as e:
            logger.error(f"Failed to initialize Square client: {e}")
            return None
    
    def get_messaging_service(self, driver=None):
        """Get ClubOS messaging service."""
        try:
            if 'messaging' not in self._services:
                from src.services.clubos.messaging import get_messaging_service
                self._services['messaging'] = get_messaging_service(driver)
            return self._services['messaging']
        except Exception as e:
            logger.error(f"Failed to initialize messaging service: {e}")
            return None
    
    def test_square_connection(self) -> bool:
        """Test Square API connection."""
        try:
            from src.services.payments.square_client_fixed import test_square_connection
            return test_square_connection()
        except Exception as e:
            logger.error(f"Square connection test failed: {e}")
            return False

class GymBotConfig:
    """Configuration management."""
    
    def __init__(self):
        self._config = {}
    
    @property
    def GCP_PROJECT_ID(self):
        """Get Google Cloud Project ID."""
        try:
            from config.secrets import GCP_PROJECT_ID
            return GCP_PROJECT_ID
        except Exception as e:
            logger.error(f"Failed to get GCP Project ID: {e}")
            return ""
    
    def get_secret(self, secret_name: str, default: Optional[str] = None):
        """Get secret value."""
        try:
            from config.secrets import get_secret
            return get_secret(secret_name, default)
        except Exception as e:
            logger.error(f"Failed to get secret {secret_name}: {e}")
            return default
    
    def get_square_secrets(self):
        """Get Square API secrets."""
        try:
            from config.secrets import get_square_secrets
            return get_square_secrets()
        except Exception as e:
            logger.error(f"Failed to get Square secrets: {e}")
            return {}
    
    def get_clubos_credentials(self):
        """Get ClubOS credentials."""
        try:
            from config.secrets import get_clubos_credentials
            return get_clubos_credentials()
        except Exception as e:
            logger.error(f"Failed to get ClubOS credentials: {e}")
            return {}

# =============================================================================
# UNIFIED BACKEND INTERFACE
# =============================================================================

class GymBotBackend:
    """Main backend interface for the Gym Bot system."""
    
    def __init__(self):
        self.core = GymBotCore()
        self.services = GymBotServices()
        self.config = GymBotConfig()
        self._initialized = False
        
        logger.info("GymBotBackend initialized")
    
    def initialize(self) -> bool:
        """Initialize all backend services."""
        try:
            logger.info("Initializing Gym Bot Backend...")
            
            # Test basic imports
            success = True
            
            # Test config
            try:
                _ = self.config.GCP_PROJECT_ID
                logger.info("✅ Config module loaded")
            except Exception as e:
                logger.error(f"❌ Config module failed: {e}")
                success = False
            
            # Test core (without actually creating driver)
            try:
                # Just test that we can import the modules
                import core.driver
                logger.info("✅ Core module loaded")
            except Exception as e:
                logger.error(f"❌ Core module failed: {e}")
                success = False
            
            # Test services (without creating instances)
            try:
                import src.services.ai.gemini
                import src.services.payments.square_client_fixed
                logger.info("✅ Services modules loaded")
            except Exception as e:
                logger.error(f"❌ Services modules failed: {e}")
                success = False
            
            self._initialized = success
            
            if success:
                logger.info("✅ Gym Bot Backend initialized successfully")
            else:
                logger.error("❌ Gym Bot Backend initialization failed")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Backend initialization error: {e}")
            return False
    
    def get_driver(self, headless: bool = True):
        """Get WebDriver instance."""
        return self.core.get_driver(headless)
    
    def login_to_clubos(self, driver=None):
        """Login to ClubOS."""
        return self.core.login_to_clubos(driver)
    
    def close_driver(self):
        """Close WebDriver."""
        self.core.close_driver()
    
    def get_gemini_client(self):
        """Get Gemini AI client."""
        return self.services.get_gemini_client()
    
    def get_square_client(self):
        """Get Square payment client."""
        return self.services.get_square_client()
    
    def get_messaging_service(self, driver=None):
        """Get messaging service."""
        return self.services.get_messaging_service(driver)
    
    def test_connections(self) -> Dict[str, bool]:
        """Test all service connections."""
        results = {}
        
        # Test Square
        try:
            results['square'] = self.services.test_square_connection()
        except Exception as e:
            logger.error(f"Square test failed: {e}")
            results['square'] = False
        
        # Test ClubOS (basic login test)
        try:
            driver = self.get_driver(headless=True)
            if driver:
                results['clubos'] = self.login_to_clubos(driver)
                self.close_driver()
            else:
                results['clubos'] = False
        except Exception as e:
            logger.error(f"ClubOS test failed: {e}")
            results['clubos'] = False
        
        # Test Gemini AI
        try:
            client = self.get_gemini_client()
            results['gemini'] = client is not None
        except Exception as e:
            logger.error(f"Gemini test failed: {e}")
            results['gemini'] = False
        
        return results

# =============================================================================
# GLOBAL BACKEND INSTANCE AND COMPATIBILITY FUNCTIONS
# =============================================================================

# Global backend instance
_backend = None

def get_backend() -> GymBotBackend:
    """Get the global backend instance."""
    global _backend
    if _backend is None:
        _backend = GymBotBackend()
    return _backend

# Compatibility functions for existing code
def get_driver(headless: bool = True):
    """Get WebDriver instance (compatibility function)."""
    return get_backend().get_driver(headless)

def login_to_clubos(driver=None):
    """Login to ClubOS (compatibility function)."""
    return get_backend().login_to_clubos(driver)

def close_driver():
    """Close WebDriver (compatibility function)."""
    get_backend().close_driver()

def get_gemini_client():
    """Get Gemini AI client (compatibility function)."""
    return get_backend().get_gemini_client()

def get_square_client():
    """Get Square payment client (compatibility function)."""
    return get_backend().get_square_client()

def get_messaging_service(driver=None):
    """Get messaging service (compatibility function)."""
    return get_backend().get_messaging_service(driver)

def test_square_connection() -> bool:
    """Test Square connection (compatibility function)."""
    return get_backend().services.test_square_connection()

def initialize_services() -> bool:
    """Initialize all services (compatibility function)."""
    return get_backend().initialize()

# =============================================================================
# MODULE CONSTANTS
# =============================================================================

# Re-export important constants
try:
    from config.constants import *
    from config.secrets import GCP_PROJECT_ID
except ImportError as e:
    logger.warning(f"Could not import constants: {e}")
    GCP_PROJECT_ID = ""

if __name__ == "__main__":
    # Test the backend when run directly
    backend = get_backend()
    success = backend.initialize()
    
    if success:
        print("✅ Gym Bot Backend is working correctly!")
        
        # Test connections
        print("\n🔍 Testing connections...")
        connections = backend.test_connections()
        
        for service, status in connections.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {service.capitalize()}: {'Connected' if status else 'Failed'}")
    else:
        print("❌ Gym Bot Backend initialization failed!")
        sys.exit(1)