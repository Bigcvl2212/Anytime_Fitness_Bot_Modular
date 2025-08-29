import requests

# Test the breakthrough process
url = 'http://localhost:5000/api/training-clients/125814462/packages'
try:
    response = requests.get(url, timeout=30)
    data = response.json()
    print('Request successful')
    print(f'GUID found: {data.get("debug_guid")}')
    print(f'Packages count: {data.get("debug_packages_count")}')
    print(f'Active packages: {data.get("active_packages")}')
    print(f'Past due: {data.get("debug_past_due")}')
except Exception as e:
    print(f'Error: {e}')
