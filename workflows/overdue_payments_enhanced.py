"""
Enhanced Overdue Payments Workflow - API-Based Version

Handles processing of overdue member payments using API calls instead of Selenium.
Includes hybrid fallback support for maximum reliability.
"""

from typing import Dict, List, Optional, Union
from src.services.data.member_data import get_yellow_red_members, get_member_balance_from_contact_data, batch_update_past_due_amounts
from src.services.payments.square_client import create_overdue_payment_message_with_invoice
from src.services.api.migration_service import get_migration_service


def process_overdue_payments_api(migration_mode: str = "hybrid") -> bool:
    """
    Enhanced overdue payments workflow using API calls with optional Selenium fallback.
    
    Args:
        migration_mode: "api_only", "hybrid", or "selenium_only"
    
    Returns:
        bool: True if processing completed successfully
    """
    print("💳 Processing overdue payments workflow (API-enhanced)...")
    print(f"   Migration mode: {migration_mode}")
    
    try:
        # Initialize migration service
        migration_service = get_migration_service(migration_mode)
        
        # Get yellow/red members who need invoices
        past_due_members = get_yellow_red_members()
        
        if not past_due_members:
            print("INFO: No past due members found")
            return True
        
        print(f"INFO: Found {len(past_due_members)} past due members to process")
        
        invoices_sent = 0
        invoices_failed = 0
        skipped_no_data = 0
        past_due_updates = []  # Collect updates for batch processing
        
        for member in past_due_members:
            try:
                member_name = member['name']
                category = member['category']  # 'yellow' or 'red'
                
                # Get the actual past due amount for this specific member
                print(f"INFO: Fetching actual balance for {category} member: {member_name}")
                actual_amount_due = get_member_balance_from_contact_data(member)
                
                # Save the past due amount to our updates list (even if 0)
                past_due_updates.append((member_name, actual_amount_due))
                
                # ONLY process members with real API data - skip if no real amount
                if actual_amount_due <= 0:
                    print(f"⚠️  SKIPPED: {member_name} - No real past due amount from API")
                    skipped_no_data += 1
                    continue
                
                print(f"INFO: Processing {category} member: {member_name} (${actual_amount_due:.2f} past due)")
                
                # Create invoice and message with actual amount
                message, invoice_url = create_overdue_payment_message_with_invoice(
                    member_name=member_name,
                    membership_amount=actual_amount_due
                )
                
                if message and invoice_url:
                    # Send message via API (with Selenium fallback if enabled)
                    success = migration_service.send_message(
                        member_name=member_name, 
                        subject="⚠️ Overdue Payment - Action Required",
                        body=message
                    )
                    
                    if success:
                        print(f"✅ Invoice sent successfully to {member_name}")
                        print(f"   Invoice URL: {invoice_url}")
                        invoices_sent += 1
                    else:
                        print(f"❌ Failed to send message to {member_name}")
                        invoices_failed += 1
                else:
                    print(f"❌ Failed to create invoice for {member_name}")
                    invoices_failed += 1
                    
            except Exception as e:
                print(f"❌ Error processing member {member.get('name', 'Unknown')}: {e}")
                invoices_failed += 1
                continue
        
        # Batch update all past due amounts to master contact list
        print(f"\n💾 UPDATING MASTER CONTACT LIST...")
        if past_due_updates:
            update_results = batch_update_past_due_amounts(past_due_updates)
            print(f"   📝 Updated {update_results['success_count']} members with past due amounts")
            if update_results['failed_count'] > 0:
                print(f"   ⚠️  Failed to update {update_results['failed_count']} members")
        
        # Get migration statistics
        migration_stats = migration_service.get_migration_stats()
        
        print(f"\n📊 OVERDUE PAYMENTS SUMMARY:")
        print(f"   ✅ Invoices sent: {invoices_sent}")
        print(f"   ❌ Failed: {invoices_failed}")
        print(f"   ⚠️  Skipped (no real API data): {skipped_no_data}")
        print(f"   📋 Total processed: {len(past_due_members)}")
        print(f"   💾 Past due amounts saved to master contact list")
        print(f"   💡 Only members with verified API balances received invoices")
        
        print(f"\n📈 MIGRATION STATISTICS:")
        print(f"   🚀 API attempts: {migration_stats['api_attempts']}")
        print(f"   ✅ API successes: {migration_stats['api_successes']}")
        print(f"   🔄 Selenium fallbacks: {migration_stats['selenium_fallbacks']}")
        print(f"   📊 API success rate: {migration_stats['api_success_rate']:.1f}%")
        
        # Save migration report
        migration_service.save_migration_report()
        
        return invoices_sent > 0
        
    except Exception as e:
        print(f"❌ Error in overdue payments workflow: {e}")
        return False


