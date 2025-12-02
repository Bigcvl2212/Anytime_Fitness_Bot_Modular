#!/usr/bin/env python3
"""Verify strings exist in compiled exe or internal files"""

import sys
import os

target_path = sys.argv[1] if len(sys.argv) > 1 else 'dist/GymBot'

strings = [b'Check Updates', b'options_frame', b'View Logs', b'open_settings', b'check_updates']
found_status = {s: False for s in strings}

print(f"Scanning {target_path} for strings...")

def scan_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
            for s in strings:
                if not found_status[s] and s in content:
                    print(f'FOUND {s.decode()} in {filepath}')
                    found_status[s] = True
    except Exception as e:
        pass

if os.path.isfile(target_path):
    scan_file(target_path)
elif os.path.isdir(target_path):
    for root, dirs, files in os.walk(target_path):
        for file in files:
            scan_file(os.path.join(root, file))

all_found = all(found_status.values())

for s, found in found_status.items():
    if not found:
        print(f'NOT FOUND: {s.decode()}')

if not all_found:
    print('\nWARNING: Some expected strings were not found in the compiled output!')
    print('This means the build might contain old code.')
    sys.exit(1)
else:
    print('\nSUCCESS: All expected strings found!')
