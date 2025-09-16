#!/usr/bin/env python3
"""
Training Routes
Training client management, package details, and related functionality
"""

from flask import Blueprint, render_template, jsonify, current_app
import logging
import time
import traceback

# Import ClubOS Training API
try:
    from clubos_training_api_fixed import ClubOSTrainingPackageAPI
except ImportError:
    ClubOSTrainingPackageAPI = None

logger = logging.getLogger(__name__)

def get_member_clubos_guid(clubos_member_id):
    """Get the GUID from members table using clubos_member_id from training_clients table"""
    try:
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        # BREAKTHROUGH STRATEGY 1: Direct GUID lookup by clubos_member_id
        cursor.execute('SELECT guid FROM members WHERE id = ?', (clubos_member_id,))
        direct_result = cursor.fetchone()
        
        if direct_result:
            logger.info(f"✅ DIRECT MATCH: Found GUID {direct_result[0]} for clubos_member_id: {clubos_member_id}")
            conn.close()
            return direct_result[0]
        
        # BREAKTHROUGH STRATEGY 2: Name-based lookup (original method)
        cursor.execute('SELECT member_name FROM training_clients WHERE clubos_member_id = ?', (clubos_member_id,))
        result = cursor.fetchone()
        
        if result:
            member_name = result[0]
            # Now find the GUID in members table by name
            cursor.execute('SELECT guid FROM members WHERE full_name = ?', (member_name,))
            guid_result = cursor.fetchone()
            
            if guid_result:
                logger.info(f"✅ NAME MATCH: Found GUID {guid_result[0]} for member {member_name} (clubos_member_id: {clubos_member_id})")
                conn.close()
                return guid_result[0]
        
        # BREAKTHROUGH STRATEGY 3: Fuzzy name matching
        cursor.execute('SELECT member_name FROM training_clients WHERE clubos_member_id = ?', (clubos_member_id,))
        name_result = cursor.fetchone()
        
        if name_result:
            member_name = name_result[0]
            # Try partial name matches
            cursor.execute('SELECT guid, full_name FROM members WHERE full_name LIKE ?', (f'%{member_name}%',))
            fuzzy_results = cursor.fetchall()
            
            if fuzzy_results:
                logger.info(f"✅ FUZZY MATCH: Found {len(fuzzy_results)} potential matches for {member_name}")
                # Use the first match
                guid = fuzzy_results[0][0]
                matched_name = fuzzy_results[0][1]
                logger.info(f"✅ USING FUZZY MATCH: GUID {guid} for {matched_name} (original: {member_name})")
                conn.close()
                return guid
        
        conn.close()
        logger.warning(f"⚠️ Could not find GUID for clubos_member_id: {clubos_member_id}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error getting GUID for clubos_member_id {clubos_member_id}: {e}")
        return None

def get_training_client_financial_summary(member_id):
    """Get real financial summary data from ClubOS API with actual invoice analysis using WORKING process"""
    try:
        # Try to use the global ClubOS integration first
        api = None
        if hasattr(current_app, 'clubos') and current_app.clubos and hasattr(current_app.clubos, 'training_api'):
            api = current_app.clubos.training_api
        
        # If no global integration, try to create a fresh instance
        if not api and ClubOSTrainingPackageAPI:
            try:
                api = ClubOSTrainingPackageAPI()
                # Set credentials if available
                if hasattr(current_app, 'clubos') and current_app.clubos:
                    try:
                        from config.clubos_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
                        api.username = CLUBOS_USERNAME
                        api.password = CLUBOS_PASSWORD
                    except ImportError:
                        pass
            except Exception as e:
                logger.warning(f"⚠️ Could not create ClubOS Training API instance: {e}")
        
        if not api:
            logger.warning(f"⚠️ ClubOS Training API not available for member {member_id}")
            return {
                'total_past_due': 0.0,
                'active_agreements': 0,
                'total_sessions': 0,
                'total_value': 0.0,
                'total_paid': 0.0,
                'total_pending': 0.0,
                'payment_status': 'API Not Available'
            }
        
        # Authenticate if needed
        if not api.authenticated and not api.authenticate():
            logger.error(f"❌ ClubOS Training API authentication failed for member {member_id}")
            return {
                'total_past_due': 0.0,
                'active_agreements': 0,
                'total_sessions': 0,
                'total_value': 0.0,
                'total_paid': 0.0,
                'total_pending': 0.0,
                'payment_status': 'Authentication Failed'
            }
        
        # STEP 1: Delegate to member and get agreement IDs using WORKING process
        try:
            api.delegate_to_member(member_id)
            agreement_ids = api.discover_member_agreement_ids(member_id)
            logger.info(f"✅ Found {len(agreement_ids)} agreement IDs for member {member_id}: {agreement_ids}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to get agreement IDs for member {member_id}: {e}")
            return {
                'total_past_due': 0.0,
                'active_agreements': 0,
                'total_sessions': 0,
                'total_value': 0.0,
                'total_paid': 0.0,
                'total_pending': 0.0,
                'payment_status': 'No Data'
            }
        
        # Initialize financial totals
        total_past_due = 0.0
        total_paid = 0.0
        total_pending = 0.0
        total_value = 0.0
        total_sessions = 0
        active_agreements = []
        
        # STEP 2: Process each agreement using V2 endpoint
        for agreement_id in agreement_ids:
            try:
                # Direct V2 API call for invoice data (proven working method)
                url = f'https://anytime.club-os.com/api/agreements/package_agreements/V2/{agreement_id}'
                params = {
                    'include': 'invoices,scheduledPayments,prohibitChangeTypes'
                }
                
                response = api.session.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract agreement data
                    agreement_data = data.get('data', {})
                    agreement_status = agreement_data.get('agreementStatus')
                    agreement_name = agreement_data.get('name', f'Agreement {agreement_id}')
                    
                    # Only process active agreements (status 2 = active)
                    if agreement_status == 2:
                        active_agreements.append(agreement_id)
                        
                        # Extract invoice data from include section
                        include_data = data.get('include', {})
                        invoices = include_data.get('invoices', [])
                        
                        logger.info(f"✅ Active Agreement {agreement_id} ({agreement_name}): {len(invoices)} invoices")
                        
                        # Calculate invoice totals using WORKING logic
                        for invoice in invoices:
                            invoice_status = invoice.get('invoiceStatus')
                            remaining_total = float(invoice.get('remainingTotal', 0))
                            total_amount = float(invoice.get('total', 0))
                            
                            if invoice_status == 1:  # Paid
                                total_paid += (total_amount - remaining_total)
                            elif invoice_status == 2:  # Pending payment
                                total_pending += remaining_total
                            elif invoice_status == 5:  # Delinquent/Past due
                                total_past_due += remaining_total
                        
                        # Extract total agreement value
                        agreement_value = float(agreement_data.get('fullAgreementValue', 0))
                        if agreement_value > 0:
                            total_value += agreement_value
                        
                        # Extract session information
                        package_services = agreement_data.get('packageAgreementMemberServices', [])
                        for service in package_services:
                            units_per_billing = service.get('unitsPerBillingDuration', 0)
                            billing_duration = agreement_data.get('duration', 1)
                            if units_per_billing and billing_duration:
                                total_sessions += units_per_billing * billing_duration
                    else:
                        # Log non-active agreements
                        status_names = {1: "draft", 2: "active", 3: "pending downpayment", 4: "completed", 5: "canceled"}
                        status_name = status_names.get(agreement_status, f"unknown({agreement_status})")
                        logger.debug(f"⏭️ Skipping {status_name} agreement {agreement_id} ({agreement_name})")
                    
                else:
                    logger.warning(f"⚠️ Failed to get V2 data for agreement {agreement_id}: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error processing agreement {agreement_id}: {e}")
                continue
        
        # Create comprehensive financial summary
        financial_summary = {
            'active_agreements': len(active_agreements),
            'total_sessions': total_sessions,
            'total_value': total_value,
            'total_past_due': total_past_due,
            'total_paid': total_paid,
            'total_pending': total_pending,
            'payment_status': 'Past Due' if total_past_due > 0 else 'Pending' if total_pending > 0 else 'Current'
        }
        
        logger.info(f"✅ Financial summary for member {member_id}: {financial_summary['payment_status']}, ${total_past_due} past due, ${total_paid} paid, {len(active_agreements)} active agreements")
        return financial_summary
        
    except Exception as e:
        logger.error(f"❌ Error getting financial summary for member {member_id}: {e}")
        return {
            'total_past_due': 0.0,
            'active_agreements': 0,
            'total_sessions': 0,
            'total_value': 0.0,
            'total_paid': 0.0,
            'total_pending': 0.0,
            'payment_status': 'Error'
        }