def process_overdue_payments_legacy(driver) -> bool:
    """
    Legacy Selenium-based overdue payments workflow (for comparison/fallback).
    
    Args:
        driver: WebDriver instance for ClubOS operations
    
    Returns:
        bool: True if processing completed successfully
    """
    print("INFO: Using legacy Selenium-based overdue payments workflow...")
    
    try:
        # Import the legacy implementation
        from src.services.clubos.messaging import send_clubos_message
        
        # Get yellow/red members who need invoices
        past_due_members = get_yellow_red_members()
        
        if not past_due_members:
            print("INFO: No past due members found")
            return True
        
        print(f"INFO: Found {len(past_due_members)} past due members to process")
        
        invoices_sent = 0
        invoices_failed = 0
        skipped_no_data = 0
        past_due_updates = []  # Collect updates for batch processing
        
        for member in past_due_members:
            try:
                member_name = member['name']
                category = member['category']  # 'yellow' or 'red'
                
                # Get the actual past due amount for this specific member
                print(f"INFO: Fetching actual balance for {category} member: {member_name}")
                actual_amount_due = get_member_balance_from_contact_data(member)
                
                # Save the past due amount to our updates list (even if 0)
                past_due_updates.append((member_name, actual_amount_due))
                
                # ONLY process members with real API data - skip if no real amount
                if actual_amount_due <= 0:
                    print(f"⚠️  SKIPPED: {member_name} - No real past due amount from API")
                    skipped_no_data += 1
                    continue
                
                print(f"INFO: Processing {category} member: {member_name} (${actual_amount_due:.2f} past due)")
                
                # Create invoice and message with actual amount
                message, invoice_url = create_overdue_payment_message_with_invoice(
                    member_name=member_name,
                    membership_amount=actual_amount_due
                )
                
                if message and invoice_url:
                    # Send message via ClubOS (legacy Selenium)
                    success = send_clubos_message(
                        driver=driver,
                        member_name=member_name, 
                        subject="⚠️ Overdue Payment - Action Required",
                        body=message
                    )
                    
                    if success:
                        print(f"✅ Invoice sent successfully to {member_name}")
                        print(f"   Invoice URL: {invoice_url}")
                        invoices_sent += 1
                    else:
                        print(f"❌ Failed to send message to {member_name}")
                        invoices_failed += 1
                else:
                    print(f"❌ Failed to create invoice for {member_name}")
                    invoices_failed += 1
                    
            except Exception as e:
                print(f"❌ Error processing member {member.get('name', 'Unknown')}: {e}")
                invoices_failed += 1
                continue
        
        # Batch update all past due amounts to master contact list
        print(f"\n💾 UPDATING MASTER CONTACT LIST...")
        if past_due_updates:
            update_results = batch_update_past_due_amounts(past_due_updates)
            print(f"   📝 Updated {update_results['success_count']} members with past due amounts")
            if update_results['failed_count'] > 0:
                print(f"   ⚠️  Failed to update {update_results['failed_count']} members")
        
        print(f"\n📊 OVERDUE PAYMENTS SUMMARY (LEGACY):")
        print(f"   ✅ Invoices sent: {invoices_sent}")
        print(f"   ❌ Failed: {invoices_failed}")
        print(f"   ⚠️  Skipped (no real API data): {skipped_no_data}")
        print(f"   📋 Total processed: {len(past_due_members)}")
        print(f"   💾 Past due amounts saved to master contact list")
        print(f"   💡 Only members with verified API balances received invoices")
        
        return invoices_sent > 0
        
    except Exception as e:
        print(f"❌ Error in legacy overdue payments workflow: {e}")
        return False


