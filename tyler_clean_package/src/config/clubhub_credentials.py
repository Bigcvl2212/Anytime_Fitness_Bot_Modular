"""
ClubHub credentials configuration
This file uses SecureSecretsManager for secure credential access
"""

from ..services.authentication.secure_secrets_manager import SecureSecretsManager
import logging

logger = logging.getLogger(__name__)

# Initialize secrets manager
_secrets_manager = SecureSecretsManager()

def get_clubhub_email():
    """Get ClubHub email from secure storage"""
    email = _secrets_manager.get_secret('clubhub-email')
    if not email:
        logger.error("❌ ClubHub email not found in SecureSecretsManager")
        return None
    return email

def get_clubhub_password():
    """Get ClubHub password from secure storage"""
    password = _secrets_manager.get_secret('clubhub-password')
    if not password:
        logger.error("❌ ClubHub password not found in SecureSecretsManager")
        return None
    return password

def get_clubos_username():
    """Get ClubOS username from secure storage"""
    username = _secrets_manager.get_secret('clubos-username')
    if not username:
        logger.error("❌ ClubOS username not found in SecureSecretsManager")
        return None
    return username

def get_clubos_password():
    """Get ClubOS password from secure storage"""
    password = _secrets_manager.get_secret('clubos-password')
    if not password:
        logger.error("❌ ClubOS password not found in SecureSecretsManager")
        return None
    return password

# Backwards compatibility - provide the old variable names but with secure access
CLUBHUB_EMAIL = get_clubhub_email()
CLUBHUB_PASSWORD = get_clubhub_password()
CLUBOS_USERNAME = get_clubos_username()
CLUBOS_PASSWORD = get_clubos_password()

# ClubHub API configuration
import os
CLUBHUB_BASE_URL = os.getenv('CLUBHUB_BASE_URL', 'https://clubhub-ios-api.anytimefitness.com')
CLUBHUB_CLUB_ID = os.getenv('DEFAULT_CLUB_ID', '1156')

# API endpoints discovered from HAR files
def get_clubhub_endpoints():
    return {
        "members": f"/api/clubs/{CLUBHUB_CLUB_ID}/members",
        "prospects": f"/api/clubs/{CLUBHUB_CLUB_ID}/prospects", 
        "contacts": f"/api/clubs/{CLUBHUB_CLUB_ID}/contacts",
        "master_contact_list": f"/api/clubs/{CLUBHUB_CLUB_ID}/master-contact-list",
        "member_details": f"/api/clubs/{CLUBHUB_CLUB_ID}/members/{{member_id}}",
        "prospect_details": f"/api/clubs/{CLUBHUB_CLUB_ID}/prospects/{{prospect_id}}",
    } 
CLUBHUB_API_ENDPOINTS = {
    "members": f"/api/clubs/{CLUBHUB_CLUB_ID}/members",
    "prospects": f"/api/clubs/{CLUBHUB_CLUB_ID}/prospects",
    "contacts": f"/api/clubs/{CLUBHUB_CLUB_ID}/contacts",
    "master_contact_list": f"/api/clubs/{CLUBHUB_CLUB_ID}/master-contact-list",
    "member_details": f"/api/clubs/{CLUBHUB_CLUB_ID}/members/{{member_id}}",
    "prospect_details": f"/api/clubs/{CLUBHUB_CLUB_ID}/prospects/{{prospect_id}}",
} 