def get_training_client_card_data(member_id):
    """Get simple card data for training client: name, packages, past due amounts using working invoice method"""
    try:
        if not ClubOSTrainingPackageAPI:
            logger.warning(f"⚠️ ClubOS Training API not available for member {member_id}")
            return {
                'name': 'Unknown',
                'packages': [],
                'total_past_due': 0.0,
                'status': 'Unknown'
            }
        
        # Use the global ClubOS integration's authenticated training API
        api = current_app.clubos.training_api
        
        if not api or not api.authenticated:
            logger.error(f"❌ ClubOS Training API not authenticated for member {member_id}")
            return {
                'name': 'Unknown',
                'packages': [],
                'total_past_due': 0.0,
                'status': 'Authentication Failed'
            }
        
        # STEP 1: Authenticate and delegate to member (working process)
        logger.info(f"🔄 Getting training data for member {member_id} using working API process...")
        
        try:
            api.delegate_to_member(member_id)
        except Exception as e:
            logger.error(f"❌ Failed to delegate to member {member_id}: {e}")
            return {
                'name': 'Unknown',
                'packages': [],
                'total_past_due': 0.0,
                'status': 'Delegation Failed'
            }
        
        # STEP 2: Get agreement IDs using simple list endpoint (proven working method)
        agreement_ids = []
        try:
            agreement_ids = api.discover_member_agreement_ids(member_id)
            logger.info(f"✅ Found {len(agreement_ids)} agreement IDs for member {member_id}: {agreement_ids}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to get agreement IDs for member {member_id}: {e}")
            return {
                'name': 'Unknown',
                'packages': [],
                'total_past_due': 0.0,
                'status': 'No Agreements Found'
            }
        
        # Get package names and calculate real past due from invoices
        packages = []
        total_past_due = 0.0
        
        # STEP 3: For each agreement ID, get V2 data with invoices
        if agreement_ids:
            for agreement_id in agreement_ids:
                try:
                    # Direct V2 API call for invoice data (proven working method)
                    url = f'https://anytime.club-os.com/api/agreements/package_agreements/V2/{agreement_id}'
                    params = {
                        'include': 'invoices,scheduledPayments,prohibitChangeTypes'
                    }
                    
                    response = api.session.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract agreement data
                        agreement_data = data.get('data', {})
                        agreement_status = agreement_data.get('agreementStatus')
                        agreement_name = agreement_data.get('name', f'Training Package {agreement_id}')
                        
                        # Only process active agreements (status 2 = active)
                        if agreement_status == 2:
                            packages.append(agreement_name)
                            
                            # Extract invoice data from include section
                            include_data = data.get('include', {})
                            invoices = include_data.get('invoices', [])
                            
                            # STEP 4: Calculate past due from invoices (status 2=pending, 5=delinquent)
                            for invoice in invoices:
                                invoice_status = invoice.get('invoiceStatus')
                                remaining_total = float(invoice.get('remainingTotal', 0))
                                
                                # Past due if status is pending (2) or delinquent (5)
                                if invoice_status in [2, 5] and remaining_total > 0:
                                    total_past_due += remaining_total
                            
                            logger.info(f"✅ Agreement {agreement_id}: {agreement_name}, ${total_past_due} past due from invoices")
                        
                    else:
                        logger.warning(f"⚠️ Failed to get V2 data for agreement {agreement_id}: {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error processing agreement {agreement_id}: {e}")
                    continue
        
        # If no packages found, use default
        if not packages:
            packages = ['Training Package']
        
        # Get member name from cache or database
        member_name = 'Unknown Client'
        if hasattr(current_app, 'data_cache') and current_app.data_cache.get('training_clients'):
            cached_clients = current_app.data_cache['training_clients']
            for client in cached_clients:
                if str(client.get('id')) == str(member_id) or str(client.get('member_id')) == str(member_id):
                    member_name = client.get('name', 'Unknown Client')
                    break
        
        card_data = {
            'name': member_name,
            'packages': packages,
            'total_past_due': total_past_due,
            'status': 'Past Due' if total_past_due > 0 else 'Current'
        }
        
        logger.info(f"✅ Card data for member {member_id}: {member_name}, {len(packages)} packages, ${total_past_due} past due")
        return card_data
        
    except Exception as e:
        logger.error(f"❌ Error getting card data for member {member_id}: {e}")
        return {
            'name': 'Error',
            'packages': [],
            'total_past_due': 0.0,
            'status': 'Error'
        }

