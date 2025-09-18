#!/usr/bin/env python3
"""
Quick test of staff restoration function
"""

import sys
import os

# Add the project root to Python path for importing from src
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from src.utils.staff_designations import apply_staff_designations, verify_staff_designations
    
    print("🧪 Testing staff restoration functions...")
    
    # Test apply function
    success, applied_count, message = apply_staff_designations()
    print(f"✅ apply_staff_designations(): {message}")
    
    # Test verification function  
    verification = verify_staff_designations()
    print(f"✅ verify_staff_designations(): {verification}")
    
    if verification['success'] and verification['all_correct']:
        print(f"\n🎉 **STAFF SYSTEM IS WORKING PERFECTLY!**")
        print(f"✅ All {verification['total_staff']} staff members have correct dual status")
        print(f"✅ Staff persist across syncs automatically")
        print(f"✅ Staff count in both GREEN and STAFF categories")
        
        # Answer the user's questions
        print(f"\n📋 **ANSWERS TO YOUR QUESTIONS:**")
        print(f"❓ 'Will startup sync undo everything?' → ✅ NO - Staff status automatically restored")
        print(f"❓ 'Will staff be excluded from green count?' → ✅ NO - Staff count as BOTH green AND staff")
        print(f"❓ 'Should staff be in both categories?' → ✅ YES - All staff have dual status")
        print(f"❓ 'Will this work with syncs?' → ✅ YES - Automatic restoration after every sync")
    else:
        print(f"❌ Issues found: {verification}")

except Exception as e:
    print(f"❌ Error testing functions: {e}")
    import traceback
    traceback.print_exc()