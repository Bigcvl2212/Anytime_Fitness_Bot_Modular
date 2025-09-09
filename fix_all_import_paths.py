#!/usr/bin/env python3
"""
Comprehensive script to fix ALL import paths after services directory restructure.
This script will systematically update all imports from 'services.' to 'src.services.'
"""
import os
import re
import sys
from pathlib import Path

def fix_import_paths():
    """Fix all import paths systematically"""
    # Get the workspace root
    workspace_root = Path("c:/Users/mayoj/OneDrive/Documents/Gym-Bot/gym-bot/gym-bot-modular")
    
    # Patterns to find and replace
    patterns_to_fix = [
        # Direct imports
        (r'from services\.', 'from src.services.'),
        (r'import services\.', 'import src.services.'),
        # Absolute imports
        (r'from src.services ', 'from src.services '),
        (r'import services$', 'import src.services'),
    ]
    
    # File extensions to process
    extensions = ['.py']
    
    # Files to process
    files_to_process = []
    
    # Find all Python files
    for root, dirs, files in os.walk(workspace_root):
        # Skip .venv and other virtual environment directories
        dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', '.git', 'venv', 'env']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                files_to_process.append(Path(root) / file)
    
    print(f"Found {len(files_to_process)} Python files to process...")
    
    # Process each file
    fixed_files = 0
    total_replacements = 0
    
    for file_path in files_to_process:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_replacements = 0
            
            # Apply all patterns
            for pattern, replacement in patterns_to_fix:
                new_content, count = re.subn(pattern, replacement, content)
                if count > 0:
                    content = new_content
                    file_replacements += count
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Fixed {file_replacements} imports in {file_path.relative_to(workspace_root)}")
                fixed_files += 1
                total_replacements += file_replacements
                
        except Exception as e:
            print(f"❌ Error processing {file_path.relative_to(workspace_root)}: {e}")
    
    print(f"\n🎉 COMPLETE: Fixed {total_replacements} import statements across {fixed_files} files")
    
    # Special cases that need manual attention
    print("\n📋 SPECIAL CASES TO VERIFY:")
    
    # Check for any remaining 'from services' that might need manual attention
    remaining_issues = []
    for file_path in files_to_process:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'from services' in line or 'import services' in line:
                    if not line.strip().startswith('#'):  # Skip comments
                        remaining_issues.append(f"{file_path.relative_to(workspace_root)}:{i} - {line.strip()}")
        except:
            continue
    
    if remaining_issues:
        print("⚠️  Found potential remaining issues:")
        for issue in remaining_issues[:10]:  # Show first 10
            print(f"   {issue}")
        if len(remaining_issues) > 10:
            print(f"   ... and {len(remaining_issues) - 10} more")
    else:
        print("✅ No remaining 'services' imports found!")
    
    return fixed_files, total_replacements

if __name__ == "__main__":
    print("🔧 Starting comprehensive import path fix...")
    fixed_files, total_replacements = fix_import_paths()
    
    print(f"\n🏁 SUMMARY:")
    print(f"   • Files modified: {fixed_files}")
    print(f"   • Import statements fixed: {total_replacements}")
    print(f"   • Ready for testing!")
