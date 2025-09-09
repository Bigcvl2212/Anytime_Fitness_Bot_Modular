#!/usr/bin/env python3
"""
Enhanced Comprehensive Data Pull with Agreement Details
Fetches all members and prospects with full agreement financial data
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import os
import sys
from typing import Dict, List, Optional, Tuple
import logging

# Add the project root to the path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedDataPuller:
    def __init__(self):
        self.clubhub_base = "https://clubhub-ios-api.anytimefitness.com"
        self.clubos_base = "https://anytime.club-os.com"
        self.session = requests.Session()
        self.club_ids = [1156]  # Only club 1156
        
    def get_fresh_auth_token(self):
        """Get a fresh authentication token"""
        try:
            # Try to get from the token capture system
            try:
                from src.services.authentication.clubhub_token_capture import ClubHubTokenCapture
                token_capturer = ClubHubTokenCapture()
                token_data = token_capturer.get_latest_token()
                
                if token_data and 'bearer_token' in token_data:
                    logger.info("Using fresh token from ClubHubTokenCapture")
                    return token_data['bearer_token']
                else:
                    logger.warning("No fresh token from ClubHubTokenCapture, trying automated login")
            except ImportError:
                logger.warning("ClubHubTokenCapture not available, trying automated login")
            
            # Fallback to automated login
            try:
                from src.services.authentication.clubhub_automated_login import ClubHubAutomatedLogin
                auto_login = ClubHubAutomatedLogin()
                success, auth_data = auto_login.login()
                
                if success and auth_data.get('bearer_token'):
                    logger.info("Using token from ClubHubAutomatedLogin")
                    return auth_data['bearer_token']
                else:
                    logger.error("ClubHubAutomatedLogin failed")
            except ImportError:
                logger.error("ClubHubAutomatedLogin not available")
            
            # Final fallback - try to read from token file
            try:
                token_file = "data/clubhub_tokens.json"
                if os.path.exists(token_file):
                    with open(token_file, 'r') as f:
                        token_data = json.load(f)
                    
                    if isinstance(token_data, list) and token_data:
                        latest_token = token_data[-1]
                        bearer_token = latest_token.get('bearer_token')
                        if bearer_token:
                            logger.info("Using token from token file")
                            return bearer_token
                        
            except Exception as e:
                logger.error(f"Error reading token file: {e}")
            
            logger.error("No valid authentication token available")
            return None
                
        except Exception as e:
            logger.error(f"Error getting fresh token: {e}")
            return None
    
    def get_clubhub_headers(self):
        """Get ClubHub API headers"""
        token = self.get_fresh_auth_token()
        if not token:
            raise Exception("No valid authentication token available")
            
        return {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'User-Agent': 'ClubHub-iOS/4.0.0',
            'API-version': '1'
        }
    
    def get_clubos_headers(self):
        """Get ClubOS API headers for agreement data"""
        try:
            # Use existing ClubOS authentication system
            from src.services.api.clubos_api_client import ClubOSAPIAuthentication
            
            # Helper function to get secrets
            def get_secret(key):
                try:
                    from utils.config import get_secret
                    return get_secret(key)
                except ImportError:
                    # Fallback: try environment variables
                    import os
                    return os.getenv(key.upper().replace('-', '_'))
            
            # Create and authenticate ClubOS client if not exists
            if not hasattr(self, 'clubos_auth') or not self.clubos_auth.is_authenticated:
                self.clubos_auth = ClubOSAPIAuthentication()
                username = get_secret("clubos-username")
                password = get_secret("clubos-password")
                
                if username and password:
                    logger.info("Authenticating with ClubOS...")
                    if self.clubos_auth.login(username, password):
                        logger.info("ClubOS authentication successful")
                    else:
                        logger.error("ClubOS authentication failed")
                        raise Exception("ClubOS authentication failed")
                else:
                    raise Exception("ClubOS credentials not configured")
            
            return self.clubos_auth.get_headers()
            
        except Exception as e:
            logger.error(f"Error getting ClubOS headers: {e}")
            # Fallback headers without authentication
            return {
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://anytime.club-os.com/',
                'X-Requested-With': 'XMLHttpRequest'
            }
    
    def fetch_all_members_and_prospects(self):
        """Fetch all members and prospects from ClubHub API"""
        logger.info("Starting comprehensive data pull...")
        
        all_members = []
        all_prospects = []
        headers = self.get_clubhub_headers()
        
        for club_id in self.club_ids:
            logger.info(f"Processing Club {club_id}...")
            
            # Fetch members
            members = self._fetch_all_members_for_club(club_id, headers)
            all_members.extend(members)
            
            # Fetch prospects  
            prospects = self._fetch_all_prospects_for_club(club_id, headers)
            all_prospects.extend(prospects)
            
        logger.info(f"Data pull complete: {len(all_members)} members, {len(all_prospects)} prospects")
        return all_members, all_prospects
    
    def _fetch_all_members_for_club(self, club_id: str, headers: Dict) -> List[Dict]:
        """Fetch all members for a specific club"""
        members = []
        page = 1
        
        while True:
            try:
                url = f"{self.clubhub_base}/api/clubs/{club_id}/members"
                params = {"page": page, "pageSize": 50}
                
                response = self.session.get(url, headers=headers, params=params, verify=False, timeout=30)
                
                if response.ok:
                    data = response.json()
                    page_members = data.get('members', data.get('data', []))
                    
                    if not page_members:
                        break
                        
                    logger.info(f"  Club {club_id} members page {page}: {len(page_members)} found")
                    members.extend(page_members)
                    
                    if len(page_members) < 50:
                        break
                        
                    page += 1
                    if page > 200:
                        logger.warning(f"Reached page limit for club {club_id} members")
                        break
                else:
                    logger.error(f"API request failed for club {club_id} members: {response.status_code}")
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching members for club {club_id}, page {page}: {e}")
                break
                
        logger.info(f"Total members from Club {club_id}: {len(members)}")
        return members
    
    def _fetch_all_prospects_for_club(self, club_id: str, headers: Dict) -> List[Dict]:
        """Fetch all prospects for a specific club"""
        prospects = []
        page = 1
        
        while True:
            try:
                url = f"{self.clubhub_base}/api/clubs/{club_id}/prospects"
                params = {"page": page, "pageSize": 50}
                
                response = self.session.get(url, headers=headers, params=params, verify=False, timeout=30)
                
                if response.ok:
                    data = response.json()
                    page_prospects = data.get('prospects', data.get('data', []))
                    
                    if not page_prospects:
                        break
                        
                    logger.info(f"  Club {club_id} prospects page {page}: {len(page_prospects)} found")
                    prospects.extend(page_prospects)
                    
                    if len(page_prospects) < 50:
                        break
                        
                    page += 1
                    if page > 200:
                        logger.warning(f"Reached page limit for club {club_id} prospects")
                        break
                else:
                    logger.error(f"API request failed for club {club_id} prospects: {response.status_code}")
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching prospects for club {club_id}, page {page}: {e}")
                break
                
        logger.info(f"Total prospects from Club {club_id}: {len(prospects)}")
        return prospects
    
    def fetch_member_agreement_details(self, member_id: str) -> Optional[Dict]:
        """Fetch detailed agreement information for a member"""
        try:
            # First get the basic agreement from ClubHub
            headers = self.get_clubhub_headers()
            url = f"{self.clubhub_base}/api/members/{member_id}/agreement"
            
            response = self.session.get(url, headers=headers, verify=False, timeout=15)
            
            if response.ok:
                basic_agreement = response.json()
                
                # If we have an agreement ID, get detailed info from ClubOS
                agreement_id = basic_agreement.get('id')
                if agreement_id:
                    detailed_agreement = self._fetch_clubos_agreement_details(agreement_id)
                    if detailed_agreement:
                        # Merge the data
                        basic_agreement.update(detailed_agreement)
                        
                return basic_agreement
            else:
                logger.debug(f"No agreement found for member {member_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching agreement for member {member_id}: {e}")
            return None
    
    def _fetch_clubos_agreement_details(self, agreement_id: str) -> Optional[Dict]:
        """Fetch detailed agreement data from ClubOS API"""
        try:
            headers = self.get_clubos_headers()
            url = f"{self.clubos_base}/api/agreements/package_agreements/V2/{agreement_id}"
            params = {
                'include': ['invoices', 'scheduledPayments', 'prohibitChangeTypes']
            }
            
            response = self.session.get(url, headers=headers, params=params, verify=False, timeout=15)
            
            if response.ok:
                details = response.json()
                
                # Calculate financial information
                financial_data = self._calculate_financial_details(details)
                details.update(financial_data)
                
                return details
            else:
                logger.debug(f"Could not fetch ClubOS details for agreement {agreement_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching ClubOS agreement details for {agreement_id}: {e}")
            return None
    
    def _calculate_financial_details(self, agreement_details: Dict) -> Dict:
        """Calculate financial information from agreement details"""
        financial_data = {
            'amountPastDue': 0.0,
            'totalOutstanding': 0.0,
            'lastPaymentDate': None,
            'nextPaymentDate': None,
            'totalInvoiced': 0.0,
            'totalPaid': 0.0,
            'unpaidInvoices': [],
            'scheduledPayments': []
        }
        
        # Process invoices
        invoices = agreement_details.get('invoices', [])
        for invoice in invoices:
            amount = float(invoice.get('amount', 0))
            status = invoice.get('status', '').upper()
            
            financial_data['totalInvoiced'] += amount
            
            if status == 'UNPAID':
                financial_data['amountPastDue'] += amount
                financial_data['unpaidInvoices'].append({
                    'id': invoice.get('id'),
                    'amount': amount,
                    'dueDate': invoice.get('dueDate'),
                    'description': invoice.get('description', '')
                })
            elif status == 'PAID':
                financial_data['totalPaid'] += amount
                payment_date = invoice.get('paymentDate')
                if payment_date:
                    if not financial_data['lastPaymentDate'] or payment_date > financial_data['lastPaymentDate']:
                        financial_data['lastPaymentDate'] = payment_date
        
        # Process scheduled payments
        scheduled = agreement_details.get('scheduledPayments', [])
        for payment in scheduled:
            if payment.get('status', '').upper() != 'PAID':
                due_date = payment.get('dueDate')
                if due_date:
                    financial_data['scheduledPayments'].append({
                        'id': payment.get('id'),
                        'amount': float(payment.get('amount', 0)),
                        'dueDate': due_date,
                        'status': payment.get('status', '')
                    })
                    
                    # Find next payment date
                    if not financial_data['nextPaymentDate'] or due_date < financial_data['nextPaymentDate']:
                        financial_data['nextPaymentDate'] = due_date
        
        financial_data['totalOutstanding'] = financial_data['amountPastDue']
        
        return financial_data
    
    def create_comprehensive_contact_list(self, members: List[Dict], prospects: List[Dict]) -> pd.DataFrame:
        """Create comprehensive contact list with agreement details"""
        logger.info("Creating comprehensive contact list with agreement details...")
        
        contacts = []
        
        # Process members with agreement details
        logger.info(f"Processing {len(members)} members with agreement details...")
        for i, member in enumerate(members):
            if i % 50 == 0:
                logger.info(f"  Processed {i}/{len(members)} members...")
                
            # Get agreement details
            member_id = member.get('id')
            agreement_data = {}
            
            if member_id:
                agreement_details = self.fetch_member_agreement_details(member_id)
                if agreement_details:
                    agreement_data = self._flatten_agreement_data(agreement_details)
            
            # Create contact record
            contact = self._create_contact_record(member, 'Member', agreement_data)
            contacts.append(contact)
            
            # Rate limiting
            time.sleep(0.1)
        
        # Process prospects
        logger.info(f"Processing {len(prospects)} prospects...")
        for i, prospect in enumerate(prospects):
            if i % 50 == 0:
                logger.info(f"  Processed {i}/{len(prospects)} prospects...")
                
            contact = self._create_contact_record(prospect, 'Prospect', {})
            contacts.append(contact)
        
        # Create DataFrame
        df = pd.DataFrame(contacts)
        
        # Remove duplicates and sort
        df = df.drop_duplicates(subset=['Name', 'Email'], keep='first')
        df = df.sort_values(['Category', 'Name'])
        
        logger.info(f"Created comprehensive contact list with {len(df)} total contacts")
        return df
    
    def _flatten_agreement_data(self, agreement_data: Dict) -> Dict:
        """Flatten agreement data for inclusion in contact record"""
        flattened = {}
        
        # Direct mapping of important fields
        field_mappings = {
            'id': 'agreement.id',
            'agreementType': 'agreement.type',
            'status': 'agreement.status',
            'startDate': 'agreement.startDate',
            'endDate': 'agreement.endDate',
            'amountPastDue': 'agreement.amountPastDue',
            'totalOutstanding': 'agreement.totalOutstanding',
            'lastPaymentDate': 'agreement.lastPaymentDate',
            'nextPaymentDate': 'agreement.nextPaymentDate',
            'totalInvoiced': 'agreement.totalInvoiced',
            'totalPaid': 'agreement.totalPaid',
            'recurringCost': 'agreement.recurringCost.total',
            'billingFrequency': 'agreement.billingFrequency',
            'membershipType': 'agreement.membershipType'
        }
        
        for source_key, target_key in field_mappings.items():
            value = agreement_data.get(source_key)
            if value is not None:
                flattened[target_key] = value
        
        # Handle nested recurringCost
        recurring_cost = agreement_data.get('recurringCost', {})
        if isinstance(recurring_cost, dict):
            flattened['agreement.recurringCost.total'] = recurring_cost.get('total', 0)
            flattened['agreement.recurringCost.subtotal'] = recurring_cost.get('subtotal', 0)
            flattened['agreement.recurringCost.tax'] = recurring_cost.get('tax', 0)
        
        # Add unpaid invoices count
        unpaid_invoices = agreement_data.get('unpaidInvoices', [])
        flattened['agreement.unpaidInvoicesCount'] = len(unpaid_invoices)
        
        # Add scheduled payments count
        scheduled_payments = agreement_data.get('scheduledPayments', [])
        flattened['agreement.scheduledPaymentsCount'] = len(scheduled_payments)
        
        return flattened
    
    def _create_contact_record(self, person_data: Dict, category: str, agreement_data: Dict) -> Dict:
        """Create a standardized contact record"""
        # Extract basic information
        contact = {
            'ProspectID': person_data.get('id', ''),
            'Name': f"{person_data.get('firstName', '')} {person_data.get('lastName', '')}".strip(),
            'FirstName': person_data.get('firstName', ''),
            'LastName': person_data.get('lastName', ''),
            'Email': person_data.get('email', ''),
            'Phone': person_data.get('phone', ''),
            'Category': category,
            'Status': person_data.get('status', ''),
            'CreatedDate': person_data.get('createdDate', ''),
            'LastModifiedDate': person_data.get('lastModifiedDate', ''),
            'Address': person_data.get('address', ''),
            'City': person_data.get('city', ''),
            'State': person_data.get('state', ''),
            'ZipCode': person_data.get('zipCode', ''),
            'DateOfBirth': person_data.get('dateOfBirth', ''),
            'Gender': person_data.get('gender', ''),
            'MembershipType': person_data.get('membershipType', ''),
            'JoinDate': person_data.get('joinDate', ''),
            'LastVisit': person_data.get('lastVisit', ''),
            'Notes': person_data.get('notes', ''),
            'Tags': json.dumps(person_data.get('tags', [])) if person_data.get('tags') else '',
            'CustomFields': json.dumps(person_data.get('customFields', {})) if person_data.get('customFields') else '',
            'ClubID': person_data.get('clubId', ''),
            'SourceCampaign': person_data.get('sourceCampaign', ''),
            'EmergencyContact': person_data.get('emergencyContact', ''),
            'FetchedAt': datetime.now().isoformat()
        }
        
        # Add agreement data if available
        contact.update(agreement_data)
        
        return contact
    
    def save_contact_list(self, df: pd.DataFrame) -> Tuple[str, str]:
        """Save the contact list to CSV and Excel files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as CSV
        csv_filename = f"master_contact_list_{timestamp}.csv"
        df.to_csv(csv_filename, index=False)
        
        # Save as Excel
        excel_filename = f"master_contact_list_{timestamp}.xlsx"
        df.to_excel(excel_filename, index=False)
        
        logger.info(f"Saved contact list: {csv_filename} and {excel_filename}")
        return csv_filename, excel_filename

