#!/usr/bin/env python3
"""
Analyze the relationship between Dennis's CSV member ID and training delegate ID
"""

import sys
sys.path.append('.')

def analyze_dennis_ids():
    """Analyze Dennis's two different IDs to find patterns"""
    
    print("🔍 Analyzing Dennis Rost's ID relationship...")
    print("=" * 60)
    
    csv_member_id = 65828815
    training_delegate_id = 189425730
    
    print(f"CSV Member ID:       {csv_member_id}")
    print(f"Training Delegate ID: {training_delegate_id}")
    print(f"Difference:          {training_delegate_id - csv_member_id}")
    print(f"Ratio:               {training_delegate_id / csv_member_id:.6f}")
    
    # Check if there's a simple mathematical relationship
    print(f"\nMathematical relationships:")
    print(f"  Delegate = CSV × 2.88: {csv_member_id * 2.88:.0f}")
    print(f"  Delegate = CSV + offset: {csv_member_id + (training_delegate_id - csv_member_id)}")
    
    # Check binary representations
    print(f"\nBinary analysis:")
    print(f"  CSV ID binary:     {bin(csv_member_id)}")
    print(f"  Delegate ID binary: {bin(training_delegate_id)}")
    
    # Check if delegate ID contains CSV ID
    csv_str = str(csv_member_id)
    delegate_str = str(training_delegate_id)
    
    print(f"\nString analysis:")
    print(f"  CSV ID as string:     '{csv_str}'")
    print(f"  Delegate ID as string: '{delegate_str}'")
    print(f"  CSV ID in delegate:   {csv_str in delegate_str}")
    
    # Look for patterns in the digits
    print(f"\nDigit analysis:")
    csv_digits = [int(d) for d in csv_str]
    delegate_digits = [int(d) for d in delegate_str]
    
    print(f"  CSV digits:      {csv_digits}")
    print(f"  Delegate digits: {delegate_digits}")
    
    # Check if there are common subsequences
    print(f"\nLooking for common digit patterns...")
    for i in range(len(csv_digits)):
        for j in range(i+1, len(csv_digits)+1):
            subsequence = csv_str[i:j]
            if len(subsequence) >= 2 and subsequence in delegate_str:
                print(f"  Common sequence: '{subsequence}' found in both")

def test_id_transformations():
    """Test various transformations that might convert CSV ID to delegate ID"""
    
    print(f"\n🧪 Testing ID transformation patterns...")
    print("=" * 60)
    
    csv_id = 65828815
    target_delegate = 189425730
    
    transformations = [
        ("Add constant", lambda x: x + 123596915),
        ("Multiply by 2.88", lambda x: int(x * 2.88)),
        ("Bit shift left", lambda x: x << 1),
        ("Add and multiply", lambda x: (x + 100000000) * 1.5),
        ("Reverse digits + add", lambda x: int(str(x)[::-1]) + 100000000),
        ("First 3 + last 3 + middle", lambda x: int(str(x)[:3] + str(x)[-3:] + str(x)[3:-3])),
    ]
    
    for name, transform in transformations:
        try:
            result = int(transform(csv_id))
            print(f"  {name:20}: {result:>10} (diff: {abs(result - target_delegate):>10})")
        except Exception as e:
            print(f"  {name:20}: Error - {e}")

def check_clubos_database_pattern():
    """Check if there's a database pattern we can exploit"""
    
    print(f"\n🗄️ Checking for database patterns...")
    print("=" * 60)
    
    # Connect to local database to see if there are other examples
    try:
        import sqlite3
        
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Check if we have any other training clients with known IDs
        cursor.execute("SELECT member_name, clubos_member_id FROM training_clients WHERE clubos_member_id IS NOT NULL AND clubos_member_id != ''")
        training_clients = cursor.fetchall()
        
        print(f"Found {len(training_clients)} training clients with ClubOS IDs:")
        for name, clubos_id in training_clients:
            print(f"  {name}: {clubos_id}")
        
        # Check members table for any patterns
        cursor.execute("SELECT full_name, id FROM members LIMIT 10")
        members = cursor.fetchall()
        
        print(f"\nSample members table entries:")
        for name, member_id in members:
            print(f"  {name}: {member_id}")
        
        conn.close()
        
    except Exception as e:
        print(f"  Database error: {e}")

if __name__ == "__main__":
    analyze_dennis_ids()
    test_id_transformations()
    check_clubos_database_pattern()
    
    print("\n" + "=" * 60)
    print("🏁 Analysis complete!")
    print("\nKey findings:")
    print("  - Dennis has two distinct IDs in ClubOS")
    print("  - CSV member ID: 65828815 (basic member data)")
    print("  - Training delegate ID: 189425730 (training packages)")
    print("  - No obvious mathematical relationship found")
    print("  - Manual workflow (search → account → clubservices) doesn't work with CSV ID")
    print("  - Need alternative approach to discover training delegate IDs")
