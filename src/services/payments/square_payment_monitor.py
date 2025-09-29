"""
Square Payment Monitor Service
Monitors invoice payment status and handles auto-unlock functionality
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SquarePaymentMonitor:
    """Monitor Square invoice payments and handle auto-unlock"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_square_client(self):
        """Get Square client for API calls"""
        try:
            from .square_client_simple import get_square_client
            return get_square_client()
        except Exception as e:
            logger.error(f"❌ Error getting Square client: {e}")
            return None

    def check_invoice_payment_status(self, square_invoice_id: str) -> Optional[Dict[str, Any]]:
        """Check payment status of a specific invoice via Square API"""
        try:
            client = self.get_square_client()
            if not client:
                return None

            # Get invoice details from Square API
            result = client.invoices.get_invoice(invoice_id=square_invoice_id)

            if result.is_success():
                invoice = result.body.get('invoice', {})
                payment_requests = invoice.get('payment_requests', [])

                # Check if any payment request is completed
                is_paid = False
                payment_id = None
                paid_amount = 0

                for payment_request in payment_requests:
                    computed_amount_money = payment_request.get('computed_amount_money', {})
                    total_completed_amount_money = payment_request.get('total_completed_amount_money', {})

                    if total_completed_amount_money and total_completed_amount_money.get('amount', 0) > 0:
                        is_paid = True
                        paid_amount = total_completed_amount_money.get('amount', 0) / 100  # Convert from cents
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
                    'invoice_status': invoice.get('invoice_status'),
                    'updated_at': datetime.now().isoformat()
                }
            else:
                error_details = result.errors if result.errors else 'Unknown error'
                logger.error(f"❌ Square API error for invoice {square_invoice_id}: {error_details}")
                return {
                    'success': False,
                    'error': str(error_details)
                }

        except Exception as e:
            logger.error(f"❌ Error checking invoice payment status: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def check_all_unpaid_invoices(self) -> Dict[str, Any]:
        """Check payment status for all unpaid invoices"""
        try:
            # Get all unpaid invoices from database
            all_invoices = self.db_manager.get_all_invoices()
            unpaid_invoices = [inv for inv in all_invoices if inv.get('payment_status') == 'UNPAID']

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
                square_invoice_id = invoice.get('square_invoice_id')
                if not square_invoice_id:
                    continue

                results['total_checked'] += 1

                # Add small delay to avoid rate limiting
                time.sleep(0.5)

                # Check payment status via Square API
                payment_status = self.check_invoice_payment_status(square_invoice_id)

                if payment_status and payment_status.get('success'):
                    if payment_status.get('is_paid'):
                        # Invoice has been paid - update database
                        success = self.db_manager.update_invoice_payment_status(
                            square_invoice_id=square_invoice_id,
                            payment_status='PAID',
                            payment_id=payment_status.get('payment_id'),
                            paid_at=payment_status.get('updated_at')
                        )

                        if success:
                            results['newly_paid'] += 1
                            results['updated_invoices'].append({
                                'invoice_id': square_invoice_id,
                                'member_id': invoice.get('member_id'),
                                'amount': invoice.get('amount'),
                                'member_name': f"{invoice.get('first_name', '')} {invoice.get('last_name', '')}"
                            })

                            # Auto-unlock member
                            member_id = invoice.get('member_id')
                            if member_id:
                                unlock_result = self.auto_unlock_member(member_id, square_invoice_id)
                                if unlock_result:
                                    results['auto_unlocked_members'].append({
                                        'member_id': member_id,
                                        'member_name': f"{invoice.get('first_name', '')} {invoice.get('last_name', '')}"
                                    })

                            logger.info(f"✅ Invoice {square_invoice_id} marked as paid and member auto-unlocked")
                        else:
                            results['errors'] += 1
                            logger.error(f"❌ Failed to update payment status for invoice {square_invoice_id}")
                    else:
                        results['still_unpaid'] += 1
                else:
                    results['errors'] += 1
                    logger.error(f"❌ Failed to check payment status for invoice {square_invoice_id}")

            logger.info(f"📊 Payment status check complete: {results['newly_paid']} newly paid, {results['still_unpaid']} still unpaid, {results['errors']} errors")
            return results

        except Exception as e:
            logger.error(f"❌ Error in check_all_unpaid_invoices: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def auto_unlock_member(self, member_id: str, invoice_id: str) -> bool:
        """Auto-unlock member access when invoice is paid"""
        try:
            # Import access monitor
            from ..automated_access_monitor import AutomatedAccessMonitor
            access_monitor = AutomatedAccessMonitor(self.db_manager)

            # Unlock member access
            success = access_monitor.unlock_member_access(
                member_id=member_id,
                reason=f'Invoice payment received - Invoice ID: {invoice_id}'
            )

            if success:
                logger.info(f"🔓 Auto-unlocked member {member_id} due to invoice payment: {invoice_id}")
                return True
            else:
                logger.warning(f"⚠️ Failed to auto-unlock member {member_id} for invoice {invoice_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Error auto-unlocking member {member_id}: {e}")
            return False

    def get_payment_summary(self) -> Dict[str, Any]:
        """Get summary of invoice payments"""
        try:
            all_invoices = self.db_manager.get_all_invoices()

            summary = {
                'total_invoices': len(all_invoices),
                'paid_invoices': len([inv for inv in all_invoices if inv.get('payment_status') == 'PAID']),
                'unpaid_invoices': len([inv for inv in all_invoices if inv.get('payment_status') == 'UNPAID']),
                'pending_invoices': len([inv for inv in all_invoices if inv.get('payment_status') == 'PENDING']),
                'total_revenue': sum(inv.get('amount', 0) for inv in all_invoices if inv.get('payment_status') == 'PAID'),
                'outstanding_amount': sum(inv.get('amount', 0) for inv in all_invoices if inv.get('payment_status') == 'UNPAID'),
                'last_checked': datetime.now().isoformat()
            }

            return summary

        except Exception as e:
            logger.error(f"❌ Error getting payment summary: {e}")
            return {
                'error': str(e)
            }