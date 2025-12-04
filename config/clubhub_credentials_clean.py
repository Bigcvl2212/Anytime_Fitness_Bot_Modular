"""
ClubHub credentials configuration
This file should be added to .gitignore to keep credentials secure
Supports environment variables with secure fallbacks
"""

import os

# ClubHub login credentials - environment variables with secure fallbacks
CLUBHUB_EMAIL = os.getenv('CLUBHUB_EMAIL', "mayo.jeremy2212@gmail.com")
CLUBHUB_PASSWORD = os.getenv('CLUBHUB_PASSWORD', "fygxy9-sybses-suvtYc")

# ClubOS login credentials - environment variables with secure fallbacks
CLUBOS_USERNAME = os.getenv('CLUBOS_USERNAME', "j.mayo")
CLUBOS_PASSWORD = os.getenv('CLUBOS_PASSWORD', "Ls$gpZ98L!hht.G")

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
