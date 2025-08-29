#!/usr/bin/env python3
"""
Final test script to verify the working prospects approach with unlimited pagination
Uses the exact same approach as update_contacts_from_source_workflow
"""

import requests
import time
import json

def test_final_prospects_approach():
    """Test the exact same approach used in update_contacts_from_source_workflow with unlimited pagination"""
    print("🔄 Testing final prospects approach with unlimited pagination...")
    
    # Use the exact same constants as the working function
    CLUBHUB_API_URL_PROSPECTS = "https://clubhub-ios-api.anytimefitness.com/api/v1.0/clubs/1156/prospects"
    CLUBHUB_HEADERS = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJlNVY4RFdVTUE0Q1dCMUFhOGpDTU1hTFNMTDNCR2RIMFZLQldPazZPME9uUkIweUVpUF9UMUFYNEdGWG1MTWJFa0ZjSmNhSm0zbjIwVEM3aUZVSmQxVzlnWk12VkRIY1F0TE1uOXZvSXk5UWhka3BIRHAyUndVVFR2WDJyM05SeEVwZHlPdVBWU19xWENXQmNBUHpnWjhVWktfbWZBSTBfUW40S1B0Wkdib3V3ZGJKcHRCWEhxY2ZUNzRUQy1oRUNCTnhIMWdyTkZLU19UeUhmcUpLdTZhMlBNd1A4MHZ5V0c4Si1LUnJyVlpPZXRuRzcyd2V5N1FBRUk3MHZqZlJjUFh0V1FBandXMk5DNFRhU0U2MndsMFRXT1BleEc2RmloRGR0SnpuVklkSER5SmV2a1l5TFlwaVZoTDllMXpTdFNSaVNhdHhaN18wVFFEb3hhYUU2ZTliOE5hVSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTIzODAxNjQsImV4cCI6MTc1MjQ2NjU2NCwiaWF0IjoxNzUyMzgwMTY0LCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.K1hiET3Bg_-CDhdUfK7Fus4smHFbZUTwHFYZbJcSXvA",
        "API-version": "1",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": "incap_ses_132_434694=pJ43Iiiq7AgIQwVIVvXUAX//b2gAAAAAcBM8Epq6mDANrol1AXD4VQ==; dtCookie=v_4_srv_2_sn_942031A186D4529AF35E56616641EB2B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_0_app-3A4b32026d63ce75ab_0_rcs-3Acss_1; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    }
    
    # Use the exact same parameters as the working function
    PARAMS_FOR_PROSPECTS_RECENT = { 
        "days": "10000", 
        "page": "1", 
        "pageSize": "100",
        "includeInactive": "true",
        "includeAll": "true", 
        "status": "all"
    }
    
    # Create session with the exact same headers
    session = requests.Session()
    session.headers.update(CLUBHUB_HEADERS)
    
    # Use the exact same URL and params approach as the working version
    all_prospects = []
    page = 1
    start_time = time.time()
    
    try:
        while True:
            # Update page parameter for each request - EXACT same as working version
            params = PARAMS_FOR_PROSPECTS_RECENT.copy()
            params["page"] = str(page)
            
            # Make request with the exact same parameters - EXACT same as working version
            print(f"📄 Fetching prospects page {page} with comprehensive parameters...")
            prospects_response = session.get(CLUBHUB_API_URL_PROSPECTS, params=params)
            
            if prospects_response.status_code != 200:
                print(f"❌ Prospects API error on page {page}: {prospects_response.status_code}")
                break
                
            prospects_data = prospects_response.json()
            
            # Handle both dictionary and direct list responses like the working version
            if isinstance(prospects_data, list):
                page_prospects = prospects_data
            elif isinstance(prospects_data, dict):
                page_prospects = prospects_data.get('prospects', [])
                if not page_prospects:
                    # Try other possible key names
                    for key in ['data', 'results', 'items', 'content']:
                        if key in prospects_data:
                            page_prospects = prospects_data[key]
                            break
            else:
                page_prospects = []
            
            if not page_prospects or len(page_prospects) == 0:
                print(f"📄 No more prospects found on page {page}")
                break
            
            all_prospects.extend(page_prospects)
            print(f"📄 Page {page}: Found {len(page_prospects)} prospects (Total so far: {len(all_prospects)})")
            
            # If we got less than the page size, we've reached the end
            if len(page_prospects) < int(params["pageSize"]):
                print(f"📄 Received less than full page size ({len(page_prospects)} < {params['pageSize']}). Reached end of data.")
                break
                
            page += 1
            
            # NO PAGE LIMIT - REMOVED TO GET ALL 9000+ PROSPECTS
            
            # Add a progress update every 10 pages
            if page % 10 == 0:
                elapsed = time.time() - start_time
                print(f"⏱️ Progress: {len(all_prospects)} prospects after {elapsed:.2f} seconds")
                
        # Done fetching all prospects
        elapsed = time.time() - start_time
        print(f"✅ Successfully fetched {len(all_prospects)} prospects in {elapsed:.2f} seconds")
        
        # Save all prospects to a file
        with open("final_prospects.json", "w") as f:
            json.dump(all_prospects, f)
            
        # Print some sample prospects
        print("\n📋 Sample prospects:")
        for i, prospect in enumerate(all_prospects[:5]):
            name = f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip()
            email = prospect.get('email', 'No email')
            print(f"  {i+1}. {name} - {email}")
            
        print(f"\n🎉 SUCCESS! Got {len(all_prospects)} prospects using the working approach!")
        
    except Exception as e:
        print(f"❌ Error getting prospects: {e}")
        
if __name__ == "__main__":
    test_final_prospects_approach()
