#!/usr/bin/env python3
"""Verify strings exist in compiled exe"""

import sys

exe_path = sys.argv[1] if len(sys.argv) > 1 else 'dist/GymBot/GymBot.exe'

with open(exe_path, 'rb') as f:
    content = f.read()

strings = [b'Check Updates', b'options_frame', b'View Logs', b'open_settings', b'check_updates']
all_found = True

for s in strings:
    if s in content:
        print(f'FOUND in exe: {s.decode()}')
    else:
        print(f'NOT FOUND in exe: {s.decode()}')
        all_found = False

if not all_found:
    print('\nWARNING: Some expected strings were not found in the compiled exe!')
    print('This means the exe was compiled from old code.')
    sys.exit(1)
else:
    print('\nSUCCESS: All expected strings found in exe!')