def compare_api_vs_selenium_payments(test_member_count: int = 3) -> Dict[str, any]:
    """
    Compare API vs Selenium performance for overdue payments.
    
    Args:
        test_member_count: Number of test members to process
        
    Returns:
        Comparison results
    """
    print("🧪 Comparing API vs Selenium for overdue payments...")
    
    try:
        # Get a subset of members for testing
        all_members = get_yellow_red_members()
        test_members = all_members[:test_member_count] if all_members else []
        
        if not test_members:
            print("⚠️ No test members available for comparison")
            return {"error": "No test members available"}
        
        # Initialize migration service in testing mode
        migration_service = get_migration_service("testing")
        
        comparison_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_member_count": len(test_members),
            "member_results": [],
            "api_total_time": 0,
            "selenium_total_time": 0,
            "api_success_count": 0,
            "selenium_success_count": 0
        }
        
        # Test each member with both approaches
        for member in test_members:
            member_name = member['name']
            print(f"   🧪 Testing member: {member_name}")
            
            # Get member balance for invoice creation
            actual_amount_due = get_member_balance_from_contact_data(member)
            
            if actual_amount_due <= 0:
                print(f"   ⚠️ Skipping {member_name} - no balance due")
                continue
            
            # Create invoice and message
            message, invoice_url = create_overdue_payment_message_with_invoice(
                member_name=member_name,
                membership_amount=actual_amount_due
            )
            
            if not message or not invoice_url:
                print(f"   ⚠️ Skipping {member_name} - invoice creation failed")
                continue
            
            # Compare API vs Selenium for message sending
            comparison_result = migration_service.compare_api_vs_selenium(
                "send_message",
                member_name=member_name,
                subject="🧪 Test - Overdue Payment",
                body=message
            )
            
            member_result = {
                "member_name": member_name,
                "amount_due": actual_amount_due,
                "api_result": comparison_result["api_result"],
                "selenium_result": comparison_result["selenium_result"],
                "api_time": comparison_result["api_time"],
                "selenium_time": comparison_result["selenium_time"],
                "results_match": comparison_result["results_match"],
                "errors": comparison_result["errors"]
            }
            
            comparison_results["member_results"].append(member_result)
            
            # Update totals
            if comparison_result["api_time"]:
                comparison_results["api_total_time"] += comparison_result["api_time"]
            if comparison_result["selenium_time"]:
                comparison_results["selenium_total_time"] += comparison_result["selenium_time"]
            
            if comparison_result["api_result"]:
                comparison_results["api_success_count"] += 1
            if comparison_result["selenium_result"]:
                comparison_results["selenium_success_count"] += 1
            
            print(f"   ✅ Comparison completed for {member_name}")
        
        # Calculate summary statistics
        if comparison_results["member_results"]:
            comparison_results["avg_api_time"] = comparison_results["api_total_time"] / len(comparison_results["member_results"])
            comparison_results["avg_selenium_time"] = comparison_results["selenium_total_time"] / len(comparison_results["member_results"])
            comparison_results["api_success_rate"] = (comparison_results["api_success_count"] / len(comparison_results["member_results"])) * 100
            comparison_results["selenium_success_rate"] = (comparison_results["selenium_success_count"] / len(comparison_results["member_results"])) * 100
        
        print(f"\n📊 COMPARISON SUMMARY:")
        print(f"   👥 Members tested: {len(comparison_results['member_results'])}")
        print(f"   ⚡ Avg API time: {comparison_results.get('avg_api_time', 0):.2f}s")
        print(f"   ⚡ Avg Selenium time: {comparison_results.get('avg_selenium_time', 0):.2f}s")
        print(f"   ✅ API success rate: {comparison_results.get('api_success_rate', 0):.1f}%")
        print(f"   ✅ Selenium success rate: {comparison_results.get('selenium_success_rate', 0):.1f}%")
        
        return comparison_results
        
    except Exception as e:
        print(f"❌ Error in comparison test: {e}")
        return {"error": str(e)}


# Convenience function for backward compatibility
def process_overdue_payments(driver=None, migration_mode: str = "hybrid") -> bool:
    """
    Process overdue payments with automatic API/Selenium selection.
    
    Args:
        driver: Optional WebDriver instance (for legacy compatibility)
        migration_mode: Migration mode for API service
        
    Returns:
        bool: True if processing completed successfully
    """
    if driver and migration_mode == "selenium_only":
        # Use legacy Selenium approach
        return process_overdue_payments_legacy(driver)
    else:
        # Use enhanced API approach
        return process_overdue_payments_api(migration_mode)


# Function aliases for testing and migration
process_overdue_payments_enhanced = process_overdue_payments_api
process_overdue_payments_original = process_overdue_payments_legacy