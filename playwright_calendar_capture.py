#!/usr/bin/env python3
"""
Playwright Calendar Workflow Capture
Captures network traffic while you manually interact with ClubOS calendar
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

class NetworkTrafficCapture:
    def __init__(self):
        self.requests = []
        self.responses = []
        self.output_dir = None
        
    async def setup_output_dir(self):
        """Create output directory for captures"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"captures/playwright_capture_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"📁 Output directory: {self.output_dir}")
        
    async def log_request(self, request):
        """Log outgoing requests"""
        if 'club-os.com' in request.url:
            req_data = {
                'timestamp': datetime.now().isoformat(),
                'method': request.method,
                'url': request.url,
                'headers': dict(request.headers),
                'post_data': request.post_data if request.post_data else None
            }
            self.requests.append(req_data)
            
            # Print important requests in real-time
            if any(keyword in request.url.lower() for keyword in ['calendar', 'event', 'delete', 'remove']):
                print(f"🌐 {request.method} {request.url}")
                if request.post_data:
                    print(f"   📤 POST Data: {request.post_data}")
                    
    async def log_response(self, response):
        """Log incoming responses"""
        if 'club-os.com' in response.url:
            try:
                response_text = await response.text() if response.status != 204 else ""
            except:
                response_text = "[Could not read response body]"
                
            resp_data = {
                'timestamp': datetime.now().isoformat(),
                'status': response.status,
                'url': response.url,
                'headers': dict(response.headers),
                'body': response_text[:1000] if response_text else None  # Limit body size
            }
            self.responses.append(resp_data)
            
            # Print important responses in real-time
            if any(keyword in response.url.lower() for keyword in ['calendar', 'event', 'delete', 'remove']):
                print(f"✅ {response.status} {response.url}")
                if response_text and len(response_text) < 200:
                    print(f"   📥 Response: {response_text}")
                    
    async def save_captures(self):
        """Save all captured data to files"""
        if not self.output_dir:
            return
            
        # Save requests
        requests_file = os.path.join(self.output_dir, "requests.json")
        with open(requests_file, 'w') as f:
            json.dump(self.requests, f, indent=2)
        print(f"💾 Saved {len(self.requests)} requests to {requests_file}")
        
        # Save responses  
        responses_file = os.path.join(self.output_dir, "responses.json")
        with open(responses_file, 'w') as f:
            json.dump(self.responses, f, indent=2)
        print(f"💾 Saved {len(self.responses)} responses to {responses_file}")
        
        # Save summary
        summary = {
            'capture_time': datetime.now().isoformat(),
            'total_requests': len(self.requests),
            'total_responses': len(self.responses),
            'calendar_requests': [r for r in self.requests if 'calendar' in r['url'].lower()],
            'event_requests': [r for r in self.requests if 'event' in r['url'].lower()],
            'delete_requests': [r for r in self.requests if any(kw in r['url'].lower() for kw in ['delete', 'remove'])]
        }
        
        summary_file = os.path.join(self.output_dir, "summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"📊 Saved capture summary to {summary_file}")

async def capture_manual_workflow():
    """Start browser and capture traffic while user manually interacts"""
    
    print("🎭 PLAYWRIGHT MANUAL CAPTURE MODE")
    print("=" * 50)
    print("This will open ClubOS in a browser and capture all network traffic")
    print("while you manually interact with the calendar.")
    print("=" * 50)
    
    capture = NetworkTrafficCapture()
    await capture.setup_output_dir()
    
    async with async_playwright() as p:
        # Launch browser (use headed mode so you can see and interact)
        print("🌐 Launching browser...")
        browser = await p.chromium.launch(
            headless=False,  # Keep browser visible
            args=[
                '--disable-web-security', 
                '--disable-features=VizDisplayCompositor',
                '--disable-blink-features=AutomationControlled',  # Hide automation
                '--no-first-run',
                '--disable-extensions-except',
                '--disable-extensions'
            ]
        )
        
        # Create new page
        page = await browser.new_page()
        
        # Make the browser look more like a regular user
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """)
        
        # Set a normal user agent
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Set up network monitoring
        page.on('request', capture.log_request)
        page.on('response', capture.log_response)
        
        print("🔍 Network monitoring active!")
        print("\nNow perform these steps manually in the browser:")
        print("1. Log into ClubOS")
        print("2. Navigate to the calendar")
        print("3. Find events to delete")
        print("4. Delete events using the UI")
        print("5. Observe what happens in the network traffic")
        
        # Navigate to ClubOS
        print("\n🚀 Opening ClubOS...")
        await page.goto("https://anytime.club-os.com")
        
        # Wait for user to complete manual workflow
        print("\n⏳ Waiting for you to complete the workflow...")
        print("   Press Ctrl+C when you're done to save the captured data")
        
        try:
            # Keep the script running until user stops it
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Capture stopped by user")
            
        # Save all captured data
        print("\n💾 Saving captured data...")
        await capture.save_captures()
        
        # Close browser
        await browser.close()
        
        print(f"\n✅ Capture complete! Check {capture.output_dir} for results")
        
        # Print summary of what was captured
        calendar_reqs = [r for r in capture.requests if 'calendar' in r['url'].lower()]
        event_reqs = [r for r in capture.requests if 'event' in r['url'].lower()]  
        delete_reqs = [r for r in capture.requests if any(kw in r['url'].lower() for kw in ['delete', 'remove'])]
        
        print("\n📊 CAPTURE SUMMARY:")
        print(f"   Total requests: {len(capture.requests)}")
        print(f"   Calendar requests: {len(calendar_reqs)}")
        print(f"   Event requests: {len(event_reqs)}")
        print(f"   Delete requests: {len(delete_reqs)}")
        
        if delete_reqs:
            print("\n🎯 DELETE REQUESTS FOUND:")
            for req in delete_reqs:
                print(f"   {req['method']} {req['url']}")
                if req['post_data']:
                    print(f"      Data: {req['post_data']}")

if __name__ == "__main__":
    asyncio.run(capture_manual_workflow())
