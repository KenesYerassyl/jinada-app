# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('db', 'db'),
        ('models', 'models'),
        ('resources', 'resources'),
        ('widgets', 'widgets'),
        ('utils', 'utils'),
    ],
    hiddenimports=['PyQt6.QtWidgets', 'PyQt6.QtGui', 'PyQt6.QtCore'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['__pycache__', '.gitignore', 'test.py', '.git'],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Jinada',
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
    icon='resources\icon_windows.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Jinada',
)
