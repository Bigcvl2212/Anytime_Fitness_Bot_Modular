"""
Square Invoice Service
Handles invoice management directly via Square API without database storage
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sys
import os

# Import secure secrets manager
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'authentication'))
from secure_secrets_manager import SecureSecretsManager

logger = logging.getLogger(__name__)

class SquareInvoiceService:
    """Service for managing Square invoices directly via API"""

    def __init__(self):
        self.client = None
        self.location_id = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Square client and location ID"""
        try:
            from square.client import Client
            
            # Get credentials from SecureSecretsManager
            secrets_manager = SecureSecretsManager()
            access_token = secrets_manager.get_secret("square-production-access-token")
            self.location_id = secrets_manager.get_secret("square-production-location-id")
            
            if not access_token:
                raise ValueError("Square production access token not found in SecureSecretsManager")
            
            if not self.location_id:
                raise ValueError("Square production location ID not found in SecureSecretsManager")
            
            # Configure the Square client for production environment
            self.client = Client(access_token=access_token)
            logger.info("✅ Square Invoice Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing Square Invoice Service: {e}")
            self.client = None

    def get_all_invoices(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all invoices from Square API with customer details"""
        try:
            if not self.client:
                logger.error("❌ Square client not initialized")
                return []

            # Get invoices from Square API
            result = self.client.invoices.list_invoices(
                location_id=self.location_id,
                limit=limit
            )

            if result.is_success():
                invoices = result.body.get('invoices', [])
                
                # Enhance invoices with customer details
                enhanced_invoices = []
                for invoice in invoices:
                    enhanced_invoice = invoice.copy()
                    
                    # Get customer details if available
                    primary_recipient = invoice.get('primary_recipient', {})
                    customer_id = primary_recipient.get('customer_id')
                    
                    if customer_id:
                        try:
                            customer_result = self.client.customers.retrieve_customer(customer_id=customer_id)
                            if customer_result.is_success():
                                customer = customer_result.body.get('customer', {})
                                enhanced_invoice['customer_details'] = {
                                    'id': customer.get('id'),
                                    'given_name': customer.get('given_name'),
                                    'family_name': customer.get('family_name'),
                                    'email_address': customer.get('email_address'),
                                    'phone_number': customer.get('phone_number')
                                }
                        except Exception as e:
                            logger.warning(f"⚠️ Could not retrieve customer details for {customer_id}: {e}")
                            enhanced_invoice['customer_details'] = {
                                'id': customer_id,
                                'given_name': 'Customer',
                                'family_name': '',
                                'email_address': '',
                                'phone_number': ''
                            }
                    else:
                        enhanced_invoice['customer_details'] = {
                            'id': None,
                            'given_name': 'Unknown',
                            'family_name': '',
                            'email_address': '',
                            'phone_number': ''
                        }
                    
                    enhanced_invoices.append(enhanced_invoice)
                
                logger.info(f"📊 Retrieved {len(enhanced_invoices)} invoices from Square API with customer details")
                return enhanced_invoices
            else:
                error_details = result.errors if result.errors else 'Unknown error'
                logger.error(f"❌ Square API error getting invoices: {error_details}")
                return []

        except Exception as e:
            logger.error(f"❌ Error getting invoices from Square API: {e}")
            return []

    def get_invoice_by_id(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific invoice by ID from Square API"""
        try:
            if not self.client:
                logger.error("❌ Square client not initialized")
                return None

            result = self.client.invoices.get_invoice(invoice_id=invoice_id)

            if result.is_success():
                invoice = result.body.get('invoice', {})
                logger.info(f"📊 Retrieved invoice {invoice_id} from Square API")
                return invoice
            else:
                error_details = result.errors if result.errors else 'Unknown error'
                logger.error(f"❌ Square API error getting invoice {invoice_id}: {error_details}")
                return None

        except Exception as e:
            logger.error(f"❌ Error getting invoice {invoice_id} from Square API: {e}")
            return None

    def get_invoices_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get invoices for a specific customer"""
        try:
            if not self.client:
                logger.error("❌ Square client not initialized")
                return []

            # Get all invoices and filter by customer
            all_invoices = self.get_all_invoices(limit=500)  # Get more to ensure we find customer invoices
            
            customer_invoices = []
            for invoice in all_invoices:
                primary_recipient = invoice.get('primary_recipient', {})
                if primary_recipient.get('customer_id') == customer_id:
                    customer_invoices.append(invoice)

            logger.info(f"📊 Found {len(customer_invoices)} invoices for customer {customer_id}")
            return customer_invoices

        except Exception as e:
            logger.error(f"❌ Error getting invoices for customer {customer_id}: {e}")
            return []

    def get_payment_summary(self) -> Dict[str, Any]:
        """Get payment summary from Square API"""
        try:
            all_invoices = self.get_all_invoices(limit=500)
            
            summary = {
                'total_invoices': len(all_invoices),
                'paid_invoices': 0,
                'unpaid_invoices': 0,
                'pending_invoices': 0,
                'total_revenue': 0.0,
                'outstanding_amount': 0.0,
                'last_checked': datetime.now().isoformat()
            }

            for invoice in all_invoices:
                invoice_status = invoice.get('invoice_status', 'UNPAID')
                payment_requests = invoice.get('payment_requests', [])
                
                # Calculate amounts
                total_amount = 0.0
                paid_amount = 0.0
                
                for payment_request in payment_requests:
                    computed_amount = payment_request.get('computed_amount_money', {})
                    total_completed = payment_request.get('total_completed_amount_money', {})
                    
                    if computed_amount:
                        total_amount += computed_amount.get('amount', 0) / 100  # Convert from cents
                    
                    if total_completed:
                        paid_amount += total_completed.get('amount', 0) / 100  # Convert from cents

                # Categorize invoice
                if invoice_status == 'PAID':
                    summary['paid_invoices'] += 1
                    summary['total_revenue'] += paid_amount
                elif invoice_status == 'UNPAID':
                    summary['unpaid_invoices'] += 1
                    summary['outstanding_amount'] += total_amount
                elif invoice_status in ['DRAFT', 'PARTIALLY_PAID']:
                    summary['pending_invoices'] += 1
                    summary['outstanding_amount'] += (total_amount - paid_amount)

            return summary

        except Exception as e:
            logger.error(f"❌ Error getting payment summary: {e}")
            return {
                'error': str(e),
                'total_invoices': 0,
                'paid_invoices': 0,
                'unpaid_invoices': 0,
                'pending_invoices': 0,
                'total_revenue': 0.0,
                'outstanding_amount': 0.0
            }

    def check_payment_status(self, invoice_id: str) -> Dict[str, Any]:
        """Check payment status of a specific invoice"""
        try:
            invoice = self.get_invoice_by_id(invoice_id)
            if not invoice:
                return {
                    'success': False,
                    'error': f'Invoice {invoice_id} not found'
                }

            invoice_status = invoice.get('invoice_status', 'UNPAID')
            payment_requests = invoice.get('payment_requests', [])
            
            is_paid = invoice_status == 'PAID'
            payment_id = None
            paid_amount = 0.0

            for payment_request in payment_requests:
                total_completed = payment_request.get('total_completed_amount_money', {})
                if total_completed and total_completed.get('amount', 0) > 0:
                    is_paid = True
                    paid_amount = total_completed.get('amount', 0) / 100  # Convert from cents
                    
                    # Get payment ID if available
                    tenders = payment_request.get('tenders', [])
                    if tenders:
                        payment_id = tenders[0].get('id')
                    break

            return {
                'success': True,
                'is_paid': is_paid,
                'payment_status': 'PAID' if is_paid else 'UNPAID',
                'payment_id': payment_id,
                'paid_amount': paid_amount,
                'invoice_status': invoice_status,
                'updated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error checking payment status for invoice {invoice_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def check_all_unpaid_invoices(self) -> Dict[str, Any]:
        """Check payment status for all unpaid invoices"""
        try:
            all_invoices = self.get_all_invoices(limit=500)
            unpaid_invoices = [inv for inv in all_invoices if inv.get('invoice_status') == 'UNPAID']

            logger.info(f"🔍 Checking payment status for {len(unpaid_invoices)} unpaid invoices")

            results = {
                'total_checked': 0,
                'newly_paid': 0,
                'still_unpaid': 0,
                'errors': 0,
                'updated_invoices': [],
                'auto_unlocked_members': []
            }

            for invoice in unpaid_invoices:
                invoice_id = invoice.get('id')
                if not invoice_id:
                    continue

                results['total_checked'] += 1

                # Check payment status
                payment_status = self.check_payment_status(invoice_id)

                if payment_status.get('success'):
                    if payment_status.get('is_paid'):
                        results['newly_paid'] += 1
                        
                        # Get customer info for auto-unlock
                        primary_recipient = invoice.get('primary_recipient', {})
                        customer_id = primary_recipient.get('customer_id')
                        
                        results['updated_invoices'].append({
                            'invoice_id': invoice_id,
                            'customer_id': customer_id,
                            'amount': payment_status.get('paid_amount', 0),
                            'payment_id': payment_status.get('payment_id')
                        })

                        # Auto-unlock member if customer_id is available
                        if customer_id:
                            unlock_result = self._auto_unlock_member(customer_id, invoice_id)
                            if unlock_result:
                                results['auto_unlocked_members'].append({
                                    'customer_id': customer_id,
                                    'invoice_id': invoice_id
                                })

                        logger.info(f"✅ Invoice {invoice_id} marked as paid")
                    else:
                        results['still_unpaid'] += 1
                else:
                    results['errors'] += 1
                    logger.error(f"❌ Failed to check payment status for invoice {invoice_id}")

            logger.info(f"📊 Payment status check complete: {results['newly_paid']} newly paid, {results['still_unpaid']} still unpaid, {results['errors']} errors")
            return results

        except Exception as e:
            logger.error(f"❌ Error in check_all_unpaid_invoices: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _auto_unlock_member(self, customer_id: str, invoice_id: str) -> bool:
        """Auto-unlock member access when invoice is paid"""
        try:
            # Import access monitor
            from ..automated_access_monitor import AutomatedAccessMonitor
            from ..database_manager import DatabaseManager
            
            db_manager = DatabaseManager()
            access_monitor = AutomatedAccessMonitor(db_manager)

            # Unlock member access
            success = access_monitor.unlock_member_access(
                member_id=customer_id,
                reason=f'Invoice payment received - Invoice ID: {invoice_id}'
            )

            if success:
                logger.info(f"🔓 Auto-unlocked member {customer_id} due to invoice payment: {invoice_id}")
                return True
            else:
                logger.warning(f"⚠️ Failed to auto-unlock member {customer_id} for invoice {invoice_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Error auto-unlocking member {customer_id}: {e}")
            return False

    def get_invoice_details(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed invoice information including customer and payment details"""
        try:
            invoice = self.get_invoice_by_id(invoice_id)
            if not invoice:
                return None

            # Get customer details if available
            customer_info = {}
            primary_recipient = invoice.get('primary_recipient', {})
            customer_id = primary_recipient.get('customer_id')
            
            if customer_id and self.client:
                try:
                    customer_result = self.client.customers.retrieve_customer(customer_id=customer_id)
                    if customer_result.is_success():
                        customer = customer_result.body.get('customer', {})
                        customer_info = {
                            'id': customer.get('id'),
                            'given_name': customer.get('given_name'),
                            'family_name': customer.get('family_name'),
                            'email_address': customer.get('email_address'),
                            'phone_number': customer.get('phone_number')
                        }
                except Exception as e:
                    logger.warning(f"⚠️ Could not retrieve customer details for {customer_id}: {e}")

            # Format invoice details
            details = {
                'invoice_id': invoice.get('id'),
                'invoice_status': invoice.get('invoice_status'),
                'created_at': invoice.get('created_at'),
                'updated_at': invoice.get('updated_at'),
                'customer_info': customer_info,
                'payment_requests': invoice.get('payment_requests', []),
                'total_amount': 0.0,
                'paid_amount': 0.0,
                'outstanding_amount': 0.0
            }

            # Calculate amounts
            for payment_request in invoice.get('payment_requests', []):
                computed_amount = payment_request.get('computed_amount_money', {})
                total_completed = payment_request.get('total_completed_amount_money', {})
                
                if computed_amount:
                    details['total_amount'] += computed_amount.get('amount', 0) / 100
                
                if total_completed:
                    details['paid_amount'] += total_completed.get('amount', 0) / 100

            details['outstanding_amount'] = details['total_amount'] - details['paid_amount']

            return details

        except Exception as e:
            logger.error(f"❌ Error getting invoice details for {invoice_id}: {e}")
            return None
