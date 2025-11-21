"""
Comprehensive Fix Script
Syncs members and training clients with addresses from ClubHub/ClubOS
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.services.database_manager import DatabaseManager
from src.services.api.clubhub_api_client import ClubHubAPIClient
from src.services.authentication.secure_secrets_manager import SecureSecretsManager
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def sync_members_with_addresses():
    """Sync members with full address data from ClubHub"""
    try:
        logger.info("=" * 80)
        logger.info("STEP 1: Syncing Members with Addresses from ClubHub")
        logger.info("=" * 80)

        # Get credentials from config file
        from src.config.clubhub_credentials import get_clubhub_email, get_clubhub_password

        clubhub_email = get_clubhub_email()
        clubhub_password = get_clubhub_password()

        if not clubhub_email or not clubhub_password:
            logger.error("❌ ClubHub credentials not found!")
            return False

        logger.info(f"✅ Using ClubHub credentials: {clubhub_email[:10]}...")

        # Create ClubHub client
        clubhub = ClubHubAPIClient()
        if not clubhub.authenticate(clubhub_email, clubhub_password):
            logger.error("❌ ClubHub authentication failed!")
            return False

        logger.info("✅ ClubHub authentication successful")

        # Get ALL members with pagination
        logger.info("📥 Fetching all members from ClubHub...")
        members = clubhub.get_all_members_paginated()
        logger.info(f"✅ Fetched {len(members)} members from ClubHub")

        # Get ALL prospects for address data
        logger.info("📥 Fetching all prospects from ClubHub for address data...")
        prospects = clubhub.get_all_prospects_paginated()
        logger.info(f"✅ Fetched {len(prospects)} prospects from ClubHub")

        # Create address lookup by prospect ID
        address_lookup = {}
        for prospect in prospects:
            prospect_id = str(prospect.get('id') or prospect.get('prospectId'))
            if prospect_id:
                address_lookup[prospect_id] = {
                    'address': prospect.get('address') or prospect.get('address1') or prospect.get('streetAddress'),
                    'city': prospect.get('city'),
                    'state': prospect.get('state'),
                    'zip_code': prospect.get('zip') or prospect.get('zipCode') or prospect.get('postalCode'),
                    'phone': prospect.get('homePhone') or prospect.get('phone') or prospect.get('phoneNumber'),
                    'mobile_phone': prospect.get('mobilePhone') or prospect.get('mobile'),
                    'email': prospect.get('email')
                }

        logger.info(f"📊 Built address lookup from {len(address_lookup)} prospects")

        # Enhance members with address data
        enhanced_members = []
        members_with_addresses = 0

        for member in members:
            # Get prospect ID
            prospect_id = str(member.get('id') or member.get('prospectId'))

            # Add basic member info
            member['prospect_id'] = prospect_id
            member['full_name'] = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()

            # Try to get address from member data first
            member['address'] = member.get('address1') or member.get('address') or member.get('streetAddress')
            member['city'] = member.get('city')
            member['state'] = member.get('state')
            member['zip_code'] = member.get('zip') or member.get('zipCode') or member.get('postalCode')

            # Enhance with prospect data if available
            if prospect_id in address_lookup:
                prospect_data = address_lookup[prospect_id]
                if not member.get('address'):
                    member['address'] = prospect_data.get('address')
                if not member.get('city'):
                    member['city'] = prospect_data.get('city')
                if not member.get('state'):
                    member['state'] = prospect_data.get('state')
                if not member.get('zip_code'):
                    member['zip_code'] = prospect_data.get('zip_code')
                if not member.get('phone'):
                    member['phone'] = prospect_data.get('phone')
                if not member.get('mobile_phone'):
                    member['mobile_phone'] = prospect_data.get('mobile_phone')
                if not member.get('email'):
                    member['email'] = prospect_data.get('email')

            # Get agreement data for billing
            try:
                agreement_data = clubhub.get_member_agreement(prospect_id)
                if agreement_data and isinstance(agreement_data, dict):
                    member['amount_past_due'] = float(agreement_data.get('amountPastDue', 0))
                    member['status_message'] = agreement_data.get('statusMessage', '')
                    member['agreement_id'] = agreement_data.get('agreementId')

                    # Extract monthly dues
                    if 'monthlyDues' in agreement_data:
                        member['agreement_recurring_cost'] = float(agreement_data['monthlyDues']) or 0.0
                    elif 'recurringCost' in agreement_data:
                        if isinstance(agreement_data['recurringCost'], dict):
                            member['agreement_recurring_cost'] = float(agreement_data['recurringCost'].get('total', 0)) or 0.0
                        else:
                            member['agreement_recurring_cost'] = float(agreement_data['recurringCost']) or 0.0
            except Exception as e:
                logger.debug(f"Could not get agreement for {prospect_id}: {e}")

            # Track members with addresses
            if member.get('address'):
                members_with_addresses += 1

            enhanced_members.append(member)

        logger.info(f"✅ Enhanced {len(enhanced_members)} members ({members_with_addresses} with addresses)")

        # Save to database
        db = DatabaseManager()
        success = db.save_members_to_db(enhanced_members)

        if success:
            logger.info(f"✅ Saved {len(enhanced_members)} members to database with address data")
            return True
        else:
            logger.error("❌ Failed to save members to database")
            return False

    except Exception as e:
        logger.error(f"❌ Error syncing members with addresses: {e}")
        import traceback
        traceback.print_exc()
        return False

def sync_training_clients_with_addresses():
    """Sync training clients with address data from members table"""
    try:
        logger.info("=" * 80)
        logger.info("STEP 2: Syncing Training Clients with Addresses from Members")
        logger.info("=" * 80)

        # Import ClubOS integration
        from src.services.clubos_integration import ClubOSIntegration

        clubos = ClubOSIntegration()
        training_clients = clubos.get_training_clients()

        if not training_clients:
            logger.warning("⚠️ No training clients found from ClubOS")
            return False

        logger.info(f"✅ Fetched {len(training_clients)} training clients from ClubOS")

        # Get members from database for address lookup
        db = DatabaseManager()
        members_query = """
            SELECT prospect_id, address, city, state, zip_code, mobile_phone, email, phone
            FROM members
            WHERE prospect_id IS NOT NULL
        """
        members_rows = db.execute_query(members_query, fetch_all=True)

        # Create lookup dictionary
        members_lookup = {}
        for row in members_rows:
            member_dict = dict(row)
            prospect_id = str(member_dict.get('prospect_id', ''))
            if prospect_id:
                members_lookup[prospect_id] = member_dict

        logger.info(f"📊 Found {len(members_lookup)} members with IDs for matching")

        # Match training clients to members
        matched_count = 0
        for client in training_clients:
            # Try multiple ID fields
            member_id = client.get('clubos_member_id') or client.get('member_id') or client.get('prospect_id')
            if member_id:
                member_id = str(member_id)

                if member_id in members_lookup:
                    member_data = members_lookup[member_id]

                    # Copy address data
                    client['address'] = member_data.get('address')
                    client['city'] = member_data.get('city')
                    client['state'] = member_data.get('state')
                    client['zip_code'] = member_data.get('zip_code')
                    client['mobile_phone'] = client.get('mobile_phone') or member_data.get('mobile_phone') or member_data.get('phone')
                    client['email'] = client.get('email') or member_data.get('email')

                    # Set prospect_id
                    if not client.get('prospect_id'):
                        client['prospect_id'] = member_id

                    matched_count += 1

        logger.info(f"✅ Enhanced {matched_count}/{len(training_clients)} training clients with address data")

        # Save to database
        success = db.save_training_clients_to_db(training_clients)

        if success:
            logger.info(f"✅ Saved {len(training_clients)} training clients to database with address data")
            return True
        else:
            logger.error("❌ Failed to save training clients to database")
            return False

    except Exception as e:
        logger.error(f"❌ Error syncing training clients with addresses: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_addresses():
    """Verify that addresses were properly synced"""
    try:
        logger.info("=" * 80)
        logger.info("STEP 3: Verifying Address Data")
        logger.info("=" * 80)

        db = DatabaseManager()

        # Check past due members
        query = """
            SELECT prospect_id, full_name, amount_past_due, address, city, state, zip_code
            FROM members
            WHERE amount_past_due > 0
            LIMIT 10
        """
        past_due = db.execute_query(query, fetch_all=True)

        logger.info("\n📋 Past Due Members (First 10):")
        logger.info("-" * 80)
        members_with_addr = 0
        for row in past_due:
            member = dict(row)
            has_address = bool(member.get('address'))
            if has_address:
                members_with_addr += 1
            status = "✅ HAS ADDRESS" if has_address else "❌ NO ADDRESS"
            logger.info(f"{member.get('full_name', 'Unknown'):30s} | Past Due: ${member.get('amount_past_due', 0):8.2f} | {status}")
            if has_address:
                logger.info(f"    {member.get('address')}, {member.get('city')}, {member.get('state')} {member.get('zip_code')}")

        logger.info(f"\n📊 {members_with_addr}/{len(past_due)} past due members have addresses")

        # Check training clients
        query = """
            SELECT prospect_id, member_name, past_due_amount, address, city, state, zip_code
            FROM training_clients
            WHERE past_due_amount > 0
            LIMIT 10
        """
        training = db.execute_query(query, fetch_all=True)

        logger.info("\n📋 Past Due Training Clients (First 10):")
        logger.info("-" * 80)
        clients_with_addr = 0
        for row in training:
            client = dict(row)
            has_address = bool(client.get('address'))
            if has_address:
                clients_with_addr += 1
            status = "✅ HAS ADDRESS" if has_address else "❌ NO ADDRESS"
            logger.info(f"{client.get('member_name', 'Unknown'):30s} | Past Due: ${client.get('past_due_amount', 0):8.2f} | {status}")
            if has_address:
                logger.info(f"    {client.get('address')}, {client.get('city')}, {client.get('state')} {client.get('zip_code')}")

        logger.info(f"\n📊 {clients_with_addr}/{len(training)} past due training clients have addresses")

        return True

    except Exception as e:
        logger.error(f"❌ Error verifying addresses: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE ADDRESS SYNC & FIX SCRIPT")
    logger.info("=" * 80)

    # Step 1: Sync members with addresses
    step1_success = sync_members_with_addresses()

    # Step 2: Sync training clients with addresses
    step2_success = sync_training_clients_with_addresses()

    # Step 3: Verify addresses
    step3_success = verify_addresses()

    logger.info("=" * 80)
    logger.info("SYNC COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Step 1 (Members Sync): {'✅ SUCCESS' if step1_success else '❌ FAILED'}")
    logger.info(f"Step 2 (Training Clients Sync): {'✅ SUCCESS' if step2_success else '❌ FAILED'}")
    logger.info(f"Step 3 (Verification): {'✅ SUCCESS' if step3_success else '❌ FAILED'}")

    if step1_success and step2_success and step3_success:
        logger.info("\n🎉 All steps completed successfully!")
        logger.info("Addresses should now be populated for collections and referrals")
    else:
        logger.error("\n⚠️ Some steps failed. Check the logs above for details")
