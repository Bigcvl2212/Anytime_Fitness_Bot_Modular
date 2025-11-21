#!/usr/bin/env python3
"""
Test script to verify campaign message sending speed improvements
"""

import os
import sys
import time
import json
from typing import List, Dict, Any

# Ensure project root is importable
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.services.clubos_messaging_client_simple import ClubOSMessagingClient


def test_campaign_speed():
    """Test both sequential and parallel campaign sending speeds"""
    
    # Test data - small batch for speed testing
    test_members = [
        {
            'member_id': '123456',
            'full_name': 'Test Member 1',
            'email': 'test1@example.com',
            'mobile_phone': '555-0001'
        },
        {
            'member_id': '123457', 
            'full_name': 'Test Member 2',
            'email': 'test2@example.com',
            'mobile_phone': '555-0002'
        },
        {
            'member_id': '123458',
            'full_name': 'Test Member 3', 
            'email': 'test3@example.com',
            'mobile_phone': '555-0003'
        }
    ]
    
    test_message = "Speed test message from Gym Bot"
    
    # Initialize client
    client = ClubOSMessagingClient()
    
    print("🚀 Testing Campaign Speed Improvements")
    print("=" * 50)
    
    # Test 1: Sequential (original method)
    print("\n📊 Testing Sequential Method...")
    start_time = time.time()
    
    try:
        if client.authenticate():
            sequential_results = client.send_bulk_campaign(
                member_data_list=test_members,
                message=test_message,
                message_type="sms"
            )
            sequential_time = time.time() - start_time
            print(f"✅ Sequential: {sequential_results['successful']}/{sequential_results['total']} in {sequential_time:.2f}s")
        else:
            print("❌ Authentication failed for sequential test")
            sequential_time = 0
    except Exception as e:
        print(f"❌ Sequential test failed: {e}")
        sequential_time = 0
    
    # Test 2: Parallel (new method)
    print("\n🚀 Testing Parallel Method...")
    start_time = time.time()
    
    try:
        if client.authenticated or client.authenticate():
            parallel_results = client.send_bulk_campaign_parallel(
                member_data_list=test_members,
                message=test_message,
                message_type="sms",
                max_workers=3
            )
            parallel_time = time.time() - start_time
            print(f"✅ Parallel: {parallel_results['successful']}/{parallel_results['total']} in {parallel_time:.2f}s")
        else:
            print("❌ Authentication failed for parallel test")
            parallel_time = 0
    except Exception as e:
        print(f"❌ Parallel test failed: {e}")
        parallel_time = 0
    
    # Performance comparison
    print("\n📈 Performance Comparison")
    print("=" * 50)
    
    if sequential_time > 0 and parallel_time > 0:
        speedup = sequential_time / parallel_time
        print(f"Sequential Time: {sequential_time:.2f}s")
        print(f"Parallel Time: {parallel_time:.2f}s")
        print(f"Speed Improvement: {speedup:.1f}x faster")
        
        if speedup > 1.5:
            print("🎉 Significant speed improvement achieved!")
        elif speedup > 1.1:
            print("✅ Modest speed improvement achieved")
        else:
            print("⚠️ Minimal speed improvement")
    else:
        print("❌ Could not complete performance comparison")
    
    # Test 3: Large batch simulation
    print("\n📊 Testing Large Batch Simulation...")
    large_batch = test_members * 10  # 30 members
    
    start_time = time.time()
    try:
        if client.authenticated or client.authenticate():
            large_results = client.send_bulk_campaign_parallel(
                member_data_list=large_batch,
                message=test_message,
                message_type="sms",
                max_workers=8
            )
            large_time = time.time() - start_time
            print(f"✅ Large Batch (30 members): {large_results['successful']}/{large_results['total']} in {large_time:.2f}s")
            print(f"📊 Rate: {large_results['total']/large_time:.1f} messages/second")
        else:
            print("❌ Authentication failed for large batch test")
    except Exception as e:
        print(f"❌ Large batch test failed: {e}")
    
    print("\n🎯 Campaign Speed Test Complete!")


if __name__ == "__main__":
    test_campaign_speed()
