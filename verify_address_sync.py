"""Quick verification of address sync results"""
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check total members and members with addresses
cursor.execute("""
    SELECT COUNT(*) FROM members
""")
total_members = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) FROM members
    WHERE address IS NOT NULL AND address != '' AND address != 'NULL'
""")
members_with_addresses = cursor.fetchone()[0]

logger.info("=" * 80)
logger.info("ADDRESS SYNC VERIFICATION RESULTS")
logger.info("=" * 80)
logger.info(f"Total Members: {total_members}")
logger.info(f"Members with Addresses: {members_with_addresses} ({members_with_addresses / total_members * 100:.1f}%)")
logger.info("")

# Check past due members
cursor.execute("""
    SELECT
        first_name || ' ' || last_name as name,
        amount_past_due,
        address,
        city,
        state,
        zip_code
    FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
    ORDER BY amount_past_due DESC
    LIMIT 10
""")

past_due_members = cursor.fetchall()
past_due_with_address = sum(1 for m in past_due_members if m[2] and m[2].strip() and m[2] != 'NULL')

logger.info("PAST DUE MEMBERS (First 10):")
logger.info("-" * 80)
for name, past_due, address, city, state, zip_code in past_due_members:
    if address and address.strip() and address != 'NULL':
        full_address = f"{address}, {city or ''}, {state or ''} {zip_code or ''}".strip()
        logger.info(f"{name:30} | Past Due: ${past_due:8.2f} | Address: YES")
    else:
        logger.info(f"{name:30} | Past Due: ${past_due:8.2f} | Address: NO")

logger.info("")
logger.info(f"RESULT: {past_due_with_address}/10 past due members have addresses")

conn.close()
