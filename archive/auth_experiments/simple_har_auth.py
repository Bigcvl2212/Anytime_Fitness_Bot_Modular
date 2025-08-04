import json
import os

def find_login_requests():
    """Find login requests in HAR files without unicode symbols"""
    
    print("HAR Authentication Flow Analyzer")
    print("=" * 50)
    
    # Get all HAR files in charles_session.chls directory
    charles_dir = "charles_session.chls"
    if not os.path.exists(charles_dir):
        print(f"Directory {charles_dir} not found!")
        return
    
    har_files = [f for f in os.listdir(charles_dir) if f.endswith('.har')]
    if not har_files:
        print(f"No HAR files found in {charles_dir}!")
        return
    
    print(f"Found {len(har_files)} HAR files to analyze...")
    print()
    
    login_found = False
    
    for har_file in har_files:
        filepath = os.path.join(charles_dir, har_file)
        print(f"Analyzing: {har_file}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Read line by line to find login patterns
                line_num = 0
                for line in f:
                    line_num += 1
                    
                    # Search for login URLs
                    if any(pattern in line.lower() for pattern in [
                        '/auth/sign_in', '/auth/login', '/login', '/signin',
                        'clubhub-ios-api', '/auth', 'authentication'
                    ]):
                        print(f"  Found potential login at line {line_num}")
                        print(f"  Content: {line[:100]}...")
                        login_found = True
                        
                        # Try to find the full request block
                        # Reset file pointer and read as JSON
                        break
                        
        except Exception as e:
            print(f"  Error reading {har_file}: {e}")
            continue
            
        print()
    
    if not login_found:
        print("No login requests found in any HAR files")
        print("Let's check what endpoints ARE in the files...")
        
        # Check what endpoints exist
        for har_file in har_files[:2]:  # Check first 2 files
            filepath = os.path.join(charles_dir, har_file)
            print(f"\nChecking endpoints in: {har_file}")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Look for URL patterns
                    import re
                    urls = re.findall(r'"url":\s*"([^"]+)"', content)
                    unique_urls = list(set(urls))[:10]  # First 10 unique URLs
                    
                    for url in unique_urls:
                        print(f"  {url}")
                        
            except Exception as e:
                print(f"  Error: {e}")

if __name__ == "__main__":
    find_login_requests()
