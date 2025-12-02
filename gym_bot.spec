# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Gym Bot Dashboard
This creates a standalone executable with all dependencies bundled
"""

import sys
import os
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

# CRITICAL: Add run_dashboard.py so launcher can start Flask server
datas += [('run_dashboard.py', '.')]

# Add VERSION file
if os.path.exists('VERSION'):
    datas += [('VERSION', '.')]  

# CRITICAL: Add src folder for auto-updater and other modules
if os.path.exists('src'):
    datas += [('src', 'src')]

# Add config folder for credentials
if os.path.exists('config'):
    datas += [('config', 'config')]

# Add optional files only if they exist
if os.path.exists('gym_bot.db'):
    datas += [('gym_bot.db', '.')]

if os.path.exists('email_config_example.env'):
    datas += [('email_config_example.env', '.')]

# Collect all submodules - but filter out test modules to reduce bloat
hiddenimports = []
hiddenimports += collect_submodules('flask')
hiddenimports += collect_submodules('jinja2')
hiddenimports += collect_submodules('werkzeug')
hiddenimports += collect_submodules('requests')
hiddenimports += collect_submodules('bs4')
hiddenimports += collect_submodules('cryptography')
hiddenimports += collect_submodules('anthropic')
hiddenimports += collect_submodules('aiohttp')

# Include pandas and numpy core modules only (NOT tests)
hiddenimports += [
    'pandas', 'pandas.core', 'pandas.io', 'pandas.api',
    'pandas._libs', 'pandas._config', 'pandas.compat',
    'numpy', 'numpy.core', 'numpy.lib', 'numpy.linalg',
    'numpy.fft', 'numpy.random', 'numpy.ma', 'numpy._typing',
]

# CRITICAL: Include socketio dependencies (used for real-time messaging)
hiddenimports += collect_submodules('flask_socketio')
hiddenimports += collect_submodules('socketio')
hiddenimports += collect_submodules('python_socketio')

# Include eventlet core only (NOT all submodules with tests)
hiddenimports += [
    'eventlet', 'eventlet.green', 'eventlet.green.socket',
    'eventlet.green.ssl', 'eventlet.green.threading',
    'eventlet.hubs', 'eventlet.hubs.hub', 'eventlet.hubs.poll',
    'eventlet.hubs.selects', 'eventlet.queue', 'eventlet.timeout',
    'eventlet.semaphore', 'eventlet.event', 'eventlet.greenpool',
    'eventlet.greenthread', 'eventlet.patcher', 'eventlet.support',
]

# CRITICAL: Include dotenv for environment loading
hiddenimports += ['dotenv']

# Include src submodules - filter to only needed ones
hiddenimports += [
    'src', 'src.main_app', 'src.config', 'src.routes', 'src.services', 
    'src.utils', 'src.monitoring', 'src.config.environment_setup',
]

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'scipy', 'pytest', 'IPython',
        # Exclude all test modules to reduce build size
        'pandas.tests', 'numpy.tests', 'numpy.f2py.tests',
        'eventlet.tests', 'aiohttp.test_utils',
        # Exclude other large optional modules
        'PIL', 'cv2', 'pyautogui',
        'google.cloud', 'google.api_core',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    console=True,  # CRITICAL: Enable console for debugging - set to False after testing
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
