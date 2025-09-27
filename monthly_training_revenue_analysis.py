#!/usr/bin/env python3
"""
Enhanced Monthly Training Revenue Analysis

This script calculates actual monthly revenue from successful training package payments
using the enhanced invoice data that includes paid invoices with payment dates.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_monthly_revenue():
    """Calculate actual monthly revenue from paid training invoices"""
    print("\n" + "="*80)
    print("💰 MONTHLY TRAINING PACKAGE REVENUE ANALYSIS")
    print("="*80)
    
    conn = sqlite3.connect('gym_bot.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all training clients with package details
    cursor.execute("""
        SELECT 
            member_name, 
            package_details, 
            past_due_amount, 
            total_past_due,
            payment_status,
            last_updated
        FROM training_clients 
        WHERE package_details IS NOT NULL 
        AND package_details != '' 
        AND package_details != '[]'
        ORDER BY member_name
    """)
    
    clients = cursor.fetchall()
    
    print(f"\n📊 Analyzing {len(clients)} training clients for monthly revenue...")
    
    # Monthly revenue tracking
    monthly_revenue = defaultdict(float)
    monthly_payment_counts = defaultdict(int)
    payment_methods = Counter()
    package_types = Counter()
    
    # Detailed payment tracking
    all_payments = []
    clients_with_payments = []
    clients_without_payment_dates = []
    
    total_paid_amount = 0.0
    total_paid_invoices = 0
    total_unpaid_amount = 0.0
    
    for client in clients:
        try:
            details = json.loads(client['package_details'])
            client_name = client['member_name']
            client_payments = []
            
            if isinstance(details, list):
                for package in details:
                    agreement_id = package.get('agreement_id')
                    package_name = package.get('package_name', 'Unknown Package')
                    
                    # Count package types
                    package_types[package_name] += 1
                    
                    # Get billing status with paid invoices
                    billing_status = package.get('billing_status', {})
                    paid_invoices = billing_status.get('paid', [])
                    
                    if paid_invoices:
                        print(f"\n👤 {client_name} - {package_name}")
                        print(f"   📦 Agreement ID: {agreement_id}")
                        print(f"   💳 Paid Invoices: {len(paid_invoices)}")
                        
                        for payment in paid_invoices:
                            amount = float(payment.get('amount', 0))
                            payment_month = payment.get('payment_month')
                            paid_date = payment.get('paid_date') or payment.get('invoice_date')
                            invoice_id = payment.get('id', 'unknown')
                            
                            total_paid_amount += amount
                            total_paid_invoices += 1
                            
                            if payment_month:
                                monthly_revenue[payment_month] += amount
                                monthly_payment_counts[payment_month] += 1
                                
                                print(f"       💰 ${amount:,.2f} in {payment_month}")
                                
                                # Store payment details
                                payment_record = {
                                    'client': client_name,
                                    'package': package_name,
                                    'amount': amount,
                                    'month': payment_month,
                                    'paid_date': paid_date,
                                    'invoice_id': invoice_id,
                                    'agreement_id': agreement_id
                                }
                                all_payments.append(payment_record)
                                client_payments.append(payment_record)
                            else:
                                print(f"       ⚠️ ${amount:,.2f} - No payment month available")
                                clients_without_payment_dates.append({
                                    'client': client_name,
                                    'package': package_name,
                                    'amount': amount,
                                    'paid_date': paid_date,
                                    'invoice_id': invoice_id
                                })
                    
                    # Track unpaid amounts
                    unpaid_invoices = billing_status.get('current', []) + billing_status.get('past', [])
                    for unpaid in unpaid_invoices:
                        total_unpaid_amount += float(unpaid.get('amount', 0))
            
            if client_payments:
                clients_with_payments.append({
                    'client': client_name,
                    'payments': client_payments,
                    'total_paid': sum(p['amount'] for p in client_payments)
                })
                        
        except json.JSONDecodeError:
            print(f"⚠️ JSON decode error for {client['member_name']}")
        except Exception as e:
            print(f"⚠️ Error analyzing {client['member_name']}: {e}")
    
    conn.close()
    
    # Generate monthly revenue report
    print(f"\n📊 MONTHLY REVENUE SUMMARY:")
    print("=" * 60)
    
    if monthly_revenue:
        sorted_months = sorted(monthly_revenue.keys())
        
        print(f"{'Month':<10} {'Revenue':<12} {'Payments':<10} {'Avg Payment':<12}")
        print("-" * 50)
        
        total_revenue = 0
        total_payments = 0
        
        for month in sorted_months:
            revenue = monthly_revenue[month]
            payment_count = monthly_payment_counts[month]
            avg_payment = revenue / payment_count if payment_count > 0 else 0
            
            total_revenue += revenue
            total_payments += payment_count
            
            print(f"{month:<10} ${revenue:<11,.2f} {payment_count:<10} ${avg_payment:<11,.2f}")
        
        print("-" * 50)
        print(f"{'TOTAL':<10} ${total_revenue:<11,.2f} {total_payments:<10} ${total_revenue/total_payments if total_payments > 0 else 0:<11,.2f}")
        
        # Show highest revenue months
        top_months = sorted(monthly_revenue.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"\n🏆 TOP REVENUE MONTHS:")
        for month, revenue in top_months:
            print(f"   {month}: ${revenue:,.2f} ({monthly_payment_counts[month]} payments)")
    else:
        print("❌ No monthly revenue data available!")
        print("   This indicates that paid invoice data is still not being captured with payment dates.")
    
    # Summary statistics
    print(f"\n💎 FINANCIAL SUMMARY:")
    print("=" * 40)
    print(f"   Total Paid Amount: ${total_paid_amount:,.2f}")
    print(f"   Total Paid Invoices: {total_paid_invoices}")
    print(f"   Total Unpaid Amount: ${total_unpaid_amount:,.2f}")
    print(f"   Clients with Payments: {len(clients_with_payments)}")
    print(f"   Clients with Missing Payment Dates: {len(clients_without_payment_dates)}")
    
    # Package type analysis
    if package_types:
        print(f"\n📦 PACKAGE TYPE REVENUE:")
        package_revenue = defaultdict(float)
        for payment in all_payments:
            package_revenue[payment['package']] += payment['amount']
        
        for package_name, revenue in sorted(package_revenue.items(), key=lambda x: x[1], reverse=True):
            count = package_types[package_name]
            avg_per_package = revenue / count if count > 0 else 0
            print(f"   {package_name}: ${revenue:,.2f} ({count} packages, avg: ${avg_per_package:,.2f})")
    
    return {
        'monthly_revenue': dict(monthly_revenue),
        'total_revenue': total_paid_amount,
        'total_payments': total_paid_invoices,
        'clients_with_payments': len(clients_with_payments),
        'payment_details': all_payments
    }

def generate_revenue_forecast():
    """Generate revenue forecast based on scheduled payments and trends"""
    print(f"\n🔮 REVENUE FORECASTING:")
    print("=" * 40)
    
    # This would require scheduled payment data which we need to capture
    print("   Revenue forecasting requires scheduled payment data.")
    print("   This will be available after the next training client sync.")

def main():
    """Main revenue analysis function"""
    print("💰 ENHANCED TRAINING REVENUE ANALYSIS")
    print("=" * 80)
    
    # Calculate monthly revenue from paid invoices
    revenue_data = calculate_monthly_revenue()
    
    # Generate forecast
    generate_revenue_forecast()
    
    if revenue_data['total_payments'] > 0:
        print(f"\n✅ ANALYSIS COMPLETE")
        print(f"   Found revenue data for {revenue_data['clients_with_payments']} clients")
        print(f"   Total revenue tracked: ${revenue_data['total_revenue']:,.2f}")
        print(f"   Ready for monthly revenue reporting!")
    else:
        print(f"\n⚠️  NO PAYMENT DATA FOUND")
        print(f"   The enhanced ClubOS integration needs to be re-run to capture paid invoice data.")
        print(f"   Please refresh the training client data to populate payment information.")

if __name__ == "__main__":
    main()