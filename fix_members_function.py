#!/usr/bin/env python3
"""
Script to replace the slow members_page function with a fast version
"""
import re

def replace_members_function():
    """Replace the slow members_page function with a fast version"""
    
    # Read the current file
    with open('src/clean_dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the fast function replacement
    fast_function = '''@app.route('/members')
def members_page():
    """Display members page with fast loading - data loads asynchronously via JavaScript."""
    
    logger.info("📋 Members page loaded - using fast loading with existing database data")
    
    # Get simple counts from database for initial display (fast operation)
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]
    
    conn.close()
    
    # Fast page load - render template immediately with minimal data
    # JavaScript will load the actual member data and category counts asynchronously
    return render_template('members.html',
                         members=[],  # Empty initially, loaded via JavaScript
                         total_members=total_members,
                         statuses=[],
                         search='',
                         status_filter='',
                         page=1,
                         total_pages=1,
                         per_page=50)'''
    
    # Find the pattern for the members_page function and replace it
    # Match from @app.route('/members') to the next @app.route or end of function
    pattern = r'@app\.route\(\'/members\'\)\s*def members_page\(\):.*?(?=@app\.route|\Z)'
    
    # Find the function first to see if it exists
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        print(f"Found members_page function at position {match.start()} to {match.end()}")
        # Replace the function
        new_content = re.sub(pattern, fast_function + '\n\n', content, flags=re.DOTALL)
        
        # Write the updated content back
        with open('src/clean_dashboard.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print('✅ Successfully replaced members_page function with fast version')
        return True
    else:
        print('❌ Could not find members_page function to replace')
        return False

if __name__ == '__main__':
    replace_members_function()
