#!/usr/bin/env python3
"""
Club OS Training Package Data Replicator
Replicates the exact process Club OS uses to fetch and display training package data
"""

import sys
import os
sys.path.append('src')

import requests
import json
from src.clubos_training_api import ClubOSTrainingPackageAPI

class ClubOSDataReplicator:
    """Replicates Club OS training package data retrieval process"""
    
    def __init__(self):
        self.api = ClubOSTrainingPackageAPI()
        self.base_url = "https://anytime.club-os.com"
        
    def get_member_training_packages(self, member_identifier):
        """
        Replicate Club OS training package data retrieval process
        
        Args:
            member_identifier: Can be clubos_member_id, name, or email
            
        Returns:
            dict: Complete training package data structure matching Club OS
        """
        
        print(f"🔍 Starting Club OS data replication for: {member_identifier}")
        
        try:
            # Step 1: Authentication (replicate Club OS login)
            if not self.api.authenticate():
                return {"error": "Authentication failed", "success": False}
                
            print("✅ Authentication successful")
            
            # Step 2: Find member and get IDs (replicate Club OS member lookup)
            member_data = self._find_member_data(member_identifier)
            if not member_data:
                return {"error": "Member not found", "success": False}
                
            member_id = member_data.get('member_id')
            agreement_ids = member_data.get('agreement_ids', [])
            
            print(f"✅ Found member ID: {member_id}")
            print(f"✅ Found agreement IDs: {agreement_ids}")
            
            # Step 3: Get comprehensive package data (replicate Club OS multi-endpoint approach)
            package_data = {}
            
            for agreement_id in agreement_ids:
                print(f"🔄 Processing agreement ID: {agreement_id}")
                
                # Replicate Club OS agreement details call
                agreement_details = self._get_agreement_details(agreement_id)
                
                # Replicate Club OS invoice data call  
                invoice_data = self._get_member_invoices(member_id, agreement_id)
                
                # Replicate Club OS scheduled payments call
                scheduled_payments = self._get_scheduled_payments(member_id, agreement_id)
                
                # Combine data like Club OS does
                package_data[agreement_id] = {
                    'agreement_details': agreement_details,
                    'invoices': invoice_data,
                    'scheduled_payments': scheduled_payments,
                    'member_id': member_id,
                    'agreement_id': agreement_id
                }
                
            return {
                "success": True,
                "member_id": member_id,
                "package_data": package_data,
                "total_agreements": len(agreement_ids)
            }
            
        except Exception as e:
            print(f"❌ Error in data replication: {e}")
            return {"error": str(e), "success": False}
    
    def _find_member_data(self, member_identifier):
        """Find member using various approaches like Club OS"""
        
        try:
            # Method 1: Direct member ID lookup
            if str(member_identifier).isdigit():
                print(f"🔍 Trying direct member ID lookup: {member_identifier}")
                
                # Delegate to member for data access
                if self.api.delegate_to_member(member_identifier):
                    # Try to get agreement IDs for this member
                    payment_details = self.api.get_member_training_payment_details(member_identifier)
                    if payment_details and payment_details.get('success'):
                        return {
                            'member_id': member_identifier,
                            'agreement_ids': payment_details.get('agreement_ids', [])
                        }
            
            # Method 2: Name-based search (if member_identifier is a name)
            if not str(member_identifier).isdigit():
                print(f"🔍 Trying name-based member search: {member_identifier}")
                # This would require implementing a member search API call
                # For now, return None to indicate need for manual member ID
                
            return None
            
        except Exception as e:
            print(f"❌ Error finding member data: {e}")
            return None
    
    def _get_agreement_details(self, agreement_id):
        """Get agreement details using Club OS V2 API endpoint"""
        
        try:
            print(f"📋 Fetching agreement details for ID: {agreement_id}")
            
            # Use the working V2 endpoint with includes (like Club OS)
            complete_data = self.api.get_complete_agreement_data(agreement_id)
            
            if complete_data and complete_data.get('v2_data'):
                v2_data = complete_data['v2_data']
                
                # Extract key agreement info (like Club OS displays)
                agreement_info = {
                    'name': v2_data.get('name', 'Unknown Package'),
                    'status': v2_data.get('agreementStatus', 'Unknown'),
                    'start_date': v2_data.get('startDate'),
                    'end_date': v2_data.get('endDate'),
                    'full_agreement_value': v2_data.get('fullAgreementValue', 0),
                    'billing_duration': v2_data.get('billingDuration'),
                    'duration_type': v2_data.get('durationType'),
                    'member_services': v2_data.get('packageAgreementMemberServices', [])
                }
                
                print(f"✅ Agreement details retrieved: {agreement_info['name']}")
                return agreement_info
                
            else:
                print(f"⚠️ No V2 data returned for agreement {agreement_id}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting agreement details: {e}")
            return None
    
    def _get_member_invoices(self, member_id, agreement_id):
        """Get invoice data (replicate Club OS invoice retrieval)"""
        
        try:
            print(f"💰 Fetching invoices for member {member_id}, agreement {agreement_id}")
            
            # Use the complete agreement data which includes invoices
            complete_data = self.api.get_complete_agreement_data(agreement_id)
            
            if complete_data and complete_data.get('v2_data'):
                invoices = complete_data['v2_data'].get('invoices', [])
                
                # Process invoices like Club OS
                processed_invoices = []
                for invoice in invoices:
                    processed_invoices.append({
                        'id': invoice.get('id'),
                        'billing_date': invoice.get('billingDate'),
                        'total': invoice.get('total', 0),
                        'status': invoice.get('invoiceStatus'),
                        'type': invoice.get('invoiceType'),
                        'line_items': invoice.get('lineItems', [])
                    })
                
                print(f"✅ Found {len(processed_invoices)} invoices")
                return processed_invoices
                
            return []
            
        except Exception as e:
            print(f"❌ Error getting invoices: {e}")
            return []
    
    def _get_scheduled_payments(self, member_id, agreement_id):
        """Get scheduled payments (replicate Club OS payment schedule)"""
        
        try:
            print(f"📅 Fetching scheduled payments for member {member_id}, agreement {agreement_id}")
            
            # Use the complete agreement data which includes scheduled payments
            complete_data = self.api.get_complete_agreement_data(agreement_id)
            
            if complete_data and complete_data.get('v2_data'):
                scheduled_payments = complete_data['v2_data'].get('scheduledPayments', [])
                
                # Process scheduled payments like Club OS
                processed_payments = []
                for payment in scheduled_payments:
                    processed_payments.append({
                        'billing_date': payment.get('billingDate'),
                        'total': payment.get('total', 0),
                        'status': payment.get('invoiceStatus'),
                        'line_items': payment.get('lineItems', [])
                    })
                
                print(f"✅ Found {len(processed_payments)} scheduled payments")
                return processed_payments
                
            return []
            
        except Exception as e:
            print(f"❌ Error getting scheduled payments: {e}")
            return []

