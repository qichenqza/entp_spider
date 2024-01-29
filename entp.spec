# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['entp.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('deps/onnxruntime_providers_shared.dll', 'onnxruntime\capi'),
        ('deps/common.onnx', 'ddddocr'),
        ('deps/common_old.onnx', 'ddddocr'),
        ('example', 'example'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='entp',
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
    name='entp',
)
