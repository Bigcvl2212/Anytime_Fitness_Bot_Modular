"""Full ClubHub member refresh to fix category counts"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'src'))

import logging
import sqlite3
from services.api.clubhub_api_client import ClubHubAPIClient
from services.authentication.secure_secrets_manager import SecureSecretsManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("FULL CLUBHUB MEMBER REFRESH")
logger.info("=" * 80)

# Get credentials
logger.info("\n1. Getting ClubHub credentials...")
secrets_manager = SecureSecretsManager()
email = secrets_manager.get_secret('clubhub-email')
password = secrets_manager.get_secret('clubhub-password')

if not email or not password:
    logger.error("Failed to get ClubHub credentials!")
    sys.exit(1)

logger.info(f"Got credentials - Email: {email}")

# Initialize ClubHub client
logger.info("\n2. Initializing ClubHub client...")
client = ClubHubAPIClient()

# Authenticate
logger.info("\n3. Authenticating with ClubHub...")
if not client.authenticate(email, password):
    logger.error("ClubHub authentication failed!")
    sys.exit(1)

logger.info("ClubHub authentication successful!")

# Fetch ALL members
logger.info("\n4. Fetching ALL members from ClubHub...")
logger.info("   (This may take a minute - fetching all pages in parallel...)")
try:
    all_members = client.get_all_members_paginated()  # Get all members with pagination
    logger.info(f"Successfully fetched {len(all_members)} members from ClubHub")
except Exception as e:
    logger.error(f"Failed to fetch members: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)

# Analyze status messages
logger.info("\n5. Analyzing member status messages...")
status_counts = {}
for member in all_members:
    status = member.get('statusMessage', 'NULL')
    status_counts[status] = status_counts.get(status, 0) + 1

logger.info("\nStatus message distribution:")
for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
    logger.info(f"  {count:4d} - {status}")

# Save to database
logger.info("\n6. Saving members to database...")
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Clear existing members first
logger.info("Clearing existing members...")
cursor.execute("DELETE FROM members")
conn.commit()

# Insert all members
saved_count = 0
for member in all_members:
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO members (
                guid, prospect_id, first_name, last_name, full_name, email, phone,
                status_message, member_type, agreement_id, agreement_type,
                agreement_recurring_cost, amount_past_due, address, city, state, zip_code,
                join_date, club_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            member.get('guid'),
            member.get('prospectId') or member.get('id'),
            member.get('firstName'),
            member.get('lastName'),
            f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
            member.get('email'),
            member.get('phone'),
            member.get('statusMessage'),  # THIS IS THE KEY FIELD
            member.get('memberType'),
            member.get('agreementId'),
            member.get('agreementType'),
            member.get('monthlyDues') or member.get('agreementRecurringCost') or 0.0,
            member.get('amountPastDue') or 0.0,
            member.get('address1') or member.get('address'),
            member.get('city'),
            member.get('state'),
            member.get('zip'),
            member.get('joinDate'),
            member.get('clubName', 'Anytime Fitness FDL')
        ))
        saved_count += 1
    except Exception as e:
        logger.warning(f"Failed to save member {member.get('firstName')} {member.get('lastName')}: {e}")
        continue

conn.commit()
logger.info(f"Saved {saved_count} members to database")

# Verify counts
logger.info("\n7. Verifying category counts...")
cursor.execute("SELECT COUNT(*) FROM members WHERE status_message = 'Member is in good standing'")
green = cursor.fetchone()[0]
logger.info(f"Green (good standing): {green}")

cursor.execute("SELECT COUNT(*) FROM members WHERE status_message = 'Comp Member'")
comp = cursor.fetchone()[0]
logger.info(f"Comp: {comp}")

cursor.execute("SELECT COUNT(*) FROM members WHERE status_message = 'Pay Per Visit Member'")
ppv = cursor.fetchone()[0]
logger.info(f"PPV: {ppv}")

cursor.execute("SELECT COUNT(*) FROM members WHERE status_message LIKE '%Past Due%'")
past_due = cursor.fetchone()[0]
logger.info(f"Past Due: {past_due}")

cursor.execute("SELECT COUNT(*) FROM members WHERE status_message = 'Staff Member'")
staff = cursor.fetchone()[0]
logger.info(f"Staff: {staff}")

cursor.execute("SELECT COUNT(*) FROM members WHERE status_message IS NULL OR status_message = ''")
null_status = cursor.fetchone()[0]
logger.info(f"NULL/Empty status: {null_status}")

conn.close()

logger.info("\n" + "=" * 80)
logger.info("REFRESH COMPLETE!")
logger.info("=" * 80)
logger.info(f"\nTotal members refreshed: {saved_count}")
logger.info(f"Expected counts:")
logger.info(f"  Green: 286 (Got: {green})")
logger.info(f"  Comp: 34 (Got: {comp})")
logger.info(f"  PPV: 119 (Got: {ppv})")
logger.info("\nThe member counts should now match ClubHub!")
