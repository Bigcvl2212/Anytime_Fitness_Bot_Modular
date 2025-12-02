# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['entry_v2.py'],
    pathex=[],
    binaries=[],
    datas=[('templates', 'templates'), ('static', 'static'), ('run_dashboard.py', '.'), ('gymbot_setup_wizard.py', '.'), ('VERSION', '.'), ('src', 'src'), ('config', 'config')],
    hiddenimports=['flask', 'jinja2', 'werkzeug', 'requests', 'flask_socketio', 'socketio', 'dotenv'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GymBot',
)
