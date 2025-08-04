#!/usr/bin/env python3
"""
Extract the working deletion request from the HAR file
"""
import json
import sys

def extract_deletion_requests():
    """Extract deletion-related requests from the HAR file"""
    
    try:
        print("🔍 Reading HAR file...")
        
        with open("charles_session.chls/clubos_calendar_flow.har", "r", encoding="utf-8") as f:
            har_data = json.load(f)
        
        print(f"✅ HAR file loaded successfully")
        
        entries = har_data.get("log", {}).get("entries", [])
        print(f"📊 Found {len(entries)} HTTP requests")
        
        deletion_requests = []
        
        for i, entry in enumerate(entries):
            request = entry.get("request", {})
            url = request.get("url", "")
            method = request.get("method", "")
            
            # Look for deletion-related requests
            if any(keyword in url.lower() for keyword in ["remove", "delete", "eventpopup"]):
                deletion_requests.append({
                    "index": i,
                    "method": method,
                    "url": url,
                    "headers": request.get("headers", []),
                    "postData": request.get("postData", {}),
                    "response": entry.get("response", {})
                })
                print(f"\n🎯 FOUND DELETION REQUEST #{len(deletion_requests)}:")
                print(f"   Method: {method}")
                print(f"   URL: {url}")
        
        if not deletion_requests:
            # Look for EventPopup requests specifically
            print("\n🔍 Searching for EventPopup requests...")
            for i, entry in enumerate(entries):
                request = entry.get("request", {})
                url = request.get("url", "")
                
                if "EventPopup" in url:
                    print(f"\n📋 EventPopup request found:")
                    print(f"   Method: {request.get('method')}")
                    print(f"   URL: {url}")
                    print(f"   PostData: {request.get('postData', {})}")
        
        if deletion_requests:
            print(f"\n✅ Found {len(deletion_requests)} deletion-related requests")
            
            # Show the most promising deletion request
            for req in deletion_requests:
                print(f"\n🔥 DELETION REQUEST DETAILS:")
                print(f"Method: {req['method']}")
                print(f"URL: {req['url']}")
                
                post_data = req.get('postData', {})
                if post_data:
                    print(f"Content-Type: {post_data.get('mimeType', 'N/A')}")
                    
                    if 'text' in post_data:
                        print(f"Form Data: {post_data['text'][:500]}...")
                    
                    if 'params' in post_data:
                        print("Form Parameters:")
                        for param in post_data['params']:
                            print(f"   {param.get('name')}: {param.get('value')}")
                
                print(f"Headers:")
                for header in req['headers']:
                    print(f"   {header.get('name')}: {header.get('value')}")
                
                response = req.get('response', {})
                print(f"Response Status: {response.get('status')}")
                print(f"Response Text: {response.get('content', {}).get('text', '')[:200]}...")
        
        else:
            print("\n❌ No deletion requests found")
            print("Let me search for any calendar-related POST requests...")
            
            calendar_posts = []
            for i, entry in enumerate(entries):
                request = entry.get("request", {})
                url = request.get("url", "")
                method = request.get("method", "")
                
                if method == "POST" and "calendar" in url.lower():
                    calendar_posts.append({
                        "method": method,
                        "url": url,
                        "postData": request.get("postData", {})
                    })
            
            print(f"Found {len(calendar_posts)} calendar POST requests:")
            for post in calendar_posts:
                print(f"   {post['method']} {post['url']}")
        
        return deletion_requests
        
    except Exception as e:
        print(f"❌ Error reading HAR file: {e}")
        return []

if __name__ == "__main__":
    extract_deletion_requests()
