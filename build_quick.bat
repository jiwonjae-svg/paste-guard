@echo off
REM ==============================================================================
REM Quick Build - Single Command Version
REM ==============================================================================
REM 
REM This is the fastest way to build PasteGuardian.exe with icon
REM 
REM Requirements:
REM - icon.ico must exist in project root folder
REM - PyInstaller must be installed: pip install pyinstaller
REM
REM ==============================================================================

echo Building PasteGuardian.exe with embedded icon...
echo.

pyinstaller --clean --onefile --noconsole ^
    --name PasteGuardian ^
    --icon=icon.ico ^
    --hidden-import=customtkinter ^
    --hidden-import=pynput ^
    --hidden-import=pyperclip ^
    --hidden-import=psutil ^
    --hidden-import=pystray ^
    --hidden-import=PIL ^
    --hidden-import=PIL.ImageGrab ^
    --hidden-import=win32api ^
    --hidden-import=win32con ^
    --hidden-import=win32gui ^
    --hidden-import=win32ui ^
    --hidden-import=win32process ^
    --hidden-import=win32clipboard ^
    --hidden-import=win32event ^
    --hidden-import=winerror ^
    --hidden-import=win10toast ^
    main.py

echo.
echo Build complete!
echo.
echo [TIP] If icon doesn't appear in Windows Explorer:
echo 1. Clear icon cache: del /f /s /q /a "%%LocalAppData%%\IconCache.db"
echo 2. Restart Explorer: taskkill /f /im explorer.exe ^&^& start explorer.exe
echo.

pause
