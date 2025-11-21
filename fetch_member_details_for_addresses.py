"""Try to fetch addresses from ClubHub member details endpoint"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import sqlite3
import logging
from src.services.api.clubhub_api_client import ClubHubAPIClient
from src.config.clubhub_credentials import get_clubhub_email, get_clubhub_password

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("FETCHING MEMBER DETAILS FOR ADDRESS DATA")
logger.info("=" * 80)

# Get past due members without addresses
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
    AND (address IS NULL OR address = '' OR address = 'NULL')
    ORDER BY amount_past_due DESC
    LIMIT 3
""")

members_to_check = cursor.fetchall()
logger.info(f"\nChecking {len(members_to_check)} members...")

# Authenticate
clubhub = ClubHubAPIClient()
email = get_clubhub_email()
password = get_clubhub_password()

logger.info(f"\nAuthenticating ClubHub...")
if not clubhub.authenticate(email, password):
    logger.error("ClubHub authentication failed!")
    sys.exit(1)

logger.info("ClubHub authentication successful!")

# Try fetching member details for each
logger.info("\n" + "=" * 80)
logger.info("CHECKING MEMBER DETAILS ENDPOINT FOR ADDRESSES")
logger.info("=" * 80)

addresses_found = 0
for member_id, guid, name in members_to_check:
    logger.info(f"\nChecking: {name}")
    logger.info(f"  Member GUID: {guid}")

    # Try to fetch member details
    try:
        # Use the built-in method
        member_details = clubhub.get_member_details(guid)

        if member_details and not member_details.get('error'):
            # Get address fields (ClubHub uses address1, address2, city, state, zip)
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

            if address:
                logger.info(f"  Address FOUND: {address}")
                logger.info(f"  City: {city if city else 'N/A'}")
                logger.info(f"  State: {state if state else 'N/A'}")
                logger.info(f"  Zip: {zip_code if zip_code else 'N/A'}")
                addresses_found += 1

                # Update database
                cursor.execute("""
                    UPDATE members
                    SET address = ?, city = ?, state = ?, zip_code = ?
                    WHERE id = ?
                """, (address, city, state, zip_code, member_id))
            else:
                logger.info(f"  Address: NOT FOUND in member details")
                # Log all available fields for debugging
                logger.info(f"  Available fields: {list(member_details.keys())}")
        else:
            logger.error(f"  Failed to fetch member details")

    except Exception as e:
        logger.error(f"  Error: {str(e)}")

conn.commit()
conn.close()

logger.info("\n" + "=" * 80)
logger.info("RESULTS")
logger.info("=" * 80)
logger.info(f"Addresses found and updated: {addresses_found}/{len(members_to_check)}")

if addresses_found == 0:
    logger.warning("\nClubHub member details endpoint does NOT contain address data.")
    logger.warning("The address data simply doesn't exist in ClubHub for these members.")
