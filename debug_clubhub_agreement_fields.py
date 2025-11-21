"""Debug: Look at ALL fields from ClubHub member details to find agreement ID"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import sqlite3
import logging
import json
from src.services.api.clubhub_api_client import ClubHubAPIClient
from src.config.clubhub_credentials import get_clubhub_email, get_clubhub_password

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get a member WITHOUT an agreement ID to debug
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT
        id,
        guid,
        first_name || ' ' || last_name as name,
        agreement_id
    FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
    ORDER BY amount_past_due DESC
    LIMIT 5
""")

members = cursor.fetchall()
conn.close()

# Authenticate
clubhub = ClubHubAPIClient()
email = get_clubhub_email()
password = get_clubhub_password()

logger.info("Authenticating ClubHub...")
if not clubhub.authenticate(email, password):
    logger.error("Authentication failed!")
    sys.exit(1)

logger.info("Authentication successful!\n")

# Fetch details for each member and show ALL fields
for member_id, guid, name, current_agreement_id in members:
    logger.info("=" * 80)
    logger.info(f"Member: {name}")
    logger.info(f"Current Agreement ID in DB: {current_agreement_id if current_agreement_id else 'NONE'}")
    logger.info(f"Member GUID: {guid}")
    logger.info("-" * 80)

    # Fetch member details
    member_details = clubhub.get_member_details(guid)

    if member_details and not member_details.get('error'):
        logger.info("ALL FIELDS FROM CLUBHUB MEMBER DETAILS:")
        logger.info(json.dumps(member_details, indent=2))
        logger.info("")
        logger.info("AGREEMENT-RELATED FIELDS:")
        for key, value in member_details.items():
            if 'agree' in key.lower() or 'id' in key.lower() or 'contract' in key.lower():
                logger.info(f"  {key}: {value}")
    else:
        logger.error("Failed to fetch member details")

    logger.info("")