def main():
    """Main execution function"""
    try:
        logger.info("Starting Enhanced Comprehensive Data Pull with Agreement Details")
        logger.info("=" * 70)
        
        # Initialize the data puller
        puller = EnhancedDataPuller()
        
        # Fetch all members and prospects
        members, prospects = puller.fetch_all_members_and_prospects()
        
        # Create comprehensive contact list with agreement details
        df = puller.create_comprehensive_contact_list(members, prospects)
        
        # Save the results
        csv_file, excel_file = puller.save_contact_list(df)
        
        # Print summary
        logger.info("🎉 COMPREHENSIVE DATA PULL COMPLETE!")
        logger.info(f"   📄 CSV File: {csv_file}")
        logger.info(f"   📄 Excel File: {excel_file}")
        logger.info(f"   📊 Total contacts: {len(df)}")
        logger.info(f"   👥 Members: {len(df[df['Category'] == 'Member'])}")
        logger.info(f"   🎯 Prospects: {len(df[df['Category'] == 'Prospect'])}")
        
        # Show agreement data summary
        agreement_columns = [col for col in df.columns if col.startswith('agreement.')]
        if agreement_columns:
            logger.info(f"   💰 Agreement fields included: {len(agreement_columns)}")
            
            # Show members with past due amounts
            members_with_debt = df[(df['Category'] == 'Member') & (df.get('agreement.amountPastDue', 0) > 0)]
            if len(members_with_debt) > 0:
                total_past_due = members_with_debt['agreement.amountPastDue'].sum()
                logger.info(f"   🚨 Members with past due: {len(members_with_debt)}")
                logger.info(f"   💸 Total past due amount: ${total_past_due:,.2f}")
        
        # Show sample data
        logger.info("\n📋 Sample contacts:")
        sample_cols = ['Name', 'Email', 'Category', 'agreement.amountPastDue', 'agreement.nextPaymentDate']
        available_cols = [col for col in sample_cols if col in df.columns]
        if available_cols:
            print(df.head(10)[available_cols].to_string(index=False))
        
        return df
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
