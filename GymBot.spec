# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gymbot_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('VERSION', '.'),
        ('build_info.txt', '.'),
        ('config', 'config'),
        ('src', 'src'),
    ],
    hiddenimports=[
        # Flask core
        'flask',
        'flask_socketio',
        'flask_talisman',
        'flask_wtf',
        'wtforms',
        'jinja2',
        # SocketIO / async
        'engineio',
        'engineio.async_drivers.threading',
        'engineio.async_drivers.eventlet',
        'socketio',
        'eventlet',
        'eventlet.hubs.epolls',
        'eventlet.hubs.kqueue',
        'eventlet.hubs.selects',
        'dns',
        'dns.resolver',
        # HTTP / scraping
        'requests',
        'urllib3',
        'bs4',
        'lxml',
        'lxml.etree',
        # Data
        'pandas',
        'numpy',
        # Security / crypto
        'cryptography',
        'cryptography.fernet',
        'bcrypt',
        # AI
        'anthropic',
        'aiohttp',
        # Payments
        'square',
        'squareup',
        'squareup.client',
        # Scheduler
        'apscheduler',
        'apscheduler.schedulers.background',
        'apscheduler.triggers.cron',
        'apscheduler.triggers.interval',
        # Misc
        'dotenv',
        'psutil',
        'validators',
        'bleach',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'tkinter.test', 'unittest'],
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
