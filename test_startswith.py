#!/usr/bin/env python3
"""Test startswith logic"""
content = 'Jeremy Mayocan you help me schedule'
print(f'Content: {content}')
print(f'Lowercase: {content.lower()}')
print(f'Starts with "jeremy mayo": {content.lower().startswith("jeremy mayo")}')

# The content is "jeremy mayocan..." which DOES start with "jeremy mayo"
# because "jeremy mayocan" starts with the substring "jeremy mayo"
