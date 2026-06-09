# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['displaybridge.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'win32api', 'win32con', 'win32gui', 'win32process',
        'pystray._win32',
        'PIL', 'PIL.Image', 'PIL.ImageDraw',
        'six',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['keyboard', 'matplotlib', 'numpy', 'scipy', 'pandas'],
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
    name='DisplayBridge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    uac_admin=False,
    icon='displaybridge.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='DisplayBridge',
)
