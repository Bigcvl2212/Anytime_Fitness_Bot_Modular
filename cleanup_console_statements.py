#!/usr/bin/env python3
"""
Script to replace console.log statements with debug equivalents in template files.
This helps clean up production console output while maintaining debug capability.
"""

import os
import re

def clean_console_statements(file_path):
    """
    Replace console statements with debug equivalents in a single file.
    """
    try:
        # Try UTF-8 first
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            # Fallback to UTF-8 with error handling
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except:
            print(f"⚠️ Skipping {file_path} - encoding issues")
            return False
    
    original_content = content
    
    # Replace console.log with debugLog (excluding the debug function definitions)
    content = re.sub(
        r'(?<!function debug)console\.log\(', 
        'debugLog(', 
        content
    )
    
    # Replace console.error with debugError (excluding the debug function definitions)
    content = re.sub(
        r'(?<!function debug)console\.error\(', 
        'debugError(', 
        content
    )
    
    # Replace console.warn with debugWarn (excluding the debug function definitions)
    content = re.sub(
        r'(?<!function debug)console\.warn\(', 
        'debugWarn(', 
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated {file_path}")
        return True
    else:
        print(f"ℹ️ No changes needed in {file_path}")
        return False

def main():
    """Main function to process template files."""
    template_dir = "templates"
    
    if not os.path.exists(template_dir):
        print(f"❌ Template directory '{template_dir}' not found!")
        return
    
    files_processed = 0
    files_changed = 0
    
    # Process HTML template files
    for filename in os.listdir(template_dir):
        if filename.endswith('.html'):
            file_path = os.path.join(template_dir, filename)
            print(f"🔍 Processing {filename}...")
            
            files_processed += 1
            if clean_console_statements(file_path):
                files_changed += 1
    
    print(f"\n📊 Summary:")
    print(f"   Files processed: {files_processed}")
    print(f"   Files changed: {files_changed}")
    print(f"   Console cleanup complete! 🎉")

if __name__ == "__main__":
    main()