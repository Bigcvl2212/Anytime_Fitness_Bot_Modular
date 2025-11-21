"""Fetch agreement IDs from ClubHub member agreement endpoint"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import sqlite3
import logging
from src.services.api.clubhub_api_client import ClubHubAPIClient
from src.config.clubhub_credentials import get_clubhub_email, get_clubhub_password
import time

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("FETCHING AGREEMENT IDs FROM MEMBER AGREEMENT ENDPOINT")
logger.info("=" * 80)

# Get past due members without agreement IDs
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT
        id,
        guid,
        first_name || ' ' || last_name as name
    FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
    AND (agreement_id IS NULL OR agreement_id = '' OR agreement_id = 'N/A')
    ORDER BY amount_past_due DESC
""")

members_to_fix = cursor.fetchall()
total_members = len(members_to_fix)

logger.info(f"\nFound {total_members} past due members without agreement IDs")

# Authenticate
clubhub = ClubHubAPIClient()
email = get_clubhub_email()
password = get_clubhub_password()

logger.info(f"\nAuthenticating ClubHub...")
if not clubhub.authenticate(email, password):
    logger.error("ClubHub authentication failed!")
    sys.exit(1)

logger.info("ClubHub authentication successful!")

# Try fetching agreement data
logger.info("\n" + "=" * 80)
logger.info("FETCHING AGREEMENT DATA")
logger.info("=" * 80)

agreement_ids_found = 0
errors = 0

for i, (member_id, guid, name) in enumerate(members_to_fix, 1):
    try:
        logger.info(f"\n{i}/{total_members}: Checking {name}")
        logger.info(f"  Member GUID: {guid}")

        # Try the member agreement endpoint
        agreement_data = clubhub.get_member_agreement(guid)

        if agreement_data and not agreement_data.get('error'):
            # The response might have agreement info
            logger.info(f"  Agreement data found!")
            logger.info(f"  Response keys: {list(agreement_data.keys())}")

            # Look for agreement ID in various possible fields
            agreement_id = None
            possible_fields = ['id', 'agreementId', 'agreement_id', 'agreementNumber', 'number']

            for field in possible_fields:
                if field in agreement_data and agreement_data[field]:
                    agreement_id = str(agreement_data[field])
                    break

            if agreement_id:
                logger.info(f"  Agreement ID: {agreement_id}")

                # Update database
                cursor.execute("""
                    UPDATE members
                    SET agreement_id = ?
                    WHERE id = ?
                """, (agreement_id, member_id))

                agreement_ids_found += 1
            else:
                logger.warning(f"  No agreement ID field found in response")
                logger.info(f"  Full response: {agreement_data}")
        else:
            errors += 1
            logger.warning(f"  No agreement data available")

        # Small delay
        time.sleep(0.1)

    except Exception as e:
        errors += 1
        logger.error(f"Error processing {name}: {str(e)}")

conn.commit()
conn.close()

logger.info("\n" + "=" * 80)
logger.info("RESULTS")
logger.info("=" * 80)
logger.info(f"Total members processed: {total_members}")
logger.info(f"Agreement IDs found and updated: {agreement_ids_found}")
logger.info(f"Errors: {errors}")

logger.info("\nDone!")
