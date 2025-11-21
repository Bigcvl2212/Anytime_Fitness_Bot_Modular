"""Fetch agreement IDs using prospect_id instead of GUID for members without agreement IDs"""
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
logger.info("FETCHING AGREEMENT IDs USING PROSPECT_ID")
logger.info("=" * 80)

# Get past due members without agreement IDs
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT
        id,
        guid,
        prospect_id,
        first_name || ' ' || last_name as name
    FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
    AND (agreement_id IS NULL OR agreement_id = '' OR agreement_id = 'N/A')
    AND prospect_id IS NOT NULL AND prospect_id != ''
    ORDER BY amount_past_due DESC
""")

members_to_fix = cursor.fetchall()
total_members = len(members_to_fix)

logger.info(f"\nFound {total_members} past due members without agreement IDs but with prospect_id")

# Authenticate
clubhub = ClubHubAPIClient()
email = get_clubhub_email()
password = get_clubhub_password()

logger.info(f"\nAuthenticating ClubHub...")
if not clubhub.authenticate(email, password):
    logger.error("ClubHub authentication failed!")
    sys.exit(1)

logger.info("ClubHub authentication successful!")

# Try fetching using prospect_id
logger.info("\n" + "=" * 80)
logger.info("FETCHING USING PROSPECT_ID")
logger.info("=" * 80)

agreement_ids_found = 0
errors = 0

for i, (member_id, guid, prospect_id, name) in enumerate(members_to_fix, 1):
    try:
        logger.info(f"\n{i}/{total_members}: {name}")
        logger.info(f"  Current GUID (not working): {guid}")
        logger.info(f"  Trying prospect_id: {prospect_id}")

        # Try using prospect_id to fetch member details
        member_details = clubhub.get_member_details(prospect_id)

        if member_details and not member_details.get('error'):
            agreement_id = member_details.get('agreementId')

            if agreement_id:
                logger.info(f"  SUCCESS! Agreement ID: {agreement_id}")

                # Update database with both agreement_id and the correct guid
                cursor.execute("""
                    UPDATE members
                    SET agreement_id = ?, guid = ?
                    WHERE id = ?
                """, (str(agreement_id), str(prospect_id), member_id))

                agreement_ids_found += 1
            else:
                logger.warning(f"  Member details fetched but no agreement ID")
        else:
            errors += 1
            logger.warning(f"  Failed to fetch using prospect_id")

        time.sleep(0.05)

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
