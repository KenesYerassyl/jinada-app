# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('db', 'db'),
        ('models', 'models'),
        ('resources', 'resources'),
        ('widgets', 'widgets'),
        ('utils', 'utils'),
        ('deep-person-reid', 'deep-person-reid'),
    ],
    hiddenimports=[],
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
    name='Jinada',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=True,
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
    name='Jinada',
)
app = BUNDLE(
    coll,
    name='Jinada.app',
    icon='resources/icon_macosx.icns',
    bundle_identifier='com.yerassyl.Jinada',
)