"""Fetch agreement IDs from ClubHub member details for all members"""
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
logger.info("FETCHING AGREEMENT IDs FROM CLUBHUB")
logger.info("=" * 80)

# Get all members without agreement IDs
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT
        id,
        guid,
        first_name || ' ' || last_name as name,
        agreement_id
    FROM members
    WHERE guid IS NOT NULL AND guid != ''
    AND (agreement_id IS NULL OR agreement_id = '' OR agreement_id = 'N/A')
""")

members_to_fix = cursor.fetchall()
total_members = len(members_to_fix)

logger.info(f"\nFound {total_members} members without agreement IDs")

# Authenticate
clubhub = ClubHubAPIClient()
email = get_clubhub_email()
password = get_clubhub_password()

logger.info(f"\nAuthenticating ClubHub...")
if not clubhub.authenticate(email, password):
    logger.error("ClubHub authentication failed!")
    sys.exit(1)

logger.info("ClubHub authentication successful!")

# Fetch agreement IDs for each member
logger.info("\n" + "=" * 80)
logger.info("FETCHING AGREEMENT IDs")
logger.info("=" * 80)

agreement_ids_found = 0
agreement_ids_not_found = 0
errors = 0

for i, (member_id, guid, name, current_agreement_id) in enumerate(members_to_fix, 1):
    try:
        # Progress indicator
        if i % 25 == 0:
            logger.info(f"Progress: {i}/{total_members} ({i/total_members*100:.1f}%)")

        # Fetch member details
        member_details = clubhub.get_member_details(guid)

        if member_details and not member_details.get('error'):
            # Get agreement fields
            agreement_id = member_details.get('agreementId')
            agreement_guid = member_details.get('agreementGuid')  # Also get GUID if available

            if agreement_id:
                # Update database with both agreement_id and agreement_guid
                cursor.execute("""
                    UPDATE members
                    SET agreement_id = ?, agreement_guid = ?
                    WHERE id = ?
                """, (str(agreement_id), agreement_guid, member_id))

                agreement_ids_found += 1
                logger.debug(f"{name:30} - Agreement ID: {agreement_id}")
            else:
                agreement_ids_not_found += 1
                logger.debug(f"{name:30} - No agreement ID")
        else:
            errors += 1
            logger.warning(f"{name:30} - Error fetching details")

        # Small delay to avoid rate limiting
        time.sleep(0.05)

    except Exception as e:
        errors += 1
        logger.error(f"Error processing {name}: {str(e)}")

conn.commit()

logger.info("\n" + "=" * 80)
logger.info("RESULTS")
logger.info("=" * 80)
logger.info(f"Total members processed: {total_members}")
logger.info(f"Agreement IDs found and updated: {agreement_ids_found}")
logger.info(f"No agreement ID available: {agreement_ids_not_found}")
logger.info(f"Errors: {errors}")

# Verify past due members now have agreement IDs
cursor.execute("""
    SELECT COUNT(*) FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
    AND agreement_id IS NOT NULL AND agreement_id != '' AND agreement_id != 'N/A'
""")

past_due_with_agreement_ids = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
""")

total_past_due = cursor.fetchone()[0]

logger.info("\n" + "=" * 80)
logger.info("PAST DUE MEMBERS AGREEMENT ID STATUS")
logger.info("=" * 80)
logger.info(f"Past due members with agreement IDs: {past_due_with_agreement_ids}/{total_past_due} ({past_due_with_agreement_ids/total_past_due*100:.1f}%)")

# Show sample of past due members with their new agreement IDs
cursor.execute("""
    SELECT
        first_name || ' ' || last_name as name,
        agreement_id,
        amount_past_due
    FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
    ORDER BY amount_past_due DESC
    LIMIT 10
""")

logger.info("\nSample of Past Due Members with Agreement IDs:")
logger.info("-" * 80)
for name, agreement_id, past_due in cursor.fetchall():
    logger.info(f"{name:30} | Agreement: {agreement_id if agreement_id else 'N/A':15} | Past Due: ${past_due:8.2f}")

conn.close()

logger.info("\nSUCCESS! All available agreement IDs have been synced from ClubHub.")
