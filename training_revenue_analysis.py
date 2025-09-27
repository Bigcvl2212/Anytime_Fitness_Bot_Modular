#!/usr/bin/env python3
"""
Training Revenue Analysis Tool
Calculates monthly revenue from training package payments
"""
import sqlite3
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any
import calendar

def examine_training_data():
    """Examine sample training client data"""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    # Get sample data
    cursor.execute('''
        SELECT full_name, package_details, financial_summary, 
               past_due_amount, total_past_due, payment_status, 
               active_packages, package_summary
        FROM training_clients 
        WHERE package_details IS NOT NULL
        LIMIT 5
    ''')
    
    rows = cursor.fetchall()
    print("🔍 SAMPLE TRAINING CLIENT DATA")
    print("=" * 80)
    
    for row in rows:
        name, pkg_details, financial, past_due, total_past_due, status, active_pkg, pkg_summary = row
        print(f"👤 Name: {name}")
        print(f"💰 Financial Summary: {financial}")
        print(f"📦 Package Summary: {pkg_summary}")
        print(f"💳 Payment Status: {status}")
        print(f"💸 Past Due Amount: ${past_due}")
        
        if pkg_details:
            try:
                # Try to parse package details JSON
                details = json.loads(pkg_details)
                if isinstance(details, list) and details:
                    first_package = details[0]
                    print(f"📋 Package Details Sample:")
                    for key, value in first_package.items():
                        if key in ['packageName', 'totalValue', 'paidAmount', 'remainingBalance', 'sessions', 'created', 'modified']:
                            print(f"   {key}: {value}")
            except:
                print(f"📋 Raw Package Details: {pkg_details[:100]}...")
        
        print("-" * 40)
    
    conn.close()

def analyze_revenue_structure():
    """Analyze the revenue structure from training packages"""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    # Get all training clients with package data
    cursor.execute('''
        SELECT full_name, package_details, active_packages, 
               past_due_amount, total_past_due, created_at, updated_at
        FROM training_clients 
        WHERE package_details IS NOT NULL
    ''')
    
    rows = cursor.fetchall()
    
    total_package_value = 0
    total_paid_amount = 0
    total_outstanding = 0
    monthly_revenue = defaultdict(float)
    payment_methods = defaultdict(int)
    package_types = defaultdict(int)
    
    print(f"\n💰 TRAINING REVENUE ANALYSIS")
    print("=" * 80)
    print(f"📊 Total Training Clients with Packages: {len(rows)}")
    
    for row in rows:
        name, pkg_details, active_pkg, past_due, total_past_due, created, updated = row
        
        if pkg_details:
            try:
                details = json.loads(pkg_details)
                if isinstance(details, list):
                    for package in details:
                        # Extract financial data
                        total_value = float(package.get('totalValue', 0))
                        paid_amount = float(package.get('paidAmount', 0))
                        remaining = float(package.get('remainingBalance', 0))
                        
                        total_package_value += total_value
                        total_paid_amount += paid_amount
                        total_outstanding += remaining
                        
                        # Package type analysis
                        pkg_name = package.get('packageName', 'Unknown')
                        package_types[pkg_name] += 1
                        
                        # Try to extract date information for monthly analysis
                        created_date = package.get('created') or package.get('modified')
                        if created_date:
                            try:
                                # Parse various date formats
                                if 'T' in str(created_date):
                                    date_obj = datetime.fromisoformat(str(created_date).replace('Z', ''))
                                else:
                                    date_obj = datetime.strptime(str(created_date), '%Y-%m-%d')
                                
                                month_key = f"{date_obj.year}-{date_obj.month:02d}"
                                monthly_revenue[month_key] += paid_amount
                            except:
                                pass
            except Exception as e:
                print(f"   ⚠️ Error parsing package for {name}: {e}")
        
        # Add past due amounts to outstanding
        if past_due:
            total_outstanding += float(past_due)
    
    # Display results
    print(f"\n💵 FINANCIAL SUMMARY:")
    print(f"   Total Package Value: ${total_package_value:,.2f}")
    print(f"   Total Paid Amount: ${total_paid_amount:,.2f}")
    print(f"   Total Outstanding: ${total_outstanding:,.2f}")
    print(f"   Collection Rate: {(total_paid_amount/total_package_value*100) if total_package_value > 0 else 0:.1f}%")
    
    print(f"\n📅 MONTHLY REVENUE:")
    if monthly_revenue:
        sorted_months = sorted(monthly_revenue.keys())
        for month in sorted_months:
            year, month_num = month.split('-')
            month_name = calendar.month_name[int(month_num)]
            print(f"   {month_name} {year}: ${monthly_revenue[month]:,.2f}")
        
        print(f"\n   📈 Average Monthly Revenue: ${sum(monthly_revenue.values())/len(monthly_revenue):,.2f}")
    else:
        print("   ⚠️ No monthly data available - using aggregate analysis")
    
    print(f"\n📦 PACKAGE TYPES:")
    sorted_packages = sorted(package_types.items(), key=lambda x: x[1], reverse=True)
    for pkg_name, count in sorted_packages[:10]:  # Top 10
        print(f"   {pkg_name}: {count} clients")
    
    conn.close()
    
    return {
        'total_package_value': total_package_value,
        'total_paid_amount': total_paid_amount,
        'total_outstanding': total_outstanding,
        'monthly_revenue': dict(monthly_revenue),
        'package_types': dict(package_types)
    }

def generate_revenue_report():
    """Generate a comprehensive training revenue report"""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    print(f"\n📋 COMPREHENSIVE TRAINING REVENUE REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Current revenue status
    cursor.execute('''
        SELECT 
            COUNT(*) as total_clients,
            COUNT(CASE WHEN payment_status = 'Current' THEN 1 END) as current_clients,
            COUNT(CASE WHEN payment_status = 'Past Due' THEN 1 END) as past_due_clients,
            SUM(past_due_amount) as total_past_due,
            AVG(past_due_amount) as avg_past_due
        FROM training_clients
        WHERE past_due_amount IS NOT NULL
    ''')
    
    stats = cursor.fetchone()
    total_clients, current_clients, past_due_clients, total_past_due, avg_past_due = stats
    
    print(f"\n🎯 CLIENT STATUS OVERVIEW:")
    print(f"   Total Training Clients: {total_clients}")
    print(f"   Current Payments: {current_clients}")
    print(f"   Past Due Clients: {past_due_clients}")
    print(f"   Total Past Due Amount: ${total_past_due or 0:,.2f}")
    print(f"   Average Past Due: ${avg_past_due or 0:,.2f}")
    
    # Revenue by trainer analysis
    cursor.execute('''
        SELECT trainer_name, COUNT(*) as client_count,
               SUM(CASE WHEN past_due_amount > 0 THEN past_due_amount ELSE 0 END) as trainer_past_due
        FROM training_clients 
        WHERE trainer_name IS NOT NULL
        GROUP BY trainer_name
        ORDER BY client_count DESC
    ''')
    
    trainer_stats = cursor.fetchall()
    if trainer_stats:
        print(f"\n👨‍💼 REVENUE BY TRAINER:")
        for trainer, client_count, past_due in trainer_stats:
            print(f"   {trainer}: {client_count} clients, ${past_due or 0:,.2f} past due")
    
    conn.close()

if __name__ == "__main__":
    examine_training_data()
    revenue_data = analyze_revenue_structure()
    generate_revenue_report()
    
    print(f"\n✅ Training revenue analysis complete!")
    print(f"💡 For detailed monthly breakdowns, ensure package creation dates are captured during sync")