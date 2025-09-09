#!/usr/bin/env python3
"""
Training Routes
Training client management, package details, and related functionality
"""

from flask import Blueprint, render_template, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

# Import ClubOS Training API for real package data
try:
    from src.clubos_training_api import ClubOSTrainingPackageAPI
except ImportError:
    try:
        from clubos_training_api import ClubOSTrainingPackageAPI
    except ImportError:
        logger.warning("⚠️ ClubOS Training API not available")
        ClubOSTrainingPackageAPI = None

def get_training_client_financial_summary(member_id):
    """Get real financial summary data from ClubOS API with actual invoice analysis"""
    try:
        if not ClubOSTrainingPackageAPI:
            logger.warning(f"⚠️ ClubOS Training API not available for member {member_id}")
            return {
                'total_past_due': 0.0,
                'active_agreements': 0,
                'total_sessions': 0,
                'total_value': 0.0
            }
        
        # Use the working ClubOS Training API
        api = ClubOSTrainingPackageAPI()
        
        # Get member's agreement IDs first
        payment_details = api.get_member_training_payment_details(member_id)
        
        if payment_details and payment_details.get('success'):
            agreement_ids = payment_details.get('agreement_ids', [])
            logger.info(f"📋 Found {len(agreement_ids)} agreements for member {member_id}")
            
            # Initialize financial totals
            total_past_due = 0.0
            total_paid = 0.0
            total_pending = 0.0
            total_value = 0.0
            total_sessions = 0
            
            # Process each agreement to get real invoice data
            for agreement_id in agreement_ids:
                try:
                    # Ensure proper delegation to member
                    api.delegate_to_member(member_id)
                    
                    # Direct V2 API call for invoice data (proven working method)
                    url = f'https://anytime.club-os.com/api/agreements/package_agreements/V2/{agreement_id}'
                    params = {
                        'include': ['invoices', 'scheduledPayments', 'prohibitChangeTypes']
                    }
                    
                    response = api.session.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract invoice data from include section
                        include_data = data.get('include', {})
                        invoices = include_data.get('invoices', [])
                        scheduled_payments = include_data.get('scheduledPayments', [])
                        agreement_data = data.get('data', {})
                        
                        logger.info(f"📄 Agreement {agreement_id}: {len(invoices)} invoices, {len(scheduled_payments)} scheduled payments")
                        
                        # Calculate invoice totals
                        for invoice in invoices:
                            status = invoice.get('invoiceStatus')
                            amount = float(invoice.get('total', 0))
                            
                            if status == 1:  # Paid
                                total_paid += amount
                            elif status == 2:  # Pending payment
                                total_pending += amount
                            elif status == 5:  # Delinquent/Past due
                                total_past_due += amount
                        
                        # Extract total agreement value
                        agreement_value = float(agreement_data.get('fullAgreementValue', 0))
                        if agreement_value > 0:
                            total_value += agreement_value
                        
                        # Extract session information from package agreement member services
                        package_services = agreement_data.get('packageAgreementMemberServices', [])
                        for service in package_services:
                            units_per_billing = service.get('unitsPerBillingDuration', 0)
                            billing_duration = agreement_data.get('duration', 1)
                            if units_per_billing and billing_duration:
                                total_sessions += units_per_billing * billing_duration
                        
                    else:
                        logger.warning(f"⚠️ Failed to get invoice data for agreement {agreement_id}: {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error processing agreement {agreement_id}: {e}")
                    continue
            
            # Create comprehensive financial summary
            financial_summary = {
                'active_agreements': len(agreement_ids),
                'total_sessions': total_sessions,
                'total_value': total_value,
                'total_past_due': total_past_due,
                'total_paid': total_paid,
                'total_pending': total_pending,
                'payment_status': 'Past Due' if total_past_due > 0 else 'Pending' if total_pending > 0 else 'Current'
            }
            
            logger.info(f"✅ Real financial summary for member {member_id}: {financial_summary['payment_status']}, ${total_past_due} past due, ${total_paid} paid, {len(agreement_ids)} agreements")
            return financial_summary
        
        else:
            # Fallback to basic data if payment details fail
            logger.warning(f"⚠️ Training payment details API failed for member {member_id}")
            return {
                'total_past_due': 0.0,
                'active_agreements': 0,
                'total_sessions': 0,
                'total_value': 0.0,
                'total_paid': 0.0,
                'total_pending': 0.0,
                'payment_status': 'Unknown'
            }
        
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

training_bp = Blueprint('training', __name__)

# Import the authentication decorator
from .auth import require_auth

