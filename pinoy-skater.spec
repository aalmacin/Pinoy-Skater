# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['pinoy-skater_3.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('images', 'images'),
        ('sounds', 'sounds'),
    ],
    hiddenimports=[
        'cocos',
        'cocos.audio.pygame',
        'cocos.audio.pygame.mixer',
        'cocos.audio.pygame.music',
        'pyglet',
        'pygame',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='PinoySkater',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PinoySkater',
)
