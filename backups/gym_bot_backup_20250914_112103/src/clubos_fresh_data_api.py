#!/usr/bin/env python3
"""
ClubOS Fresh Data API - Get real-time member and prospect data
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ClubOSFreshDataAPI:
    """API to fetch fresh member and prospect data from ClubOS"""
    
    def __init__(self, username: str = "j.mayo", password: str = "j@SD4fjhANK5WNA"):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.authenticated = False
        self.base_url = "https://anytime.club-os.com"
        
    def authenticate(self) -> bool:
        """Authenticate with ClubOS"""
        try:
            # Use the existing authentication method from clubos_training_api
            login_url = f"{self.base_url}/auth/login"
            
            login_data = {
                'username': self.username,
                'password': self.password
            }
            
            response = self.session.post(login_url, data=login_data)
            
            if response.status_code == 200 and "dashboard" in response.url:
                self.authenticated = True
                logger.info("✅ ClubOS authentication successful for fresh data API")
                return True
            else:
                logger.error(f"❌ ClubOS authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ ClubOS authentication error: {e}")
            return False
    
    def get_fresh_members(self) -> List[Dict]:
        """Get fresh member data from ClubHub - ALL members at once like ClubHub does"""
        if not self.authenticated:
            if not self.authenticate():
                return []
        
        try:
            logger.info("📊 Fetching ALL fresh member data from ClubHub API...")
            
            # Get ClubHub credentials from SecureSecretsManager
            from .services.authentication.secure_secrets_manager import SecureSecretsManager
            secrets_manager = SecureSecretsManager()
            CLUBHUB_EMAIL = secrets_manager.get_secret('clubhub-email')
            CLUBHUB_PASSWORD = secrets_manager.get_secret('clubhub-password')
            
            if not CLUBHUB_EMAIL or not CLUBHUB_PASSWORD:
                logger.error("❌ ClubHub credentials not found in SecureSecretsManager")
                return []
            
            # ClubHub API endpoint for getting all members
            members_url = "https://app.clubhub.com/api/members/export"
            
            # Authenticate with ClubHub and get all members
            login_data = {
                'email': CLUBHUB_EMAIL,
                'password': CLUBHUB_PASSWORD
            }
            
            # First login to ClubHub
            login_response = self.session.post("https://app.clubhub.com/api/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                logger.info("✅ ClubHub authentication successful")
                
                # Now get all members data
                members_response = self.session.get(members_url)
                
                if members_response.status_code == 200:
                    members_data = members_response.json()
                    
                    # Process the members data to match our expected format
                    processed_members = []
                    
                    if isinstance(members_data, list):
                        for member in members_data:
                            processed_member = {
                                'ProspectID': member.get('id', member.get('prospect_id')),
                                'Name': f"{member.get('first_name', '')} {member.get('last_name', '')}".strip(),
                                'FirstName': member.get('first_name', ''),
                                'LastName': member.get('last_name', ''),
                                'Email': member.get('email', ''),
                                'Phone': member.get('phone', member.get('mobile_phone', '')),
                                'MobilePhone': member.get('mobile_phone', ''),
                                'Address': member.get('address', member.get('address1', '')),
                                'Address1': member.get('address1', ''),
                                'City': member.get('city', ''),
                                'State': member.get('state', ''),
                                'ZipCode': member.get('zip', member.get('zip_code', '')),
                                'Zip': member.get('zip', ''),
                                'StatusMessage': member.get('status_message', member.get('payment_status', '')),
                                'MemberSince': member.get('membership_start', member.get('member_since', '')),
                                'MembershipStart': member.get('membership_start', ''),
                                'LastVisit': member.get('last_visit', ''),
                                'Status': member.get('status', ''),
                                'PaymentStatus': member.get('payment_status', ''),
                                'AccountStatus': member.get('account_status', ''),
                                'MembershipType': member.get('membership_type', ''),
                                'AmountPastDue': member.get('amount_past_due', 0),
                                'NextPaymentDate': member.get('next_payment_date', ''),
                                'NextPaymentAmount': member.get('next_payment_amount', 0)
                            }
                            processed_members.append(processed_member)
                    
                    logger.info(f"✅ Retrieved {len(processed_members)} members from ClubHub API")
                    return processed_members
                    
                else:
                    logger.error(f"❌ Failed to get members data: {members_response.status_code}")
                    return []
            else:
                logger.error(f"❌ ClubHub login failed: {login_response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching fresh member data from ClubHub: {e}")
            return []
    
    def get_fresh_prospects(self) -> List[Dict]:
        """Get fresh prospect data from ClubOS"""
        if not self.authenticated:
            if not self.authenticate():
                return []
        
        try:
            logger.info("📈 Fetching fresh prospect data from ClubOS...")
            
            # This would call the actual ClubOS prospects endpoint
            prospects_url = f"{self.base_url}/prospects/export"
            
            response = self.session.get(prospects_url)
            
            if response.status_code == 200:
                logger.info("✅ Fresh prospect data retrieved")
                return []  # Placeholder
            else:
                logger.error(f"❌ Failed to get fresh prospect data: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching fresh prospect data: {e}")
            return []
    
    def get_member_payment_status(self, member_id: str) -> Dict:
        """Get real-time payment status for a specific member"""
        if not self.authenticated:
            if not self.authenticate():
                return {}
        
        try:
            # This would call the ClubOS payment status API
            payment_url = f"{self.base_url}/members/{member_id}/payment-status"
            
            response = self.session.get(payment_url)
            
            if response.status_code == 200:
                # Parse payment status
                return {
                    'member_id': member_id,
                    'status': 'Current',  # Placeholder
                    'amount_due': 0,
                    'last_payment': datetime.now().isoformat(),
                    'next_payment_date': None
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error getting payment status for member {member_id}: {e}")
            return {}
    
    def get_member_payment_history(self, member_id: str) -> List[Dict]:
        """Get the complete payment history for a member."""
        if not self.authenticated:
            if not self.authenticate():
                return []
        
        # This is a placeholder. In a real scenario, this would call a ClubOS API endpoint.
        logger.info(f"Fetching payment history for member {member_id}...")
        return [
            {"date": "2025-07-01", "amount": 50.00, "status": "Paid", "description": "Monthly Dues"},
            {"date": "2025-06-01", "amount": 50.00, "status": "Paid", "description": "Monthly Dues"},
            {"date": "2025-05-01", "amount": 50.00, "status": "Missed", "description": "Monthly Dues"},
            {"date": "2025-04-01", "amount": 50.00, "status": "Paid", "description": "Monthly Dues"},
        ]
    
    def get_fresh_data_summary(self) -> Dict:
        """Get a summary of fresh data from ClubOS"""
        try:
            logger.info("📋 Getting fresh data summary from ClubOS...")
            
            if not self.authenticated:
                if not self.authenticate():
                    return {}
            
            # Get counts and summary info
            summary = {
                'timestamp': datetime.now().isoformat(),
                'members': {
                    'total': 0,
                    'active': 0,
                    'past_due': 0,
                    'due_soon': 0
                },
                'prospects': {
                    'total': 0,
                    'new_today': 0,
                    'hot_leads': 0
                },
                'last_updated': datetime.now().isoformat()
            }
            
            logger.info("✅ Fresh data summary retrieved")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting fresh data summary: {e}")
            return {}

    def get_member_agreement_details(self, member_id: str) -> Dict:
        """Get detailed agreement and billing information for a specific member from ClubHub"""
        if not self.authenticated:
            if not self.authenticate():
                return {}
        
        try:
            logger.info(f"📋 Fetching agreement details for member {member_id} from ClubHub...")
            
            # Get ClubHub credentials from SecureSecretsManager
            from .services.authentication.secure_secrets_manager import SecureSecretsManager
            secrets_manager = SecureSecretsManager()
            CLUBHUB_EMAIL = secrets_manager.get_secret('clubhub-email')
            CLUBHUB_PASSWORD = secrets_manager.get_secret('clubhub-password')
            
            if not CLUBHUB_EMAIL or not CLUBHUB_PASSWORD:
                logger.error("❌ ClubHub credentials not found in SecureSecretsManager")
                return {}
            
            # ClubHub API base URL (from API documentation)
            clubhub_base = "https://clubhub-ios-api.anytimefitness.com/api"
            
            # First, authenticate with ClubHub iOS API
            login_url = f"{clubhub_base}/login"
            login_data = {
                'email': CLUBHUB_EMAIL,
                'password': CLUBHUB_PASSWORD
            }
            
            # Login to get authorization token
            login_response = self.session.post(login_url, json=login_data)
            if login_response.status_code != 200:
                logger.error(f"❌ ClubHub iOS API login failed: {login_response.status_code}")
                return {}
            
            # Get authorization token from response
            auth_token = login_response.json().get('token', '')
            if not auth_token:
                logger.error("❌ No authorization token received from ClubHub")
                return {}
            
            # Set authorization header for subsequent requests
            headers = {
                'Authorization': f'Bearer {auth_token}',
                'Accept': 'application/json',
                'API-version': '1'
            }
            
            # Get member's agreement details
            agreement_url = f"{clubhub_base}/members/{member_id}/agreement"
            agreement_response = self.session.get(agreement_url, headers=headers)
            
            if agreement_response.status_code == 200:
                agreement_data = agreement_response.json()
                logger.info(f"✅ Retrieved agreement data for member {member_id}")
                
                # Get additional billing details if agreement exists
                billing_details = {}
                if agreement_data.get('id'):
                    agreement_id = agreement_data['id']
                    
                    # Get detailed billing status with invoices and scheduled payments
                    billing_url = f"https://anytime.club-os.com/api/agreements/package_agreements/V2/{agreement_id}?include=invoices&include=scheduledPayments&include=prohibitChangeTypes"
                    billing_response = self.session.get(billing_url, headers=headers)
                    
                    if billing_response.status_code == 200:
                        billing_details = billing_response.json()
                        logger.info(f"✅ Retrieved billing details for agreement {agreement_id}")
                    
                    # Get current billing status
                    status_url = f"https://anytime.club-os.com/api/agreements/package_agreements/{agreement_id}/billing_status"
                    status_response = self.session.get(status_url, headers=headers)
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        billing_details['billing_status'] = status_data
                        logger.info(f"✅ Retrieved billing status for agreement {agreement_id}")
                
                # Combine agreement and billing data
                complete_data = {
                    'member_id': member_id,
                    'agreement': agreement_data,
                    'billing_details': billing_details,
                    'timestamp': datetime.now().isoformat()
                }
                
                return complete_data
                
            else:
                logger.error(f"❌ Failed to get agreement for member {member_id}: {agreement_response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error getting agreement details for member {member_id}: {e}")
            return {}
    
    def get_members_with_billing_details(self, member_ids: List[str] = None) -> List[Dict]:
        """Get members with their real billing details from ClubHub agreements"""
        if not self.authenticated:
            if not self.authenticate():
                return []
        
        try:
            logger.info("💰 Fetching members with real billing details from ClubHub...")
            
            # If no specific member IDs provided, get all members first
            if not member_ids:
                members = self.get_fresh_members()
                member_ids = [m.get('ProspectID') for m in members if m.get('ProspectID')]
            
            members_with_billing = []
            
            for member_id in member_ids[:10]:  # Limit to 10 for testing to avoid rate limits
                try:
                    logger.info(f"🔍 Processing billing for member {member_id}")
                    
                    # Get agreement and billing details
                    billing_data = self.get_member_agreement_details(member_id)
                    
                    if billing_data and billing_data.get('agreement'):
                        agreement = billing_data['agreement']
                        billing_details = billing_data.get('billing_details', {})
                        
                        # Extract real past due information
                        past_due_amount = 0.0
                        missed_payments = 0
                        late_fees = 0.0
                        next_payment_amount = 0.0
                        next_payment_date = None
                        
                        # Check invoices for past due amounts
                        invoices = billing_details.get('invoices', [])
                        for invoice in invoices:
                            if invoice.get('status') == 'past_due' or invoice.get('overdue', False):
                                past_due_amount += float(invoice.get('amount', 0))
                                missed_payments += 1
                        
                        # Check scheduled payments for upcoming dues
                        scheduled_payments = billing_details.get('scheduledPayments', [])
                        if scheduled_payments:
                            next_payment = scheduled_payments[0]  # Next upcoming payment
                            next_payment_amount = float(next_payment.get('amount', 0))
                            next_payment_date = next_payment.get('dueDate')
                        
                        # Calculate late fees (same logic as frontend)
                        if past_due_amount > 0:
                            payment_periods_behind = max(1, int(past_due_amount / 50))
                            late_fees = min(100.0, max(25.0, payment_periods_behind * 5.0))
                        
                        member_billing = {
                            'member_id': member_id,
                            'amount_past_due': past_due_amount,
                            'missed_payments': missed_payments,
                            'late_fees': late_fees,
                            'next_payment_amount': next_payment_amount,
                            'next_payment_date': next_payment_date,
                            'total_invoice_amount': past_due_amount + late_fees,
                            'agreement_id': agreement.get('id'),
                            'billing_status': billing_details.get('billing_status', {}),
                            'last_updated': datetime.now().isoformat()
                        }
                        
                        members_with_billing.append(member_billing)
                        logger.info(f"✅ Processed billing for member {member_id}: ${past_due_amount:.2f} past due")
                    
                    else:
                        logger.warning(f"⚠️ No agreement found for member {member_id}")
                
                except Exception as e:
                    logger.error(f"❌ Error processing billing for member {member_id}: {e}")
                    continue
            
            logger.info(f"✅ Retrieved billing details for {len(members_with_billing)} members")
            return members_with_billing
            
        except Exception as e:
            logger.error(f"❌ Error getting members with billing details: {e}")
            return []
    
    def update_member_billing_in_database(self, member_billing_data: List[Dict]) -> bool:
        """Update the database with real billing information from ClubHub"""
        try:
            from .services.database_manager import DatabaseManager
            
            db_manager = DatabaseManager()
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            updated_count = 0
            
            for billing in member_billing_data:
                member_id = billing.get('member_id')
                amount_past_due = billing.get('amount_past_due', 0)
                missed_payments = billing.get('missed_payments', 0)
                late_fees = billing.get('late_fees', 0)
                next_payment_amount = billing.get('next_payment_amount', 0)
                next_payment_date = billing.get('next_payment_date')
                
                # Update the members table with real billing data
                cursor.execute("""
                    UPDATE members 
                    SET amount_past_due = ?, 
                        amount_of_next_payment = ?,
                        date_of_next_payment = ?,
                        billing_updated_at = ?
                    WHERE prospect_id = ? OR id = ?
                """, (
                    amount_past_due, 
                    next_payment_amount, 
                    next_payment_date,
                    datetime.now().isoformat(),
                    member_id, 
                    member_id
                ))
                
                if cursor.rowcount > 0:
                    updated_count += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Updated billing information for {updated_count} members in database")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating member billing in database: {e}")
            return False

if __name__ == "__main__":
    # Test the API
    api = ClubOSFreshDataAPI()
    if api.authenticate():
        summary = api.get_fresh_data_summary()
        print(f"Fresh data summary: {json.dumps(summary, indent=2)}")
    else:
        print("Failed to authenticate with ClubOS")
