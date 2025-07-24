#!/usr/bin/env python3

# Test syntax by importing parts of the file

def test_syntax():
    """Test syntax of gym_bot_dashboard.py by line numbers."""
    
    with open('gym_bot_dashboard.py', 'r') as f:
        lines = f.readlines()
    
    # Test up to line 1163 (before the error)
    test_code = ''.join(lines[:1163])
    
    try:
        compile(test_code, 'test', 'exec')
        print("Lines 1-1163: OK")
    except SyntaxError as e:
        print(f"Syntax error in lines 1-1163: {e}")
        print(f"Error at line {e.lineno}: {lines[e.lineno-1].strip() if e.lineno <= len(lines) else 'EOF'}")
        return
    
    # Test up to line 1164 (the error line)
    test_code = ''.join(lines[:1164])
    
    try:
        compile(test_code, 'test', 'exec')
        print("Lines 1-1164: OK")
    except SyntaxError as e:
        print(f"Syntax error in lines 1-1164: {e}")
        print(f"Error at line {e.lineno}: {lines[e.lineno-1].strip() if e.lineno <= len(lines) else 'EOF'}")

if __name__ == '__main__':
    test_syntax()
