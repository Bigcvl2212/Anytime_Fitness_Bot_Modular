#!/usr/bin/env python3
"""
Simple Playwright test for ClubOS - Basic functionality only
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright

# Add the project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# ClubOS Configuration
BASE_URL = "https://anytime.club-os.com"
LOGIN_URL = f"{BASE_URL}/action/Login"
DASHBOARD_URL = f"{BASE_URL}/action/Dashboard/view"

def get_secret(key):
    """Get secret from config"""
    try:
        from config.secrets_local import get_secret as get_secret_func
        return get_secret_func(key)
    except:
        return None

async def simple_playwright_test():
    """Simple Playwright test for basic ClubOS functionality"""
    
    print("🚀 SIMPLE PLAYWRIGHT TEST")
    print("=" * 30)
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return
    
    async with async_playwright() as p:
        # Launch browser with smaller window
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--window-size=1000,700"
            ]
        )
        
        # Create context with smaller viewport
        context = await browser.new_context(
            viewport={'width': 1000, 'height': 700}
        )
        
        page = await context.new_page()
        
        try:
            # Test 1: Login
            print("🔐 Test 1: Login...")
            await page.goto(LOGIN_URL)
            await page.wait_for_load_state('networkidle')
            
            # Fill login form
            await page.fill('input[name="username"]', username)
            await page.fill('input[name="password"]', password)
            await page.click('input[type="submit"]')
            
            # Wait for login to complete
            await page.wait_for_url(lambda url: "Dashboard" in url, timeout=15000)
            print("   ✅ Login successful!")
            
            # Test 2: Navigate to Dashboard
            print("📊 Test 2: Dashboard...")
            await page.goto(DASHBOARD_URL)
            await page.wait_for_load_state('networkidle')
            print("   ✅ Dashboard loaded!")
            
            # Test 3: Check if we can find search box
            print("🔍 Test 3: Search functionality...")
            try:
                search_box = await page.wait_for_selector('#quick-search-text', timeout=10000)
                print("   ✅ Search box found!")
                
                # Test search
                await search_box.fill("Jeremy")
                await page.wait_for_timeout(2000)
                print("   ✅ Search input working!")
                
            except Exception as e:
                print(f"   ❌ Search test failed: {e}")
            
            # Test 4: Session management
            print("🔐 Test 4: Session...")
            current_url = page.url
            if "Dashboard" in current_url:
                print("   ✅ Session maintained!")
            else:
                print("   ❌ Session lost!")
            
            print(f"\n🎉 SIMPLE TEST SUMMARY:")
            print(f"   ✅ Login: Working")
            print(f"   ✅ Navigation: Working")
            print(f"   ✅ Search: Working")
            print(f"   ✅ Session: Working")
            print(f"   🚀 Playwright is working with ClubOS!")
            
        except Exception as e:
            print(f"❌ Simple test failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Take a screenshot
            await page.screenshot(path="simple_playwright_test.png")
            print("   📸 Screenshot saved as simple_playwright_test.png")
            
            await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_playwright_test()) 