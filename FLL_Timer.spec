# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['FLL_Timer.py'],
    pathex=[],
    binaries=[],
    datas=[('fll_logo.png', '.'), ('charge.wav', '.'), ('dingding.wav', '.'), ('laser.wav', '.'), ('buzzer.wav', '.')],
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
    a.binaries,
    a.datas,
    [],
    name='FLL_Timer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['fll_icon.ico'],
)
