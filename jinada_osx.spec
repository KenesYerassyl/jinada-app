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
    ],
    hiddenimports=[
            'altgraph', 'certifi', 'contourpy', 'cvzone', 'cycler', 'filelock', 'fsspec', 'idna', 'tensorboard',
            'kiwisolver', 'lap', 'macholib', 'matplotlib', 'mpmath', 'networkx', 'numpy', 'packaging', 'pandas', 
            'psutil', 'pyparsing', 'PyQt6', 'pytz', 'requests', 'scipy', 'seaborn', 'six', 'sympy', 
            'torch', 'torchvision', 'tqdm', 'typing_extensions', 'tzdata', 'ultralytics', 'urllib3'
        ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['__pycache__', '.gitignore', 'builddmg.sh', 'test.py',  '.git'],
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
    upx=False,
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=True,
    target_arch=None,
    codesign_identity='Apple Development: kenesyerassyl@gmail.com (U3CCJ6RP8M)',
    entitlements_file='entitlements.plist',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Jinada',
)
app = BUNDLE(
    coll,
    name='Jinada.app',
    icon='resources/icon_macosx.icns',
    bundle_identifier='com.yerassyl.Jinada',
)