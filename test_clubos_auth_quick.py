"""Quick test of ClubOS authentication fix"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.services.authentication.unified_auth_service import UnifiedAuthService
from src.config.clubhub_credentials import get_clubos_username, get_clubos_password
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("Testing ClubOS Authentication Fix")
logger.info("=" * 80)

# Get credentials
username = get_clubos_username()
password = get_clubos_password()

logger.info(f"Username: {username}")
logger.info(f"Password: {'*' * len(password) if password else 'NONE'}")

# Create auth service
auth_service = UnifiedAuthService()

# Test authentication
logger.info("\nAttempting ClubOS authentication...")
session = auth_service.authenticate_clubos(username, password)

if session and session.authenticated:
    logger.info("\n" + "=" * 80)
    logger.info("✅ SUCCESS! ClubOS Authentication Working")
    logger.info("=" * 80)
    logger.info(f"Session ID: {session.session_id}")
    logger.info(f"User ID: {session.logged_in_user_id}")
    logger.info(f"Base URL: {session.base_url}")
    logger.info(f"Authenticated: {session.authenticated}")
else:
    logger.error("\n" + "=" * 80)
    logger.error("❌ FAILED - ClubOS Authentication Not Working")
    logger.error("=" * 80)
