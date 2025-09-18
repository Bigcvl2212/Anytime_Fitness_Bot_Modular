#!/usr/bin/env python3
"""
Test script to verify rate limiting configuration for automation endpoints
"""

import requests
import time
import sys
from datetime import datetime

def test_rate_limiting():
    """Test the rate limiting behavior for bulk check-in status endpoint"""
    
    base_url = "http://127.0.0.1:5000"
    endpoint = f"{base_url}/api/bulk-checkin-status"
    
    print(f"Testing rate limiting for: {endpoint}")
    print(f"Started at: {datetime.now()}")
    print("-" * 50)
    
    success_count = 0
    rate_limited_count = 0
    
    # Test with rapid requests to see if automation endpoints are properly exempt
    for i in range(1, 21):  # Test 20 requests rapidly
        try:
            start_time = time.time()
            response = requests.get(endpoint, timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                success_count += 1
                print(f"Request {i:2d}: ✅ SUCCESS (200) - {response_time:.3f}s")
            elif response.status_code == 429:  # Rate limited
                rate_limited_count += 1
                print(f"Request {i:2d}: ❌ RATE LIMITED (429) - {response_time:.3f}s")
                print(f"           Rate limit response: {response.text}")
            else:
                print(f"Request {i:2d}: ⚠️  OTHER ({response.status_code}) - {response_time:.3f}s")
                
        except requests.exceptions.RequestException as e:
            print(f"Request {i:2d}: ❌ CONNECTION ERROR - {e}")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    print("-" * 50)
    print(f"Test Summary:")
    print(f"  Total requests: 20")
    print(f"  Successful: {success_count}")
    print(f"  Rate limited: {rate_limited_count}")
    print(f"  Completed at: {datetime.now()}")
    
    if rate_limited_count == 0:
        print("✅ SUCCESS: No rate limiting detected - automation endpoints are properly exempt!")
    else:
        print("❌ ISSUE: Rate limiting still occurring on automation endpoint")
    
    return rate_limited_count == 0

if __name__ == "__main__":
    try:
        success = test_rate_limiting()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)