@training_bp.route('/training-clients')
@require_auth
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
                
                # Use cached financial data instead of making fresh API calls
                financial_summary = {
                    'total_past_due': client_data.get('total_past_due', 0.0),
                    'active_agreements': len(client_data.get('package_details', [])) if client_data.get('package_details') else 1,
                    'total_sessions': client_data.get('sessions_remaining', 0),
                    'total_value': 0.0,  # We'll calculate this from package_details if needed
                    'payment_status': client_data.get('payment_status', 'Current')
                }
                
                logger.info(f"✅ Found training client {member_id} in cache with past due: ${financial_summary['total_past_due']}")
                return render_template('training_client_profile.html', 
                                     client=client_data, 
                                     training_client=client_data,
                                     financial_summary=financial_summary)
        
        # Fallback: try database
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tc.*, m.first_name, m.last_name, m.full_name, m.email, m.mobile_phone, m.status_message
            FROM training_clients tc
            LEFT JOIN members m ON (tc.member_id = m.guid OR tc.member_id = m.prospect_id)
            WHERE tc.member_id = ? OR tc.id = ?
        """, (member_id, member_id))
        
        client_record = cursor.fetchone()
        if client_record:
            client_data = dict(client_record)
            client_data['member_name'] = (client_data.get('full_name') or 
                                        f"{client_data.get('first_name', '')} {client_data.get('last_name', '')}".strip() or 
                                        'Unknown Client')
            conn.close()
            
            # Use database financial data instead of making fresh API calls
            financial_summary = {
                'total_past_due': client_data.get('total_past_due', 0.0),
                'active_agreements': len(client_data.get('package_details', [])) if client_data.get('package_details') else 1,
                'total_sessions': client_data.get('sessions_remaining', 0),
                'total_value': 0.0,  # We'll calculate this from package_details if needed
                'payment_status': client_data.get('payment_status', 'Current')
            }
            
            logger.info(f"✅ Found training client {member_id} in database with past due: ${financial_summary['total_past_due']}")
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

@training_bp.route('/api/training-clients/all')
def get_all_training_clients():
	"""Get all training clients from database (prioritized) or cache."""
	try:
		# Prioritize database data since it has the correct names from ClubOS assignees
		conn = current_app.db_manager.get_connection()
		cursor = conn.cursor()
		
		# Get all training clients directly from database
		cursor.execute("""
			SELECT * FROM training_clients 
			ORDER BY member_name, created_at DESC
		""")
		
		training_clients = []
		for row in cursor.fetchall():
			c = dict(row)
			
			# Parse JSON fields that are stored as strings in the database
			import json
			try:
				if c.get('active_packages') and isinstance(c['active_packages'], str):
					# Try to parse as JSON first
					try:
						c['active_packages'] = json.loads(c['active_packages'])
					except json.JSONDecodeError:
						# If it's not JSON, treat it as a single package name and convert to array
						c['active_packages'] = [c['active_packages']]
				elif not c.get('active_packages'):
					c['active_packages'] = []
			except (TypeError, AttributeError):
				c['active_packages'] = []
			
			try:
				if c.get('package_details') and isinstance(c['package_details'], str):
					# Try to parse as JSON first
					try:
						c['package_details'] = json.loads(c['package_details'])
					except json.JSONDecodeError:
						# If it's not JSON, create empty array
						c['package_details'] = []
				elif not c.get('package_details'):
					c['package_details'] = []
			except (TypeError, AttributeError):
				c['package_details'] = []
			
			# Ensure member_name is set, fallback if needed
			c['member_name'] = c.get('member_name') or f"Training Client #{str(c.get('clubos_member_id', 'Unknown'))[-4:]}"
			
			# Ensure required fields for frontend
			c['member_id'] = c.get('clubos_member_id')  # Use ClubOS ID as member_id for routing
			c['prospect_id'] = c.get('clubos_member_id')  # Also set prospect_id for compatibility
			c['trainer_name'] = c.get('trainer_name') or 'Jeremy Mayo'
			c['sessions_remaining'] = c.get('sessions_remaining') or 0
			c['last_session'] = c.get('last_session') or 'Never'
			c['payment_status'] = c.get('payment_status') or 'Unknown'
			
			training_clients.append(c)
		
		conn.close()
		
		if training_clients:
			logger.info(f"✅ Retrieved {len(training_clients)} training clients from database")
			return jsonify({'success': True, 'training_clients': training_clients, 'source': 'database'})
		
		# Fallback to cache only if database is empty
		if hasattr(current_app, 'data_cache') and current_app.data_cache.get('training_clients'):
			cached_training_clients = current_app.data_cache['training_clients']
			
			# Enhance training client data with member information
			enhanced_clients = []
			cached_members = current_app.data_cache.get('members', []) if hasattr(current_app, 'data_cache') else []
			
			for client in cached_training_clients:
				enhanced_client = client.copy()
				
				# Multiple strategies to match training clients with members
				client_id = client.get('id') or client.get('member_id') or client.get('clubos_member_id')
				client_name = client.get('name', '').strip()
				
				member_found = False
				
				if cached_members:
					# Strategy 1: Exact ID match
					for member in cached_members:
						if (str(member.get('id')) == str(client_id) or
							str(member.get('guid')) == str(client_id) or
							str(member.get('prospect_id')) == str(client_id) or
							str(member.get('prospectId')) == str(client_id)):
							
							# Add member information to client
							enhanced_client['member_name'] = member.get('full_name') or f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
							enhanced_client['email'] = member.get('email')
							enhanced_client['phone'] = member.get('mobile_phone') or member.get('mobilePhone')
							enhanced_client['first_name'] = member.get('firstName')
							enhanced_client['last_name'] = member.get('lastName')
							enhanced_client['status_message'] = member.get('status_message') or member.get('statusMessage')
							
							# Use member ID fields
							enhanced_client['member_id'] = member.get('guid') or member.get('prospect_id') or member.get('prospectId') or member.get('id')
							enhanced_client['prospect_id'] = member.get('prospect_id') or member.get('prospectId')
							enhanced_client['clubos_member_id'] = member.get('id') or member.get('prospect_id') or member.get('prospectId')
							member_found = True
							break
					
					# Strategy 2: Name-based matching if ID match failed and we have a name
					if not member_found and client_name:
						for member in cached_members:
							member_full_name = member.get('full_name') or f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
							if member_full_name and client_name.lower() == member_full_name.lower():
								# Add member information to client
								enhanced_client['member_name'] = member_full_name
								enhanced_client['email'] = member.get('email')
								enhanced_client['phone'] = member.get('mobile_phone') or member.get('mobilePhone')
								enhanced_client['first_name'] = member.get('firstName')
								enhanced_client['last_name'] = member.get('lastName')
								enhanced_client['status_message'] = member.get('status_message') or member.get('statusMessage')
								
								# Use member ID fields
								enhanced_client['member_id'] = member.get('guid') or member.get('prospect_id') or member.get('prospectId') or member.get('id')
								enhanced_client['prospect_id'] = member.get('prospect_id') or member.get('prospectId')
								enhanced_client['clubos_member_id'] = member.get('id') or member.get('prospect_id') or member.get('prospectId')
								member_found = True
								break
				
				# Ensure we have a name even if not found in members
				if not enhanced_client.get('member_name'):
					# Try different fallback strategies for training client names
					fallback_name = (
						client_name or  # Name from ClubOS assignees
						enhanced_client.get('full_name') or
						f"{enhanced_client.get('first_name', '')} {enhanced_client.get('last_name', '')}".strip() or
						f"Training Client #{str(client_id)[-4:]}" if client_id else "Unknown Client"  # Use last 4 digits of ID
					)
					enhanced_client['member_name'] = fallback_name
				
				# Ensure we have required fields for frontend
				enhanced_client['trainer_name'] = enhanced_client.get('trainer_name') or enhanced_client.get('trainer') or 'Jeremy Mayo'
				enhanced_client['sessions_remaining'] = enhanced_client.get('sessions_remaining') or 0
				enhanced_client['last_session'] = enhanced_client.get('last_session') or 'Never'
				enhanced_client['payment_status'] = enhanced_client.get('payment_status') or 'Unknown'
				
				enhanced_clients.append(enhanced_client)
			
			logger.info(f"✅ Retrieved {len(enhanced_clients)} enhanced training clients from cache")
			return jsonify({'success': True, 'training_clients': enhanced_clients, 'source': 'cache'})

		# Fallback to database
		conn = current_app.db_manager.get_connection()
		cursor = conn.cursor()
		
		# Get all training clients with member info joined
		cursor.execute(
			"""
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
			ORDER BY tc.created_at DESC
			"""
		)
		
		training_clients = []
		for row in cursor.fetchall():
			c = dict(row)
			
			# Use member info if available, otherwise fall back to training client info
			c['member_name'] = (c.get('member_full_name') or 
							  f"{c.get('member_first_name', '')} {c.get('member_last_name', '')}".strip() or
							  c.get('full_name') or
							  'Unknown Client')
			
			c['email'] = c.get('member_email') or c.get('email')
			c['phone'] = c.get('member_phone') or c.get('phone')
			c['status_message'] = c.get('member_status_message') or c.get('status')
			
			# Ensure required fields for frontend
			c['trainer_name'] = c.get('trainer_name') or 'Jeremy Mayo'
			c['sessions_remaining'] = c.get('sessions_remaining') or 0
			c['last_session'] = c.get('last_session') or 'Never'
			c['payment_status'] = c.get('payment_status') or 'Unknown'
			
			training_clients.append(c)
		
		conn.close()
		
		logger.info(f"✅ Retrieved {len(training_clients)} training clients from database")
		return jsonify({'success': True, 'training_clients': training_clients, 'source': 'database'})
		
	except Exception as e:
		logger.error(f"❌ Error getting all training clients: {e}")
		return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/api/training-clients/<member_id>/agreements')
def get_member_package_agreements(member_id):
    """Get training package agreements for a specific member from cached data."""
    try:
        # First try to get from cached data (which has our improved calculations)
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
            
            if client_data and client_data.get('package_details'):
                # Use our cached package details which have the correct past due amounts
                agreements = []
                package_details = client_data.get('package_details', [])
                
                if isinstance(package_details, str):
                    try:
                        import json
                        package_details = json.loads(package_details)
                    except:
                        package_details = [package_details]
                
                for package in package_details:
                    if isinstance(package, dict):
                        agreement = {
                            'agreement_id': package.get('agreement_id', 'Unknown'),
                            'package_name': package.get('package_name', 'Training Package'),
                            'amount_owed': package.get('amount_owed', 0.0),
                            'payment_status': package.get('payment_status', 'Current'),
                            'sessions_remaining': package.get('sessions_remaining', 0),
                            'amount': package.get('amount', 0.0),
                            'created_date': package.get('created_date', ''),
                            'invoice_count': package.get('invoice_count', 0),
                            'scheduled_payments_count': package.get('scheduled_payments_count', 0)
                        }
                        agreements.append(agreement)
                
                logger.info(f"✅ Retrieved {len(agreements)} agreements from cache for member {member_id}")
                return jsonify({'success': True, 'agreements': agreements, 'source': 'cache'})
        
        # Fallback to database
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT package_details, total_past_due, payment_status, sessions_remaining
            FROM training_clients 
            WHERE member_id = ? OR clubos_member_id = ? OR id = ?
        """, (member_id, member_id, member_id))
        
        client_record = cursor.fetchone()
        if client_record:
            package_details = client_record[0]  # package_details column
            total_past_due = client_record[1]  # total_past_due column
            payment_status = client_record[2]  # payment_status column
            sessions_remaining = client_record[3]  # sessions_remaining column
            
            conn.close()
            
            # Parse package details and create agreements
            agreements = []
            if package_details:
                try:
                    import json
                    if isinstance(package_details, str):
                        package_details = json.loads(package_details)
                    
                    for package in package_details:
                        if isinstance(package, dict):
                            agreement = {
                                'agreement_id': package.get('agreement_id', 'Unknown'),
                                'package_name': package.get('package_name', 'Training Package'),
                                'amount_owed': package.get('amount_owed', 0.0),
                                'payment_status': package.get('payment_status', payment_status),
                                'sessions_remaining': package.get('sessions_remaining', sessions_remaining),
                                'amount': package.get('amount', 0.0),
                                'created_date': package.get('created_date', ''),
                                'invoice_count': package.get('invoice_count', 0),
                                'scheduled_payments_count': package.get('scheduled_payments_count', 0)
                            }
                            agreements.append(agreement)
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing package details for member {member_id}: {e}")
                    # Fallback: create a simple agreement with total past due
                    agreements = [{
                        'agreement_id': 'Unknown',
                        'package_name': 'Training Package',
                        'amount_owed': total_past_due,
                        'payment_status': payment_status,
                        'sessions_remaining': sessions_remaining,
                        'amount': 0.0,
                        'created_date': '',
                        'invoice_count': 0,
                        'scheduled_payments_count': 0
                    }]
            
            logger.info(f"✅ Retrieved {len(agreements)} agreements from database for member {member_id}")
            return jsonify({'success': True, 'agreements': agreements, 'source': 'database'})
        
        conn.close()
        
        # If no data found, return empty list
        logger.info(f"ℹ️ No agreements found for member {member_id}")
        return jsonify({'success': True, 'agreements': [], 'source': 'none'})
            
    except Exception as e:
        logger.error(f"❌ Error getting agreements for member {member_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
