import sys
import os
import csv
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services'))

from api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

# Import ClubOS APIs
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI
from config.clubhub_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD

def main():
    print("💰 INVESTIGATING: Dennis's Past Due Amount and Payment Details")
    print("=" * 70)
    
    # Authenticate
    client = ClubHubAPIClient()
    training_api = ClubOSTrainingPackageAPI()
    
    if not (client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD) and training_api.authenticate()):
        print("❌ Authentication failed")
        return
    
    print("✅ APIs authenticated")
    
    # Get Dennis's IDs from CSV
    csv_file_path = r"c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\data\csv_exports\master_contact_list_with_agreements_20250722_180712.csv"
    dennis_csv_data = None
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if 'DENNIS' in row.get('firstName', '').upper() and 'ROST' in row.get('lastName', '').upper():
                dennis_csv_data = row
                break
    
    if not dennis_csv_data:
        print("❌ Dennis not found in CSV")
        return
    
    print(f"👤 Dennis Rost - ID Collection:")
    dennis_ids = [
        ("ClubHub ID", dennis_csv_data.get('id')),
        ("Agreement ID", dennis_csv_data.get('agreement_agreementID')),
        ("User ID", dennis_csv_data.get('userId')),
        ("Agreement Member ID", dennis_csv_data.get('agreementHistory_memberId')),
    ]
    
    for name, id_val in dennis_ids:
        print(f"   {name}: {id_val}")
    
    print(f"\n🔍 EXPLORING ClubOS API Methods for Payment Details...")
    
    # Check what methods are available on the training API
    api_methods = [method for method in dir(training_api) if not method.startswith('_') and callable(getattr(training_api, method))]
    print(f"📋 Available API methods:")
    for method in api_methods:
        print(f"   - {method}")
    
    print(f"\n💰 TESTING: Different approaches to get Dennis's payment data...")
    
    for name, test_id in dennis_ids:
        if not test_id or test_id == '0':
            continue
            
        print(f"\n🔍 Testing {name} ({test_id}):")
        
        # Try get_member_payment_status (we know this returns None)
        try:
            payment_status = training_api.get_member_payment_status(test_id)
            print(f"   📊 get_member_payment_status(): {payment_status}")
        except Exception as e:
            print(f"   ❌ get_member_payment_status() error: {e}")
        
        # Try other methods that might exist
        potential_methods = [
            'get_member_balance',
            'get_member_debt', 
            'get_member_outstanding',
            'get_member_account',
            'get_member_financial',
            'get_member_billing',
            'get_payment_history',
            'get_account_balance',
            'get_member_details',
            'get_member_info',
            'get_member_data',
            'get_training_balance',
            'get_training_debt'
        ]
        
        for method_name in potential_methods:
            if hasattr(training_api, method_name):
                try:
                    method = getattr(training_api, method_name)
                    result = method(test_id)
                    print(f"   💰 {method_name}(): {result}")
                except Exception as e:
                    print(f"   ⚠️ {method_name}() error: {e}")
    
    # Try direct API exploration
    print(f"\n🔬 DIRECT API EXPLORATION:")
    print(f"Let's check the training_api object structure...")
    
    # Check if there's a client or session we can inspect
    if hasattr(training_api, 'client'):
        print(f"   📡 Has client attribute")
    if hasattr(training_api, 'session'):
        print(f"   📡 Has session attribute") 
    if hasattr(training_api, 'base_url'):
        print(f"   🌐 Base URL: {training_api.base_url}")
    
    # Check the actual ClubOS API file to see what endpoints are available
    print(f"\n📖 Let's examine the ClubOS training API source code...")
    
    try:
        import inspect
        source_file = inspect.getfile(ClubOSTrainingPackageAPI)
        print(f"   📁 API file location: {source_file}")
        
        # Read the source to see what endpoints exist
        with open(source_file, 'r') as f:
            content = f.read()
            
        # Look for API endpoints or URLs
        lines = content.split('\n')
        endpoints = []
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['url', 'endpoint', 'api/', 'get', 'post']):
                if any(payment_term in line.lower() for payment_term in ['payment', 'balance', 'debt', 'amount', 'financial']):
                    endpoints.append(f"Line {i+1}: {line.strip()}")
        
        if endpoints:
            print(f"   💰 Found potential payment-related endpoints:")
            for endpoint in endpoints[:10]:  # Show first 10
                print(f"     {endpoint}")
        else:
            print(f"   ❌ No obvious payment endpoints found")
            
    except Exception as e:
        print(f"   ⚠️ Could not examine source: {e}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"1. 📖 Manually check ClubOS interface for Dennis's account")
    print(f"2. 🔍 Look for other ClubOS API endpoints that handle billing/payments")
    print(f"3. 💰 Check if there's a separate billing/accounting API")
    print(f"4. 📋 See if the master contact list CSV has payment amount columns")

if __name__ == "__main__":
    main()
