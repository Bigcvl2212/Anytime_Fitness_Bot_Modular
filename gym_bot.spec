# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Gym Bot Dashboard
This creates a standalone executable with all dependencies bundled
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all data files from packages
datas = []
datas += collect_data_files('flask')
datas += collect_data_files('jinja2')
datas += collect_data_files('werkzeug')

# Add templates and static folders
datas += [('templates', 'templates')]
datas += [('static', 'static')]

# Add empty database schema
datas += [('gym_bot.db', '.')]

# Add config example
datas += [('email_config_example.env', '.')]

# Collect all submodules
hiddenimports = []
hiddenimports += collect_submodules('flask')
hiddenimports += collect_submodules('jinja2')
hiddenimports += collect_submodules('werkzeug')
hiddenimports += collect_submodules('requests')
hiddenimports += collect_submodules('bs4')
hiddenimports += collect_submodules('cryptography')
hiddenimports += collect_submodules('google.cloud')
hiddenimports += collect_submodules('anthropic')
hiddenimports += collect_submodules('aiohttp')
hiddenimports += ['src.main_app', 'src.config', 'src.routes', 'src.services', 'src.utils']

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pytest', 'IPython'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

import os

# Check if icon files exist
icon_win = 'static/favicon.ico' if os.path.exists('static/favicon.ico') else None
icon_mac = 'static/favicon.icns' if os.path.exists('static/favicon.icns') else None

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
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_win if sys.platform == 'win32' else None,
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

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='GymBot.app',
        icon=icon_mac,
        bundle_identifier='com.anytimefitness.gymbot',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
        },
    )
