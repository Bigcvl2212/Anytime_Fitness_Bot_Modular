import requests
import json

# Bearer token extracted from HAR file
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsIm5hbWUiOiJNYXlvLCBKZXJlbXkiLCJlbWFpbCI6Im1heW8uamVyZW15MjIxMkBnbWFpbC5jb20iLCJyb2xlIjoiQ2x1Ykh1Yklvc0FwaSJ9.QeEoZuoov4hw7-LN7XcuKWGn99HsDfhkDtJNHxr07ms"

def test_clubhub_api():
    """Test ClubHub API access using the Bearer token from HAR file"""
    
    headers = {
        'User-Agent': 'ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4',
        'Accept': 'application/json',
        'Accept-Language': 'en-US',
        'Accept-Encoding': 'br;q=1.0, gzip;q=0.9, deflate;q=0.8',
        'Connection': 'keep-alive',
        'API-version': '1',
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Cookie': 'dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy'
    }
    
    base_url = "https://clubhub-ios-api.anytimefitness.com"
    club_id = "1156"
    
    # Test 1: Get club features
    print("Testing ClubHub API access...")
    print("1. Testing club features endpoint...")
    
    try:
        response = requests.get(f"{base_url}/api/clubs/{club_id}/features", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Success! Club features endpoint works.")
        else:
            print(f"   Failed: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Get members
    print("\n2. Testing members endpoint...")
    try:
        response = requests.get(f"{base_url}/api/clubs/{club_id}/members/all", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success! Found {len(data)} members.")
            if data:
                print(f"   First member: {data[0].get('firstName', 'N/A')} {data[0].get('lastName', 'N/A')}")
        else:
            print(f"   Failed: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Get prospects
    print("\n3. Testing prospects endpoint...")
    try:
        response = requests.get(f"{base_url}/api/clubs/{club_id}/prospects?days=1&page=1&pageSize=50", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success! Found {len(data)} prospects.")
            if data:
                print(f"   First prospect: {data[0].get('firstName', 'N/A')} {data[0].get('lastName', 'N/A')}")
        else:
            print(f"   Failed: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_clubhub_api() 