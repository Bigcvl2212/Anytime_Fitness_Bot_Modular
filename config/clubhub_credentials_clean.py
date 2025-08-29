#!/usr/bin/env python3
"""ClubHub credentials config placeholder.
Loads credentials from environment variables to avoid hardcoding."""
import os

CLUBHUB_EMAIL = os.getenv('CLUBHUB_EMAIL', '')
CLUBHUB_PASSWORD = os.getenv('CLUBHUB_PASSWORD', '')

# Fallback warning
if not CLUBHUB_EMAIL or not CLUBHUB_PASSWORD:
    import logging
    logging.getLogger(__name__).warning('CLUBHUB_EMAIL or CLUBHUB_PASSWORD not set in env vars')

# ClubOS login credentials
CLUBOS_USERNAME = "j.mayo"
CLUBOS_PASSWORD = "j@SD4fjhANK5WNA"

# ClubHub API configuration
CLUBHUB_BASE_URL = "https://clubhub-ios-api.anytimefitness.com"
CLUBHUB_CLUB_ID = "1156"  # From the API endpoints we discovered

# API endpoints discovered from HAR files
CLUBHUB_API_ENDPOINTS = {
    "members": f"/api/clubs/{CLUBHUB_CLUB_ID}/members",
    "prospects": f"/api/clubs/{CLUBHUB_CLUB_ID}/prospects",
    "contacts": f"/api/clubs/{CLUBHUB_CLUB_ID}/contacts",
    "master_contact_list": f"/api/clubs/{CLUBHUB_CLUB_ID}/master-contact-list",
    "member_details": f"/api/clubs/{CLUBHUB_CLUB_ID}/members/{{member_id}}",
    "prospect_details": f"/api/clubs/{CLUBHUB_CLUB_ID}/prospects/{{prospect_id}}",
}
