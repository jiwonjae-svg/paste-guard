# Build configuration for Paste Guardian
# PyInstaller spec file - Single file build with embedded icon

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],  # No external data files needed - icon is embedded in code
    hiddenimports=[
        'customtkinter',
        'pynput',
        'pyperclip',
        'psutil',
        'pywin32',
        'pystray',
        'PIL',
        'PIL.ImageGrab',
        'win32api',
        'win32con',
        'win32gui',
        'win32ui',
        'win32process',
        'win32clipboard',
        'win32event',
        'winerror',
        'win10toast'
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PasteGuardian',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI application)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # =========================================================================
    # ICON CONFIGURATION - Embeds icon.ico into the .exe file
    # =========================================================================
    # This sets the icon that appears in Windows Explorer, taskbar, etc.
    # File must exist in project root: icon.ico
    # 
    # If icon doesn't update after build:
    # 1. Delete Windows icon cache:
    #    del /f /s /q /a "%LocalAppData%\IconCache.db"
    # 2. Restart Windows Explorer:
    #    taskkill /f /im explorer.exe && start explorer.exe
    # 3. Or use: ie4uinit.exe -ClearIconCache
    # =========================================================================
    icon='icon.ico'  # Path to icon file (relative to project root)
)