def test_replicator():
    """Test the Club OS data replicator"""
    
    print("🧪 Testing Club OS Training Package Data Replicator")
    print("=" * 60)
    
    replicator = ClubOSDataReplicator()
    
    # Test with known working member IDs
    test_members = [
        "191215290",  # Alexander - known to have agreement data
        "125814462",  # Mark Benzinger - known to have packages
    ]
    
    for member_id in test_members:
        print(f"\n🎯 Testing with member ID: {member_id}")
        print("-" * 40)
        
        result = replicator.get_member_training_packages(member_id)
        
        if result.get('success'):
            print(f"✅ SUCCESS! Found {result['total_agreements']} training agreements")
            
            for agreement_id, package_data in result['package_data'].items():
                agreement_details = package_data['agreement_details']
                invoices = package_data['invoices']
                scheduled_payments = package_data['scheduled_payments']
                
                if agreement_details:
                    print(f"  📦 Package: {agreement_details['name']}")
                    print(f"  💰 Value: ${agreement_details['full_agreement_value']}")
                    print(f"  📅 Start: {agreement_details['start_date']}")
                    print(f"  📊 Invoices: {len(invoices)}")
                    print(f"  📅 Scheduled: {len(scheduled_payments)}")
                else:
                    print(f"  ⚠️ Agreement {agreement_id}: No details available")
                    
        else:
            print(f"❌ FAILED: {result.get('error')}")
    
    print("\n🏁 Replicator testing complete")

if __name__ == "__main__":
    test_replicator()
