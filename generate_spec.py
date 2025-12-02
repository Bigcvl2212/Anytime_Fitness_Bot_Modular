#!/usr/bin/env python3
"""Generate a fresh PyInstaller spec file for GymBot"""

import os

spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

datas = []
datas += collect_data_files('flask')
datas += collect_data_files('jinja2')
datas += collect_data_files('werkzeug')
datas += [('templates', 'templates')]
datas += [('static', 'static')]
datas += [('run_dashboard.py', '.')]
datas += [('setup_wizard.py', '.')]
datas += [('launcher.py', '.')]
datas += [('VERSION', '.')]
if os.path.exists('src'):
    datas += [('src', 'src')]
if os.path.exists('config'):
    datas += [('config', 'config')]

hiddenimports = []
hiddenimports += collect_submodules('flask')
hiddenimports += collect_submodules('jinja2')
hiddenimports += collect_submodules('werkzeug')
hiddenimports += collect_submodules('requests')
hiddenimports += collect_submodules('flask_socketio')
hiddenimports += collect_submodules('socketio')
hiddenimports += ['dotenv', 'src', 'src.main_app', 'src.config', 'src.routes', 'src.services', 'src.utils']

a = Analysis(
    ['launcher.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pytest', 'IPython', 'pandas.tests', 'numpy.tests'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GymBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GymBot',
)
'''

with open('gym_bot_fresh.spec', 'w') as f:
    f.write(spec_content)

print('Fresh spec file generated: gym_bot_fresh.spec')
