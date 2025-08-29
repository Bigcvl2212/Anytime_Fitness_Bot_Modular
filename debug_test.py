import requests

# Test different API endpoints to find the working one
url = 'http://localhost:5000/api/debug/test-auth/125814462'
try:
    response = requests.get(url, timeout=30)
    data = response.json()
    print('=== DEBUG ENDPOINT TEST ===')
    print(f'Status Code: {response.status_code}')
    print(f'Success: {data.get("success", False)}')
    if 'error' in data:
        print(f'Error: {data["error"]}')
        if 'response_status' in data:
            print(f'Response Status: {data["response_status"]}')
        if 'response_text' in data:
            print(f'Response Text: {data["response_text"][:200]}...')

    # Now test the packages endpoint
    print('\n=== PACKAGES ENDPOINT TEST ===')
    packages_url = 'http://localhost:5000/api/training-clients/125814462/packages'
    packages_response = requests.get(packages_url, timeout=30)
    packages_data = packages_response.json()
    print(f'Packages Status: {packages_response.status_code}')
    print(f'Packages Success: {packages_data.get("success", False)}')
    print(f'Active Packages: {packages_data.get("active_packages", [])}')
    print(f'Past Due: {packages_data.get("debug_past_due", 0)}')
    print(f'GUID: {packages_data.get("debug_guid")}')

    # Test alternative endpoints that might work
    print('\n=== TESTING ALTERNATIVE ENDPOINTS ===')

    # Test member agreements endpoint
    member_agreements_url = 'http://localhost:5000/api/debug/test-member-agreements/125814462'
    try:
        member_response = requests.get(member_agreements_url, timeout=30)
        member_data = member_response.json()
        print(f'Member Agreements Status: {member_response.status_code}')
        print(f'Member Agreements Success: {member_data.get("success", False)}')
        if 'agreements' in member_data:
            print(f'Found {len(member_data["agreements"])} agreements')
    except Exception as e:
        print(f'Member Agreements Error: {e}')

    # Test training clients endpoint
    training_clients_url = 'http://localhost:5000/api/debug/test-training-clients'
    try:
        training_response = requests.get(training_clients_url, timeout=30)
        training_data = training_response.json()
        print(f'Training Clients Status: {training_response.status_code}')
        print(f'Training Clients Success: {training_data.get("success", False)}')
        if 'clients' in training_data:
            print(f'Found {len(training_data["clients"])} training clients')
    except Exception as e:
        print(f'Training Clients Error: {e}')

except Exception as e:
    print(f'Error: {e}')
