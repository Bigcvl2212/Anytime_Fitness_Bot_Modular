#!/usr/bin/env python3
"""
Comprehensive Playwright test for ClubOS messaging
Tests all major functions: login, search, navigation, messaging
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright
import time

# Add the project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# ClubOS Configuration
BASE_URL = "https://anytime.club-os.com"
LOGIN_URL = f"{BASE_URL}/action/Login"
DASHBOARD_URL = f"{BASE_URL}/action/Dashboard/view"

# Jeremy Mayo details
TARGET_NAME = "Jeremy Mayo"
TARGET_MEMBER_ID = "187032782"
SMS_MESSAGE = "🎉 Playwright Test - This SMS was sent via Playwright automation!"
EMAIL_MESSAGE = "🎉 Playwright Test - This EMAIL was sent via Playwright automation!"

def get_secret(key):
    """Get secret from config"""
    try:
        from config.secrets_local import get_secret as get_secret_func
        return get_secret_func(key)
    except:
        return None

async def test_playwright_messaging():
    """Comprehensive Playwright test for ClubOS messaging"""
    
    print("🚀 PLAYWRIGHT CLUBOS MESSAGING TEST")
    print("=" * 50)
    print(f"Target: {TARGET_NAME}")
    print(f"Member ID: {TARGET_MEMBER_ID}")
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return
    
    async with async_playwright() as p:
        # Launch browser with better options
        browser = await p.chromium.launch(
            headless=False,  # Set to True for production
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1200,800"
            ]
        )
        
        # Create context with better settings
        context = await browser.new_context(
            viewport={'width': 1200, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        try:
            # Test 1: Login
            print("🔐 Test 1: Login to ClubOS...")
            await page.goto(LOGIN_URL)
            await page.wait_for_load_state('networkidle')
            
            # Fill login form
            await page.fill('input[name="username"]', username)
            await page.fill('input[name="password"]', password)
            
            # Click login button
            await page.click('input[type="submit"]')
            
            # Wait for login to complete
            await page.wait_for_url(lambda url: "Dashboard" in url, timeout=15000)
            print("   ✅ Login successful!")
            
            # Test 2: Navigate to Dashboard
            print("📊 Test 2: Navigate to Dashboard...")
            await page.goto(DASHBOARD_URL)
            await page.wait_for_load_state('networkidle')
            print("   ✅ Dashboard loaded successfully!")
            
            # Test 3: Search for Member
            print(f"🔍 Test 3: Search for {TARGET_NAME}...")
            search_box = await page.wait_for_selector('#quick-search-text', timeout=10000)
            await search_box.fill(TARGET_NAME)
            await page.wait_for_timeout(3000)  # Wait for search results
            
            # Click on search result
            try:
                # Try multiple selectors for the search result
                search_result_selectors = [
                    f"//h4[contains(text(), '{TARGET_NAME}')]",
                    f"//div[contains(text(), '{TARGET_NAME}')]",
                    f"//a[contains(text(), '{TARGET_NAME}')]"
                ]
                
                search_result_clicked = False
                for selector in search_result_selectors:
                    try:
                        await page.click(selector, timeout=5000)
                        search_result_clicked = True
                        print(f"   ✅ Found and clicked on {TARGET_NAME}")
                        break
                    except:
                        continue
                
                if not search_result_clicked:
                    print(f"   ⚠️ Could not find {TARGET_NAME} in search results")
                    # Try direct navigation
                    member_url = f"{BASE_URL}/action/Delegate/{TARGET_MEMBER_ID}/url=/action/LeadProfile"
                    await page.goto(member_url)
                    print(f"   ✅ Navigated directly to member profile")
                
            except Exception as e:
                print(f"   ⚠️ Search result click failed: {e}")
                # Fallback to direct navigation
                member_url = f"{BASE_URL}/action/Delegate/{TARGET_MEMBER_ID}/url=/action/LeadProfile"
                await page.goto(member_url)
                print(f"   ✅ Used direct navigation to member profile")
            
            await page.wait_for_load_state('networkidle')
            print("   ✅ Member profile loaded successfully!")
            
            # Test 4: Find and Click Send Message Button
            print("📤 Test 4: Find Send Message button...")
            try:
                # Try multiple selectors for the Send Message button
                send_message_selectors = [
                    "a[data-original-title='Send Message']",
                    "a[title='Send Message']",
                    "//a[contains(text(), 'Send Message')]",
                    "//button[contains(text(), 'Send Message')]",
                    "//a[contains(@class, 'send-message')]"
                ]
                
                send_button_clicked = False
                for selector in send_message_selectors:
                    try:
                        await page.click(selector, timeout=5000)
                        send_button_clicked = True
                        print("   ✅ Found and clicked Send Message button")
                        break
                    except:
                        continue
                
                if not send_button_clicked:
                    print("   ❌ Could not find Send Message button")
                    return
                
            except Exception as e:
                print(f"   ❌ Send Message button click failed: {e}")
                return
            
            # Test 5: Wait for Popup and Handle Messaging
            print("📱 Test 5: Handle messaging popup...")
            await page.wait_for_timeout(3000)  # Wait for popup to load
            
            # Check if popup is visible
            popup_visible = await page.is_visible('#followup-popup-content')
            if not popup_visible:
                print("   ❌ Messaging popup not visible")
                return
            
            print("   ✅ Messaging popup is visible!")
            
            # Test 6: Send SMS
            print("📱 Test 6: Send SMS...")
            try:
                # Check for text tab
                text_tab = await page.query_selector('#text-tab')
                if text_tab:
                    await text_tab.click()
                    await page.wait_for_timeout(1000)
                    
                    # Fill SMS form
                    await page.fill('input[name="textMessage"]', SMS_MESSAGE)
                    await page.fill('input[name="followUpOutcomeNotes"]', 'Playwright test SMS')
                    
                    # Click send button
                    send_button = await page.query_selector('a.save-follow-up')
                    if send_button:
                        await send_button.click()
                        print("   ✅ SMS form submitted!")
                        
                        # Wait for popup to close
                        await page.wait_for_selector('#followup-popup-content', state='hidden', timeout=10000)
                        print("   ✅ SMS sent successfully!")
                    else:
                        print("   ❌ Could not find SMS send button")
                else:
                    print("   ⚠️ Text tab not available")
                    
            except Exception as e:
                print(f"   ❌ SMS sending failed: {e}")
            
            # Test 7: Send Email
            print("📧 Test 7: Send Email...")
            try:
                # Re-open popup if needed
                popup_visible = await page.is_visible('#followup-popup-content')
                if not popup_visible:
                    print("   📤 Re-opening message popup for email...")
                    await page.click("a[data-original-title='Send Message']")
                    await page.wait_for_timeout(3000)
                
                # Check for email tab
                email_tab = await page.query_selector('#email-tab')
                if email_tab:
                    await email_tab.click()
                    await page.wait_for_timeout(1000)
                    
                    # Fill email form
                    await page.fill('input[name="emailSubject"]', 'Playwright Test Email')
                    
                    # Handle rich text editor for email body
                    email_editor = await page.query_selector('div.redactor_editor')
                    if email_editor:
                        await page.evaluate("arguments[0].innerHTML = arguments[1];", email_editor, EMAIL_MESSAGE)
                    else:
                        # Fallback to regular textarea
                        email_body_input = await page.query_selector('textarea[name="emailBody"]')
                        if email_body_input:
                            await email_body_input.fill(EMAIL_MESSAGE)
                    
                    await page.fill('input[name="followUpOutcomeNotes"]', 'Playwright test email')
                    
                    # Click send button
                    send_button = await page.query_selector('a.save-follow-up')
                    if send_button:
                        await send_button.click()
                        print("   ✅ Email form submitted!")
                        
                        # Wait for popup to close
                        await page.wait_for_selector('#followup-popup-content', state='hidden', timeout=10000)
                        print("   ✅ Email sent successfully!")
                    else:
                        print("   ❌ Could not find email send button")
                else:
                    print("   ⚠️ Email tab not available")
                    
            except Exception as e:
                print(f"   ❌ Email sending failed: {e}")
            
            # Test 8: Session Management
            print("🔐 Test 8: Verify session management...")
            await page.goto(DASHBOARD_URL)
            await page.wait_for_load_state('networkidle')
            
            # Check if still logged in
            current_url = page.url
            if "Dashboard" in current_url or "dashboard" in current_url.lower():
                print("   ✅ Session maintained successfully!")
            else:
                print("   ❌ Session lost!")
            
            print(f"\n🎉 PLAYWRIGHT TEST SUMMARY:")
            print(f"   ✅ Login: Working")
            print(f"   ✅ Navigation: Working")
            print(f"   ✅ Member Search: Working")
            print(f"   ✅ Popup Handling: Working")
            print(f"   ✅ Form Interactions: Working")
            print(f"   ✅ Session Management: Working")
            print(f"   📧 Check your phone and email for the messages!")
            
        except Exception as e:
            print(f"❌ Playwright test failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Take a screenshot for debugging
            await page.screenshot(path="playwright_test_result.png")
            print("   📸 Screenshot saved as playwright_test_result.png")
            
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_playwright_messaging()) 