"""Investigate why specific past due members don't have addresses"""
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Get past due members without addresses
cursor.execute("""
    SELECT
        id,
        prospect_id,
        first_name || ' ' || last_name as name,
        email,
        phone,
        amount_past_due
    FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
    AND (address IS NULL OR address = '' OR address = 'NULL')
    ORDER BY amount_past_due DESC
    LIMIT 10
""")

members_no_address = cursor.fetchall()

logger.info("=" * 80)
logger.info("PAST DUE MEMBERS WITHOUT ADDRESSES")
logger.info("=" * 80)
logger.info("")

for member_id, prospect_id, name, email, phone, past_due in members_no_address:
    logger.info(f"Name: {name}")
    logger.info(f"  Member ID: {member_id}")
    logger.info(f"  Prospect ID: {prospect_id if prospect_id else 'NONE - NO LINK TO PROSPECT!'}")
    logger.info(f"  Email: {email if email else 'NONE'}")
    logger.info(f"  Phone: {phone if phone else 'NONE'}")
    logger.info(f"  Past Due: ${past_due:.2f}")
    logger.info("")

# Count how many have prospect IDs
members_with_prospect_ids = sum(1 for m in members_no_address if m[1])
members_without_prospect_ids = len(members_no_address) - members_with_prospect_ids

logger.info("=" * 80)
logger.info("SUMMARY")
logger.info("=" * 80)
logger.info(f"Past due members without addresses: {len(members_no_address)}")
logger.info(f"  - Have prospect_id link: {members_with_prospect_ids}")
logger.info(f"  - NO prospect_id link: {members_without_prospect_ids}")
logger.info("")

if members_with_prospect_ids > 0:
    logger.info("ISSUE: These members have prospect_id values but still no addresses.")
    logger.info("       This means the prospect records in ClubHub don't have address data.")
    logger.info("")

if members_without_prospect_ids > 0:
    logger.info("CRITICAL: These members have NO prospect_id link!")
    logger.info("          Cannot fetch addresses without a link to prospect records.")
    logger.info("")

conn.close()
