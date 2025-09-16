#!/usr/bin/env python3
"""
Debug script to check current state of training clients data
"""
import sqlite3
import json

def check_training_clients_state():
    """Check what's currently in the training_clients table"""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    try:
        # Get all training clients with their package details
        cursor.execute("""
            SELECT 
                member_name, 
                payment_status, 
                past_due_amount, 
                total_past_due, 
                package_details,
                package_summary,
                last_updated
            FROM training_clients 
            ORDER BY member_name
            LIMIT 10
        """)
        
        clients = cursor.fetchall()
        
        print(f"📊 Found {len(clients)} training clients in database")
        print("=" * 80)
        
        for i, client in enumerate(clients, 1):
            member_name, payment_status, past_due_amount, total_past_due, package_details, package_summary, last_updated = client
            
            print(f"\n{i}. {member_name}")
            print(f"   Payment Status: {payment_status}")
            print(f"   Past Due Amount: ${past_due_amount or 0}")
            print(f"   Total Past Due: ${total_past_due or 0}")
            print(f"   Last Updated: {last_updated}")
            
            # Try to parse package_details JSON
            if package_details:
                try:
                    details = json.loads(package_details)
                    print(f"   Package Details Type: {type(details)}")
                    print(f"   Package Details Length: {len(details) if isinstance(details, list) else 'N/A'}")
                    if isinstance(details, list) and len(details) > 0:
                        print(f"   First Package: {details[0]}")
                    else:
                        print(f"   Package Details: {details}")
                except json.JSONDecodeError:
                    print(f"   Package Details (raw): {package_details[:100]}...")
            else:
                print("   Package Details: NULL/Empty")
            
            if package_summary:
                print(f"   Package Summary: {package_summary[:100]}...")
            else:
                print("   Package Summary: NULL/Empty")
                
        # Check if any clients have non-zero past due amounts
        cursor.execute("""
            SELECT COUNT(*) FROM training_clients 
            WHERE past_due_amount > 0 OR total_past_due > 0
        """)
        past_due_count = cursor.fetchone()[0]
        print(f"\n📊 Clients with past due amounts: {past_due_count}")
        
        # Check payment statuses
        cursor.execute("""
            SELECT payment_status, COUNT(*) FROM training_clients 
            GROUP BY payment_status
        """)
        status_counts = cursor.fetchall()
        print(f"\n📊 Payment Status Breakdown:")
        for status, count in status_counts:
            print(f"   {status}: {count}")
            
    except Exception as e:
        print(f"❌ Error checking training clients: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_training_clients_state()