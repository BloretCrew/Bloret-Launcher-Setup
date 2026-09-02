# PyInstaller Windows x64 single-file, windowed installer.
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("PyQt5")
a = Analysis(
    ["installer.py"],
    pathex=["."],
    binaries=[],
    datas=[("bloret.ico", ".")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["qfluentwidgets", "requests"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name="BloretLauncherSetup",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch="x64",
    icon="bloret.ico",
)