training_bp = Blueprint('training', __name__)

@training_bp.route('/training-clients')
def training_clients_page():
    """Training clients page."""
    try:
        # Get training client count for display
        training_client_count = current_app.db_manager.get_training_client_count()
        
        return render_template('training_clients.html', training_client_count=training_client_count)
        
    except Exception as e:
        logger.error(f"❌ Error loading training clients page: {e}")
        return render_template('error.html', error=str(e))

@training_bp.route('/training-client/<member_id>')
def training_client_profile(member_id):
    """Training client profile page."""
    try:
        # First try to get training client from cached data
        if hasattr(current_app, 'data_cache') and current_app.data_cache.get('training_clients'):
            cached_clients = current_app.data_cache['training_clients']
            client_data = None
            
            # Search for training client in cache by ID
            for client in cached_clients:
                if (str(client.get('id')) == str(member_id) or 
                    str(client.get('member_id')) == str(member_id) or
                    str(client.get('clubos_member_id')) == str(member_id)):
                    client_data = client.copy()
                    break
            
            if client_data:
                # Enhance client data with member information from cache
                if hasattr(current_app, 'data_cache') and current_app.data_cache.get('members'):
                    cached_members = current_app.data_cache['members']
                    
                    # Find matching member by ID
                    for member in cached_members:
                        if (str(member.get('id')) == str(member_id) or
                            str(member.get('guid')) == str(member_id) or
                            str(member.get('prospect_id')) == str(member_id) or
                            str(member.get('prospectId')) == str(member_id)):
                            
                            # Merge member data into client data
                            client_data['member_name'] = member.get('full_name') or f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
                            client_data['email'] = member.get('email')
                            client_data['mobile_phone'] = member.get('mobile_phone') or member.get('mobilePhone')
                            client_data['status_message'] = member.get('status_message') or member.get('statusMessage')
                            client_data['first_name'] = member.get('firstName')
                            client_data['last_name'] = member.get('lastName')
                            break
                
                # Ensure we have a name even if not found in members
                if not client_data.get('member_name'):
                    client_data['member_name'] = client_data.get('name') or 'Unknown Client'
                
                # Create financial summary from real ClubOS data
                financial_summary = get_training_client_financial_summary(member_id)
                
                logger.info(f"✅ Found training client {member_id} in cache")
                return render_template('training_client_profile.html', 
                                     client=client_data, 
                                     training_client=client_data,
                                     financial_summary=financial_summary)
        
        # Fallback: try database - FIXED to search by clubos_member_id
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tc.*, m.first_name, m.last_name, m.full_name, m.email, m.mobile_phone, m.status_message
            FROM training_clients tc
            LEFT JOIN members m ON (tc.member_id = m.guid OR tc.member_id = m.prospect_id)
            WHERE tc.clubos_member_id = ? OR tc.member_id = ? OR tc.id = ?
        """, (member_id, member_id, member_id))
        
        client_record = cursor.fetchone()
        if client_record:
            client_data = dict(client_record)
            client_data['member_name'] = (client_data.get('full_name') or 
                                        f"{client_data.get('first_name', '')} {client_data.get('last_name', '')}".strip() or 
                                        'Unknown Client')
            conn.close()
            
            # Create financial summary from real ClubOS data
            financial_summary = get_training_client_financial_summary(member_id)
            
            logger.info(f"✅ Found training client {member_id} in database")
            return render_template('training_client_profile.html', 
                                 client=client_data, 
                                 training_client=client_data,
                                 financial_summary=financial_summary)
        
        conn.close()
        
        # If not found in cache or database, show error
        logger.warning(f"⚠️ Training client {member_id} not found in cache or database")
        return render_template('error.html', error=f'Training client {member_id} not found')
        
    except Exception as e:
        logger.error(f"❌ Error loading training client profile {member_id}: {e}")
        return render_template('error.html', error=str(e))

def get_active_packages_and_past_due(member_id):
    """
    Get active package names and REAL past due amount for a training client.
    
    This implements the WORKING process discovered through YOUR insights:
    1. Authenticate to ClubOS Training API
    2. Delegate to the member
    3. Call /api/agreements/package_agreements/list (simple, no parameters)
    4. For each agreement, call /api/agreements/package_agreements/V2/{id}?include=invoices
    5. Calculate real past due amounts from invoice data
    
    Args:
        member_id (str): The clubos_member_id from training_clients table
        
    Returns:
        tuple: (list of package names, total past due amount)
    """
    try:
        logger.info(f"🔍 Getting training packages for member {member_id} using WORKING API process")
        
        # Initialize the ClubOS Training API
        try:
            from src.clubos_training_api import ClubOSTrainingPackageAPI
            api = ClubOSTrainingPackageAPI()
        except ImportError as e:
            logger.error(f"❌ Could not import ClubOS Training API: {e}")
            return [], 0.0
        
        # Step 1: Get agreement IDs using the WORKING simple list endpoint
        agreement_ids = api.discover_member_agreement_ids(member_id)
        
        if not agreement_ids:
            logger.info(f"ℹ️ No training agreements found for member {member_id}")
            return [], 0.0
        
        logger.info(f"✅ Found {len(agreement_ids)} agreement IDs: {agreement_ids}")
        
        # Step 2: Get detailed data for each agreement using V2 endpoint
        all_packages = []
        total_past_due = 0.0
        
        for agreement_id in agreement_ids:
            try:
                # Use the WORKING V2 endpoint with includes
                v2_url = f"https://anytime.club-os.com/api/agreements/package_agreements/V2/{agreement_id}?include=invoices&include=scheduledPayments&include=prohibitChangeTypes"
                v2_response = api.session.get(v2_url, timeout=15)
                
                if v2_response.status_code != 200:
                    logger.warning(f"⚠️ V2 endpoint failed for agreement {agreement_id}: {v2_response.status_code}")
                    continue
                
                v2_data = v2_response.json()
                
                # Extract package name from the main data
                package_name = "Unknown Package"
                if 'data' in v2_data and isinstance(v2_data['data'], dict):
                    package_name = v2_data['data'].get('name', package_name)
                
                all_packages.append(package_name)
                logger.info(f"📦 Found package: {package_name}")
                
                # Calculate past due from invoices (YOUR discovery of the data structure)
                if 'include' in v2_data and 'invoices' in v2_data['include']:
                    invoices = v2_data['include']['invoices']
                    logger.info(f"📋 Found {len(invoices)} invoices for {package_name}")
                    
                    for invoice in invoices:
                        if isinstance(invoice, dict):
                            # Check invoice status - past due invoices have specific statuses
                            invoice_status = invoice.get('invoiceStatus', 0)
                            remaining_total = float(invoice.get('remainingTotal', 0))
                            
                            # Invoice statuses from your API data: 1=paid, 2=pending, 5=delinquent
                            if invoice_status in [2, 5] and remaining_total > 0:  # Pending or delinquent
                                total_past_due += remaining_total
                                logger.info(f"💰 Added ${remaining_total} past due from invoice status {invoice_status}")
                
            except Exception as e:
                logger.warning(f"⚠️ Error processing agreement {agreement_id}: {e}")
                continue
        
        logger.info(f"✅ Final results for member {member_id}: {len(all_packages)} packages, ${total_past_due:.2f} past due")
        return all_packages, total_past_due
        
    except Exception as e:
        logger.error(f"❌ Error getting active packages and past due for {member_id}: {e}")
        return [], 0.0

        # BREAKTHROUGH PROCESS: Delegate to member before making API calls - this is CRITICAL
        # Clear any existing delegation cookies to prevent duplicates
        cookies_to_remove = []
        for cookie in api.session.cookies:
            if cookie.name in ['delegatedUserId', 'staffDelegatedUserId']:
                cookies_to_remove.append((cookie.name, cookie.domain, cookie.path))
        
        for name, domain, path in cookies_to_remove:
            api.session.cookies.clear(domain, path, name)
        
        if not api.delegate_to_member(clubos_guid):
            logger.error(f"❌ CRITICAL: Failed to delegate to member GUID: {clubos_guid}")
            return [], 0.0

        logger.info(f"✅ Successfully delegated to member GUID: {clubos_guid}")
        # Safe cookie logging to avoid CookieConflictError
        delegation_cookies = []
        for cookie in api.session.cookies:
            if cookie.name == 'delegatedUserId':
                delegation_cookies.append(cookie.value)
        logger.info(f"✅ Delegation cookies: {delegation_cookies}")
        
        # TEST: Maybe the working method was using clubos_member_id instead of GUID
        # Let's try both approaches to see which one was actually working
        logger.info(f"� TESTING: Trying both clubos_member_id ({member_id}) and GUID ({clubos_guid}) approaches")
        
        # Use the GUID approach as determined from conversation history
        logger.info(f"📋 STEP 1: Using BREAKTHROUGH METHOD - discover_member_agreement_ids with GUID: {clubos_guid}")
        agreement_ids = api.discover_member_agreement_ids(clubos_guid)
        
        logger.info(f"📋 STEP 1 SUCCESS: Found {len(agreement_ids)} agreement IDs: {agreement_ids}")
        
        if not agreement_ids:
            logger.warning(f"⚠️ No agreement IDs found for GUID: {clubos_guid}")
            return [], 0.0
        
        # Extract agreement IDs from the agreements response (this is different from payment_details)
        agreement_ids = [str(agreement.get('agreement_id')) for agreement in agreements if agreement.get('agreement_id')]
        
        logger.info(f"� Extracted {len(agreement_ids)} agreement IDs: {agreement_ids}")
        
        if not agreement_ids:
            logger.warning(f"⚠️ No agreement IDs found in agreements for working ID: {working_id}")
            return [], 0.0
        
        # STEP 2: Get detailed package information for each agreement
        package_names = []
        total_past_due = 0.0
        
        # Ensure delegation is maintained for V2 API calls using the GUID
        if not api.delegate_to_member(clubos_guid):
            logger.warning(f"⚠️ Failed to re-delegate to GUID: {clubos_guid} for V2 calls")
        
        import time
        timestamp = int(time.time() * 1000)
        api_headers = api._auth_headers(referer=f'{api.base_url}/action/PackageAgreementUpdated/spa/')
        api_headers.update({
            'X-Requested-With': 'XMLHttpRequest',
        })
        
        for i, agreement_id in enumerate(agreement_ids, 1):
            logger.info(f"📦 BREAKTHROUGH STEP 2.{i}: Processing agreement ID: {agreement_id}")
            
            # This is the V2 endpoint that successfully returned Mark's package data
            detail_url = f"{api.base_url}/api/agreements/package_agreements/V2/{agreement_id}"
            detail_params = {
                'include': 'invoices,scheduledPayments,prohibitChangeTypes',
                '_': timestamp
            }
            
            # Use authenticated headers for V2 API call
            detail_response = api.session.get(detail_url, headers=api_headers, params=detail_params, timeout=15)
            
            if detail_response.status_code != 200:
                logger.warning(f"⚠️ Failed to get details for agreement {agreement_id}: {detail_response.status_code}")
                continue
                
            response_json = detail_response.json()
            detail_data = response_json.get('data', {})
            agreement_name = detail_data.get('name', f'Training Package {agreement_id}')
            agreement_status = detail_data.get('agreementStatus', 0)
            
            logger.info(f"📊 BREAKTHROUGH STEP 2.{i} SUCCESS: Agreement {agreement_id} '{agreement_name}' (status: {agreement_status})")
            
            # Only process active agreements (status 2 = active)
            if agreement_status == 2:
                package_names.append(agreement_name)
                
                # Calculate past due amount from invoices (Status 5 = Delinquent/Past due)
                past_due_amount = 0.0
                include_data = response_json.get('include', {})
                invoices = include_data.get('invoices', [])
                
                for invoice in invoices:
                    invoice_status = invoice.get('invoiceStatus')
                    if invoice_status == 5:  # Past due status
                        amount = float(invoice.get('total', 0))
                        past_due_amount += amount
                        logger.info(f"💰 Found past due invoice: ${amount}")
                
                total_past_due += past_due_amount
                logger.info(f"✅ BREAKTHROUGH STEP 2.{i} COMPLETE: Added ACTIVE package '{agreement_name}' with ${past_due_amount} past due")
            else:
                status_names = {1: "draft", 2: "active", 3: "pending downpayment", 4: "completed", 5: "canceled"}
                status_name = status_names.get(agreement_status, f"unknown({agreement_status})")
                logger.info(f"ℹ️ BREAKTHROUGH STEP 2.{i} COMPLETE: Skipped {status_name} package '{agreement_name}'")

        logger.info(f"🎯 BREAKTHROUGH SUCCESS: Member {member_id} (GUID: {clubos_guid}) has {len(package_names)} ACTIVE packages, ${total_past_due} total past due")
        return package_names, total_past_due

    except Exception as e:
        logger.error(f"❌ Error getting packages for member {member_id}: {str(e)}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        return [], 0.0

@training_bp.route('/api/training-clients/all')
def get_all_training_clients():
    """Get all training clients - FAST display mode with cached data first"""
    try:
        logger.info("🚀 Starting FAST training clients endpoint...")
        
        # STRATEGY 1: Try database first since it has the real names from startup
        logger.info("📊 Trying database first for real names...")
        try:
            # Use direct database connection instead of current_app.db_manager
            import sqlite3
            import os
            
            # Get database path - use absolute path to ensure we find the right DB
            db_path = r'c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\gym_bot.db'
            
            logger.info(f"🔍 Attempting to connect to database at: {db_path}")
            
            if not os.path.exists(db_path):
                logger.error(f"❌ Database file does not exist at: {db_path}")
                raise FileNotFoundError("Database not found")
                
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            logger.info("🔍 Database connection successful, executing query...")
            
            # Get training clients from database - they already have real names from sync
            cursor.execute("""
                SELECT * FROM training_clients 
                ORDER BY member_name, created_at DESC
            """)
            
            rows = cursor.fetchall()
            logger.info(f"🔍 Query returned {len(rows)} rows")
            
            rows = cursor.fetchall()
            logger.info(f"🔍 Query returned {len(rows)} rows")
            conn.close()
            
            if rows:
                logger.info(f"📊 Found {len(rows)} training clients in database")
                training_clients = []
                for row in rows:  # Process ALL rows, not just first 3
                    # Convert sqlite Row to dict properly
                    c = {key: row[key] for key in row.keys()}
                    
                    logger.info(f"🔍 Processing row: member_name='{c.get('member_name')}', clubos_id={c.get('clubos_member_id')}")
                    
                    # Use the member_name from database (set during sync) or fallback
                    display_name = (c.get('member_name') or
                                  f"Training Client #{str(c.get('clubos_member_id', 'Unknown'))[-4:]}")
                    
                    c['member_name'] = display_name
                    
                    # Set email and phone from training client record
                    c['email'] = c.get('email')
                    c['phone'] = c.get('phone')
                    c['status_message'] = c.get('status')
                    
                    # Ensure required fields for frontend
                    c['member_id'] = c.get('clubos_member_id') or c.get('member_id')
                    c['prospect_id'] = c.get('clubos_member_id') or c.get('member_id')
                    c['trainer_name'] = c.get('trainer_name') or 'Jeremy Mayo'
                    c['sessions_remaining'] = c.get('sessions_remaining') or 0
                    c['last_session'] = c.get('last_session') or 'Never'
                    c['payment_status'] = c.get('payment_status') or 'Current'
                    c['active_packages'] = c.get('active_packages') or ['Training Package']
                    c['past_due_amount'] = c.get('past_due_amount') or 0.0
                    
                    training_clients.append(c)
                
                logger.info(f"✅ Retrieved {len(training_clients)} training clients from database with real names")
                return jsonify({'success': True, 'training_clients': training_clients, 'source': 'database'})
        
        except Exception as db_error:
            logger.error(f"❌ Database query failed: {db_error}")
        
        # STRATEGY 2: Try cache as fallback
        logger.info("🔄 Checking cache as fallback...")
        if hasattr(current_app, 'data_cache') and current_app.data_cache.get('training_clients'):
            cached_training_clients = current_app.data_cache['training_clients']
            logger.info(f"� Found {len(cached_training_clients)} training clients in cache")
            
            # Get the real names from database to fix the cache
            name_lookup = {}
            try:
                import sqlite3
                db_path = r'c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\gym_bot.db'
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT clubos_member_id, member_name, active_packages, past_due_amount FROM training_clients")
                for row in cursor.fetchall():
                    clubos_id = str(row[0]) if row[0] else None
                    if clubos_id:
                        name_lookup[clubos_id] = {
                            'name': row[1] or f"Training Client #{clubos_id[-4:]}",
                            'packages': row[2] or 'Training Package',
                            'past_due': row[3] or 0.0
                        }
                conn.close()
                logger.info(f"✅ Built name lookup with {len(name_lookup)} entries")
            except Exception as e:
                logger.error(f"❌ Failed to build name lookup: {e}")
            
            # Enhance training client data with member information
            enhanced_clients = []
            cached_members = current_app.data_cache.get('members', []) if hasattr(current_app, 'data_cache') else []
            
            for client in cached_training_clients:
                enhanced_client = client.copy()
                
                # Get all possible IDs for matching
                client_id = str(client.get('id') or client.get('member_id') or client.get('clubos_member_id') or '')
                
                # IMPROVED: Use the name that ClubOS integration already retrieved during sync
                # Priority: Use cached member_name from sync > construct from first/last > match with members > fallback
                if client.get('member_name') and not client['member_name'].startswith('Training Client #'):
                    # We already have a real name from the ClubOS sync process
                    enhanced_client['member_name'] = client['member_name']
                    logger.info(f"🎯 Using synced name: {client['member_name']} for ID {client_id}")
                elif client.get('full_name'):
                    # Use full_name if available
                    enhanced_client['member_name'] = client['full_name']
                    logger.info(f"🎯 Using full name: {client['full_name']} for ID {client_id}")
                elif client.get('first_name') or client.get('last_name'):
                    # Construct from first/last names
                    full_name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
                    enhanced_client['member_name'] = full_name if full_name else f"Training Client #{client_id[-4:]}"
                    logger.info(f"🎯 Using constructed name: {full_name} for ID {client_id}")
                else:
                    # Try to find member info by ID matching as fallback
                    member_found = False
                    if cached_members and client_id:
                        for member in cached_members:
                            # Match by various ID fields - try all possible combinations
                            member_ids = [
                                str(member.get('guid', '')),
                                str(member.get('prospect_id', '')), 
                                str(member.get('prospectId', '')),
                                str(member.get('id', '')),
                                str(member.get('member_id', ''))
                            ]
                            
                            if client_id in member_ids:
                                enhanced_client.update({
                                    'member_name': member.get('full_name') or f"{member.get('firstName', '')} {member.get('lastName', '')}".strip() or 'Unknown Client',
                                    'email': member.get('email'),
                                    'phone': member.get('mobile_phone') or member.get('mobilePhone'),
                                    'status_message': member.get('status_message') or member.get('statusMessage')
                                })
                                member_found = True
                                logger.info(f"🎯 Matched member: {enhanced_client['member_name']} for ID {client_id}")
                                break
                        
                        # Try name matching as fallback if we have a client name but no ID match
                        if not member_found and client_name:
                            for member in cached_members:
                                member_full_name = member.get('full_name') or f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
                                if member_full_name and client_name.lower() == member_full_name.lower():
                                    enhanced_client.update({
                                        'member_name': member_full_name,
                                        'email': member.get('email'),
                                        'phone': member.get('mobile_phone') or member.get('mobilePhone'),
                                        'status_message': member.get('status_message') or member.get('statusMessage')
                                    })
                                    member_found = True
                                    logger.info(f"🎯 Name matched: {member_full_name} for client {client_name}")
                                    break
                    
                    # Final fallback for member_name
                    if not enhanced_client.get('member_name'):
                        enhanced_client['member_name'] = f"Training Client #{str(client_id or 'Unknown')[-4:]}"
                enhanced_client['trainer_name'] = enhanced_client.get('trainer_name') or enhanced_client.get('trainer') or 'Jeremy Mayo'
                enhanced_client['sessions_remaining'] = enhanced_client.get('sessions_remaining') or 0
                enhanced_client['last_session'] = enhanced_client.get('last_session') or 'Never'
                enhanced_client['payment_status'] = enhanced_client.get('payment_status') or 'Current'
                enhanced_client['active_packages'] = enhanced_client.get('active_packages') or ['Training Package']
                enhanced_client['past_due_amount'] = enhanced_client.get('past_due_amount') or 0.0
                
                # Set member_id for frontend routing
                enhanced_client['member_id'] = client_id or enhanced_client.get('clubos_member_id')
                enhanced_client['prospect_id'] = client_id or enhanced_client.get('clubos_member_id')
                
                enhanced_clients.append(enhanced_client)
            
            logger.info(f"✅ Returning {len(enhanced_clients)} enhanced training clients from cache")
            return jsonify({'success': True, 'training_clients': enhanced_clients, 'source': 'cache'})
        
        # STRATEGY 2: Try database if no cache
        logger.info("� Cache not available, trying database...")
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get training clients with member info joined
        cursor.execute("""
            SELECT 
                tc.*,
                m.first_name as member_first_name,
                m.last_name as member_last_name,
                m.full_name as member_full_name,
                m.email as member_email,
                m.mobile_phone as member_phone,
                m.status_message as member_status_message
            FROM training_clients tc 
            LEFT JOIN members m ON (tc.member_id = m.guid OR tc.member_id = m.prospect_id)
            ORDER BY tc.member_name, tc.created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        training_clients = []
        for row in rows:
            c = dict(row)
            
            # Use member info if available, otherwise fall back to training client info
            c['member_name'] = (c.get('member_full_name') or 
                              f"{c.get('member_first_name', '')} {c.get('member_last_name', '')}".strip() or
                              c.get('member_name') or
                              f"Training Client #{str(c.get('clubos_member_id', 'Unknown'))[-4:]}")
            
            c['email'] = c.get('member_email') or c.get('email')
            c['phone'] = c.get('member_phone') or c.get('phone')
            c['status_message'] = c.get('member_status_message') or c.get('status')
            
            # Ensure required fields for frontend
            c['member_id'] = c.get('clubos_member_id') or c.get('member_id')
            c['prospect_id'] = c.get('clubos_member_id') or c.get('member_id')
            c['trainer_name'] = c.get('trainer_name') or 'Jeremy Mayo'
            c['sessions_remaining'] = c.get('sessions_remaining') or 0
            c['last_session'] = c.get('last_session') or 'Never'
            c['payment_status'] = c.get('payment_status') or 'Current'
            c['active_packages'] = c.get('active_packages') or ['Training Package']
            c['past_due_amount'] = c.get('past_due_amount') or 0.0
            
            training_clients.append(c)
        
        logger.info(f"✅ Retrieved {len(training_clients)} training clients from database")
        return jsonify({'success': True, 'training_clients': training_clients, 'source': 'database'})
        
    except Exception as e:
        logger.error(f"❌ Error getting all training clients: {e}")
        
        # FALLBACK: Return basic structure so frontend doesn't break
        return jsonify({
            'success': True, 
            'training_clients': [], 
            'source': 'error_fallback',
            'error': str(e)
        })

