"""
ClubHub credentials configuration
Simple direct credential access without circular imports
"""

import os
import logging

logger = logging.getLogger(__name__)

def get_clubhub_email():
    """Get ClubHub email from environment or default"""
    email = os.getenv('CLUBHUB_EMAIL', "mayo.jeremy2212@gmail.com")
    return email

def get_clubhub_password():
    """Get ClubHub password from environment or default"""
    password = os.getenv('CLUBHUB_PASSWORD', "fygxy9-sybses-suvtYc")
    return password

def get_clubos_username():
    """Get ClubOS username from environment or default"""
    username = os.getenv('CLUBOS_USERNAME') or os.getenv('CLUBOS_EMAIL', "j.mayo")
    return username

def get_clubos_password():
    """Get ClubOS password from environment or default"""
    password = os.getenv('CLUBOS_PASSWORD', "Ls$gpZ98L!hht.G")
    return password

# Backwards compatibility - provide the old variable names
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