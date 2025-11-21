"""Fetch addresses from ClubHub member details for all members without addresses"""
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
logger.info("FIXING ALL MISSING ADDRESSES FROM CLUBHUB MEMBER DETAILS")
logger.info("=" * 80)

# Get ALL members without addresses
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT
        id,
        guid,
        first_name || ' ' || last_name as name
    FROM members
    WHERE (address IS NULL OR address = '' OR address = 'NULL')
    AND guid IS NOT NULL AND guid != ''
""")

members_to_fix = cursor.fetchall()
total_members = len(members_to_fix)

logger.info(f"\nFound {total_members} members without addresses")
logger.info("These members will be updated with addresses from ClubHub member details endpoint")

# Authenticate
clubhub = ClubHubAPIClient()
email = get_clubhub_email()
password = get_clubhub_password()

logger.info(f"\nAuthenticating ClubHub...")
if not clubhub.authenticate(email, password):
    logger.error("ClubHub authentication failed!")
    sys.exit(1)

logger.info("ClubHub authentication successful!")

# Fetch addresses for each member
logger.info("\n" + "=" * 80)
logger.info("FETCHING ADDRESSES")
logger.info("=" * 80)

addresses_found = 0
addresses_not_found = 0
errors = 0

for i, (member_id, guid, name) in enumerate(members_to_fix, 1):
    try:
        # Progress indicator
        if i % 10 == 0:
            logger.info(f"Progress: {i}/{total_members} ({i/total_members*100:.1f}%)")

        # Fetch member details
        member_details = clubhub.get_member_details(guid)

        if member_details and not member_details.get('error'):
            # Get address fields
            address = member_details.get('address1')
            address2 = member_details.get('address2')
            city = member_details.get('city')
            state = member_details.get('state')
            zip_code = member_details.get('zip')

            # Combine address1 and address2 if both exist
            if address and address2:
                address = f"{address} {address2}"
            elif address2 and not address:
                address = address2

            if address or city or state or zip_code:
                # Update database
                cursor.execute("""
                    UPDATE members
                    SET address = ?, city = ?, state = ?, zip_code = ?
                    WHERE id = ?
                """, (address, city, state, zip_code, member_id))

                addresses_found += 1
                logger.debug(f"{name:30} - Address: {address}")
            else:
                addresses_not_found += 1
                logger.debug(f"{name:30} - No address data")
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
logger.info(f"Addresses found and updated: {addresses_found}")
logger.info(f"No address data available: {addresses_not_found}")
logger.info(f"Errors: {errors}")

# Verify past due members now have addresses
cursor.execute("""
    SELECT COUNT(*) FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
    AND (address IS NOT NULL AND address != '' AND address != 'NULL')
""")

past_due_with_addresses = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
""")

total_past_due = cursor.fetchone()[0]

logger.info("\n" + "=" * 80)
logger.info("PAST DUE MEMBERS ADDRESS STATUS")
logger.info("=" * 80)
logger.info(f"Past due members with addresses: {past_due_with_addresses}/{total_past_due} ({past_due_with_addresses/total_past_due*100:.1f}%)")

conn.close()

logger.info("\nSUCCESS! All available addresses have been synced from ClubHub.")
