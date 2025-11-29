#!/usr/bin/env python3
"""
Sync training clients payment status from LIVE ClubOS API
This updates the database with current payment status from ClubOS
"""

from clubos_training_api import ClubOSTrainingPackageAPI
from src.services.database_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_training_payment_status():
    """Sync payment status for all training clients from ClubOS"""
    db = DatabaseManager()
    api = ClubOSTrainingPackageAPI()
    
    if not api.authenticate():
        print("❌ ClubOS authentication failed")
        return
    
    # Get all training clients
    all_clients = db.execute_query(
        'SELECT id, member_name, clubos_member_id, payment_status, past_due_amount, total_past_due FROM training_clients',
        fetch_all=True
    )
    
    print(f"📋 Checking {len(all_clients)} training clients against LIVE ClubOS data...")
    
    updated_count = 0
    errors = []
    
    for c in all_clients:
        d = dict(c)
        db_id = d['id']
        member_id = d.get('clubos_member_id')
        name = d.get('member_name')
        old_status = d.get('payment_status', 'Unknown')
        
        if not member_id:
            print(f"  ⚠️ {name}: No ClubOS ID - skipping")
            continue
        
        try:
            # Get LIVE status from ClubOS
            live_status = api.get_member_payment_status(member_id)
            
            if live_status:
                # Normalize status
                is_past_due = 'past due' in live_status.lower()
                new_status = 'Past Due' if is_past_due else 'Current'
                
                # Only update if status changed
                if new_status != old_status:
                    # Update database
                    if is_past_due:
                        # For past due, we need to get the actual amount - but API doesn't return it
                        # Just set a flag for now, amount will need manual lookup
                        db.execute_query(
                            """UPDATE training_clients 
                               SET payment_status = ?, 
                                   past_due_amount = CASE WHEN past_due_amount = 0 THEN 0.01 ELSE past_due_amount END,
                                   total_past_due = CASE WHEN total_past_due = 0 THEN 0.01 ELSE total_past_due END,
                                   updated_at = CURRENT_TIMESTAMP
                               WHERE id = ?""",
                            (new_status, db_id)
                        )
                    else:
                        # Clear past due status
                        db.execute_query(
                            """UPDATE training_clients 
                               SET payment_status = ?, 
                                   past_due_amount = 0,
                                   total_past_due = 0,
                                   updated_at = CURRENT_TIMESTAMP
                               WHERE id = ?""",
                            (new_status, db_id)
                        )
                    
                    updated_count += 1
                    print(f"  🔄 {name}: {old_status} → {new_status}")
                else:
                    print(f"  ✅ {name}: {new_status} (no change)")
            else:
                print(f"  ⚠️ {name}: Could not get status from ClubOS")
                
        except Exception as e:
            errors.append(f"{name}: {e}")
            print(f"  ❌ {name}: Error - {e}")
    
    print(f"\n=== SYNC COMPLETE ===")
    print(f"Updated: {updated_count} clients")
    print(f"Errors: {len(errors)}")
    
    # Show current state
    result = db.execute_query(
        "SELECT member_name, payment_status, total_past_due FROM training_clients WHERE payment_status = 'Past Due' ORDER BY member_name",
        fetch_all=True
    )
    print(f"\nCurrent Past Due Training Clients: {len(result)}")
    for r in result:
        d = dict(r)
        print(f"  🔴 {d['member_name']}: ${d['total_past_due']:.2f}")

if __name__ == "__main__":
    sync_training_payment_status()