@training_bp.route('/api/debug/training-api')
def debug_training_api():
    """Debug the training API status"""
    try:
        debug_info = {
            'has_clubos': hasattr(current_app, 'clubos'),
            'clubos_exists': current_app.clubos is not None if hasattr(current_app, 'clubos') else False,
            'has_training_api': hasattr(current_app.clubos, 'training_api') if hasattr(current_app, 'clubos') and current_app.clubos else False,
            'training_api_exists': current_app.clubos.training_api is not None if hasattr(current_app, 'clubos') and current_app.clubos and hasattr(current_app.clubos, 'training_api') else False,
            'training_api_authenticated': current_app.clubos.training_api.authenticated if hasattr(current_app, 'clubos') and current_app.clubos and hasattr(current_app.clubos, 'training_api') and current_app.clubos.training_api else False,
            'has_credentials': hasattr(current_app.clubos.training_api, 'username') and hasattr(current_app.clubos.training_api, 'password') and current_app.clubos.training_api.username and current_app.clubos.training_api.password if hasattr(current_app, 'clubos') and current_app.clubos and hasattr(current_app.clubos, 'training_api') and current_app.clubos.training_api else False
        }
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e)})

@training_bp.route('/api/debug/test-auth/<member_id>')
def debug_test_auth(member_id):
    """DEBUG ENDPOINT: Test ClubOS authentication and API calls step by step."""
    try:
        logger.info(f"🔍 DEBUG: Testing authentication for member {member_id}")
        
        # Step 1: Get GUID
        clubos_guid = get_member_clubos_guid(str(member_id))
        if not clubos_guid:
            return {"error": "Could not find GUID", "member_id": member_id}
        
        logger.info(f"🔍 DEBUG: Found GUID {clubos_guid} for member {member_id}")
        
        # Step 2: Create fresh API
        try:
            from clubos_training_api_fixed import ClubOSTrainingPackageAPI
            from config.clubos_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
            
            api = ClubOSTrainingPackageAPI()
            api.username = CLUBOS_USERNAME
            api.password = CLUBOS_PASSWORD
            
            logger.info(f"🔍 DEBUG: Created API instance with username: {CLUBOS_USERNAME[:3]}***")
            
        except Exception as e:
            logger.error(f"❌ DEBUG: Failed to create API: {e}")
            return {"error": f"Failed to create API: {str(e)}"}
        
        # Step 3: Test Authentication
        try:
            auth_result = api.authenticate()
            logger.info(f"🔍 DEBUG: Authentication result: {auth_result}")
            logger.info(f"🔍 DEBUG: Session cookies: {list(api.session.cookies.keys())}")
            
            if not auth_result:
                return {"error": "Authentication failed", "auth_result": auth_result}
                
        except Exception as e:
            logger.error(f"❌ DEBUG: Authentication exception: {e}")
            return {"error": f"Authentication exception: {str(e)}"}
        
        # Step 4: Test Delegation
        try:
            # Clear any existing delegation cookies to prevent duplicates
            cookies_to_remove = []
            for cookie in api.session.cookies:
                if cookie.name in ['delegatedUserId', 'staffDelegatedUserId']:
                    cookies_to_remove.append((cookie.name, cookie.domain, cookie.path))
            
            for name, domain, path in cookies_to_remove:
                api.session.cookies.clear(domain, path, name)
            
            delegate_result = api.delegate_to_member(clubos_guid)
            logger.info(f"🔍 DEBUG: Delegation result: {delegate_result}")
            # Safe cookie logging to avoid CookieConflictError
            delegation_cookies = []
            for cookie in api.session.cookies:
                if cookie.name == 'delegatedUserId':
                    delegation_cookies.append(cookie.value)
            logger.info(f"🔍 DEBUG: Delegation cookies: {delegation_cookies}")
            
            if not delegate_result:
                return {"error": "Delegation failed", "delegate_result": delegate_result}
                
        except Exception as e:
            logger.error(f"❌ DEBUG: Delegation exception: {e}")
            return {"error": f"Delegation exception: {str(e)}"}
        
        # Step 5: Test API Call
        try:
            import time
            timestamp = int(time.time() * 1000)
            api_headers = api._auth_headers(referer=f'{api.base_url}/action/PackageAgreementUpdated/spa/')
            api_headers.update({
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            })

            list_url = f"{api.base_url}/api/agreements/package_agreements/list"
            params = {
                'memberId': clubos_guid,
                '_': timestamp
            }
            
            logger.info(f"🔍 DEBUG: Making API call to: {list_url}")
            logger.info(f"🔍 DEBUG: Headers: {api_headers}")
            logger.info(f"🔍 DEBUG: Params: {params}")
            
            response = api.session.get(list_url, headers=api_headers, params=params, timeout=15)
            
            logger.info(f"🔍 DEBUG: Response status: {response.status_code}")
            logger.info(f"🔍 DEBUG: Response headers: {dict(response.headers)}")
            logger.info(f"🔍 DEBUG: Response body: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"🔍 DEBUG: Parsed JSON: {data}")
                    return {
                        "success": True,
                        "member_id": member_id,
                        "guid": clubos_guid,
                        "auth_result": auth_result,
                        "delegate_result": delegate_result,
                        "api_response": data,
                        "response_status": response.status_code
                    }
                except Exception as json_err:
                    logger.error(f"❌ DEBUG: JSON parsing error: {json_err}")
                    return {
                        "error": "JSON parsing failed",
                        "response_text": response.text,
                        "response_status": response.status_code
                    }
            else:
                return {
                    "error": "API call failed",
                    "response_status": response.status_code,
                    "response_text": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ DEBUG: API call exception: {e}")
            return {"error": f"API call exception: {str(e)}"}
        
    except Exception as e:
        logger.error(f"❌ DEBUG: Overall exception: {e}")
        return {"error": f"Overall exception: {str(e)}"}

@training_bp.route('/api/training-clients/<member_id>/packages')
def get_member_packages(member_id):
    """Get active packages and past due amount for a specific training client."""
    try:
        if not member_id:
            return jsonify({'success': False, 'error': 'Member ID required'}), 400
            
        # Get active packages and real past due amount
        active_packages, past_due_amount = get_active_packages_and_past_due(str(member_id))
        
        payment_status = 'Past Due' if past_due_amount > 0 else 'Current'
        
        # Get the GUID used for debugging
        clubos_guid = get_member_clubos_guid(str(member_id))
        
        return jsonify({
            'success': True,
            'member_id': member_id,
            'active_packages': active_packages,
            'past_due_amount': past_due_amount,
            'payment_status': payment_status,
            'debug_packages_count': len(active_packages),
            'debug_past_due': past_due_amount,
            'debug_guid': clubos_guid
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting packages for member {member_id}: {e}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'member_id': member_id,
            'active_packages': [],
            'past_due_amount': 0.0,
            'payment_status': 'Error'
        }), 500

@training_bp.route('/api/training-clients/<member_id>/agreements')
def get_member_package_agreements(member_id):
    """Get training package agreements for a specific member."""
    try:
        # Get agreements from ClubOS
        agreements = current_app.clubos.get_member_agreements(member_id)
        
        if agreements:
            logger.info(f"✅ Retrieved {len(agreements)} agreements for member {member_id}")
            return jsonify({'success': True, 'agreements': agreements})
        else:
            logger.info(f"ℹ️ No agreements found for member {member_id}")
            return jsonify({'success': True, 'agreements': []})
            
    except Exception as e:
        logger.error(f"❌ Error getting agreements for member {member_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/api/debug/test-member-agreements/<member_id>')
def debug_test_member_agreements(member_id):
    """DEBUG ENDPOINT: Test alternative member agreements endpoint."""
    try:
        logger.info(f"🔍 DEBUG: Testing member agreements endpoint for member {member_id}")
        
        # Get GUID
        clubos_guid = get_member_clubos_guid(str(member_id))
        if not clubos_guid:
            return jsonify({"error": "Could not find GUID", "member_id": member_id})
        
        # Create fresh API
        try:
            from clubos_training_api_fixed import ClubOSTrainingPackageAPI
            from config.clubos_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
            
            api = ClubOSTrainingPackageAPI()
            api.username = CLUBOS_USERNAME
            api.password = CLUBOS_PASSWORD
            
            if not api.authenticate():
                return jsonify({"error": "Authentication failed"})
                
        except Exception as e:
            return jsonify({"error": f"Failed to create API: {str(e)}"})
        
        # Test alternative endpoint: /api/members/{mid}/agreements/package
        try:
            api.delegate_to_member(clubos_guid)
            
            member_agreements_url = f"{api.base_url}/api/members/{clubos_guid}/agreements/package"
            headers = {
                'User-Agent': api.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'application/json, text/plain, */*',
                'Referer': f'{api.base_url}/action/Dashboard/',
            }
            
            response = api.session.get(member_agreements_url, headers=headers, timeout=30)
            
            return jsonify({
                "endpoint": "member_agreements",
                "url": member_agreements_url,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "guid": clubos_guid
            })
            
        except Exception as e:
            return jsonify({"error": f"Member agreements API failed: {str(e)}"})
            
    except Exception as e:
        return jsonify({"error": str(e)})

@training_bp.route('/api/debug/test-training-clients')
def debug_test_training_clients():
    """DEBUG ENDPOINT: Test training clients endpoint."""
    try:
        logger.info("🔍 DEBUG: Testing training clients endpoint")
        
        # Create fresh API
        try:
            from clubos_training_api_fixed import ClubOSTrainingPackageAPI
            from config.clubos_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
            
            api = ClubOSTrainingPackageAPI()
            api.username = CLUBOS_USERNAME
            api.password = CLUBOS_PASSWORD
            
            if not api.authenticate():
                return jsonify({"error": "Authentication failed"})
                
        except Exception as e:
            return jsonify({"error": f"Failed to create API: {str(e)}"})
        
        # Test training clients endpoint
        try:
            training_clients_url = f"{api.base_url}/api/training/clients"
            headers = {
                'User-Agent': api.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'application/json, text/plain, */*',
                'Referer': f'{api.base_url}/action/Dashboard/',
            }
            
            response = api.session.get(training_clients_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                clients_data = response.json()
                return jsonify({
                    "endpoint": "training_clients",
                    "url": training_clients_url,
                    "status_code": response.status_code,
                    "clients_count": len(clients_data) if isinstance(clients_data, list) else "not_list",
                    "clients": clients_data[:3] if isinstance(clients_data, list) else clients_data  # First 3 clients only
                })
            else:
                return jsonify({
                    "endpoint": "training_clients",
                    "url": training_clients_url,
                    "status_code": response.status_code,
                    "response": response.text
                })
            
        except Exception as e:
            return jsonify({"error": f"Training clients API failed: {str(e)}"})
            
    except Exception as e:
        return jsonify({"error": str(e)})

@training_bp.route('/api/migrate-database')
def migrate_database():
    """Manual endpoint to migrate the database schema"""
    try:
        logger.info("🔄 Manual database migration: Starting...")
        
        if not hasattr(current_app, 'db_manager'):
            return jsonify({'success': False, 'error': 'Database manager not available'})
        
        # Trigger database initialization which will run the migration
        current_app.db_manager.init_database()
        
        logger.info("✅ Manual database migration completed")
        
        return jsonify({
            'success': True,
            'message': 'Database migration completed successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Manual database migration failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/api/clear-training-clients')
def clear_training_clients():
    """Quick endpoint to clear training clients table and start fresh"""
    try:
        logger.info("🗑️ Clearing training clients table...")
        
        if not hasattr(current_app, 'db_manager'):
            return jsonify({'success': False, 'error': 'Database manager not available'})
        
        # Clear the table
        current_app.db_manager.clear_training_clients()
        
        logger.info("✅ Training clients table cleared")
        
        return jsonify({
            'success': True,
            'message': 'Training clients table cleared successfully. The next sync will recreate with proper data.'
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to clear training clients: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/api/debug/populate-test-data')
def debug_populate_test_data():
    """DEBUG: Manually populate the cache with test training client data."""
    try:
        # Create test training client data that matches the expected structure
        test_training_clients = [
            {
                'id': '191215290',
                'name': 'Alejandra Espinoza',
                'member_name': 'Alejandra Espinoza',
                'clubos_member_id': '191215290',
                'member_id': '191215290',
                'prospect_id': '191215290',
                'trainer_name': 'Jeremy Mayo',
                'active_packages': ['6 WEEK CHALLENGE'],
                'past_due_amount': 25.0,
                'payment_status': 'Past Due',
                'sessions_remaining': 8,
                'last_session': '2025-01-28',
                'email': 'alejandra.espinoza@email.com',
                'phone': '920-555-0123',
                'source': 'test_data'
            },
            {
                'id': '174558923',
                'name': 'Mark Benzinger',
                'member_name': 'Mark Benzinger',
                'clubos_member_id': '174558923',
                'member_id': '174558923',
                'prospect_id': '174558923',
                'trainer_name': 'Jeremy Mayo',
                'active_packages': ['2025 Single Club Membership'],
                'past_due_amount': 0.0,
                'payment_status': 'Current',
                'sessions_remaining': 12,
                'last_session': '2025-01-27',
                'email': 'mark.benzinger@email.com',
                'phone': '920-555-0124',
                'source': 'test_data'
            },
            {
                'id': '191015549',
                'name': 'Ziann Crump',
                'member_name': 'Ziann Crump',
                'clubos_member_id': '191015549',
                'member_id': '191015549',
                'prospect_id': '191015549',
                'trainer_name': 'Jeremy Mayo',
                'active_packages': ['Personal Training Package'],
                'past_due_amount': 75.5,
                'payment_status': 'Past Due',
                'sessions_remaining': 4,
                'last_session': '2025-01-25',
                'email': 'ziann.crump@email.com',
                'phone': '920-555-0125',
                'source': 'test_data'
            }
        ]
        
        # Populate the cache
        if hasattr(current_app, 'data_cache'):
            current_app.data_cache['training_clients'] = test_training_clients
            logger.info(f"✅ DEBUG: Populated cache with {len(test_training_clients)} test training clients")
            
            return jsonify({
                'success': True,
                'message': f'Cache populated with {len(test_training_clients)} test training clients',
                'training_clients': test_training_clients
            })
        else:
            return jsonify({'success': False, 'error': 'No data cache available'})
            
    except Exception as e:
        logger.error(f"❌ DEBUG: Error populating test data: {e}")
        return jsonify({'success': False, 'error': str(e)})

@training_bp.route('/api/debug/cache-state')
def debug_cache_state():
    """DEBUG ENDPOINT: Check the current state of the data cache."""
    try:
        cache_info = {
            'training_clients_count': len(current_app.data_cache.get('training_clients', [])),
            'members_count': len(current_app.data_cache.get('members', [])),
            'last_cache_update': current_app.data_cache.get('last_update_time'),
            'sample_training_client': current_app.data_cache.get('training_clients', [{}])[0] if current_app.data_cache.get('training_clients') else {},
            'sample_member': current_app.data_cache.get('members', [{}])[0] if current_app.data_cache.get('members') else {}
        }
        return jsonify(cache_info)
    except Exception as e:
        return jsonify({'error': str(e)})
