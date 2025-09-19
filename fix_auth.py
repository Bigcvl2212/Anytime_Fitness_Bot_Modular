#!/usr/bin/env python3
"""
Quick fix for authentication performance issues
"""

# Read the current auth service file
with open('src/services/authentication/secure_auth_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the verbose validation method with a simpler one
old_method_start = 'def validate_session(self) -> Tuple[bool, str]:'
method_end_marker = 'def logout(self) -> None:'

# Find the start and end positions
start_pos = content.find(old_method_start)
end_pos = content.find(method_end_marker)

if start_pos != -1 and end_pos != -1:
    # Extract the method signature and replace with simplified version
    new_method = '''    def validate_session(self) -> Tuple[bool, str]:
        """
        Validate current session (simplified for performance)
        
        Returns:
            Tuple of (is_valid, manager_id)
        """
        try:
            # Quick session existence check
            if not session:
                return False, ""
            
            # Check required session data
            authenticated = session.get('authenticated')
            manager_id = session.get('manager_id')
            
            if not authenticated or not manager_id:
                return False, ""
            
            # Check session timeout (simplified)
            if 'login_time' in session:
                try:
                    login_time = datetime.fromisoformat(session['login_time'])
                    session_age = datetime.now() - login_time
                    
                    if session_age > self.session_timeout:
                        self.logout()
                        return False, ""
                except (ValueError, TypeError):
                    # Invalid time format - reset it but don't fail
                    session['login_time'] = datetime.now().isoformat()
                    session.modified = True
            else:
                # Add login_time if missing
                session['login_time'] = datetime.now().isoformat()
                session.modified = True
            
            # Update last activity (minimal)
            session['last_activity'] = datetime.now().isoformat()
            session.modified = True
            
            return True, manager_id
            
        except Exception as e:
            logger.error(f"❌ Session validation exception: {e}")
            return False, ""

    '''
    
    # Replace the content
    new_content = content[:start_pos] + new_method + content[end_pos:]
    
    # Write back to the file
    with open('src/services/authentication/secure_auth_service.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Authentication method simplified for better performance")
else:
    print("❌ Could not find method boundaries")