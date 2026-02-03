@echo off
REM ==============================================================================
REM Paste Guardian Build Script
REM ==============================================================================
REM 
REM Builds PasteGuardian.exe with embedded icon.ico
REM 
REM Icon Cache Refresh (if icon doesn't update):
REM   Method 1: del /f /s /q /a "%LocalAppData%\IconCache.db"
REM   Method 2: taskkill /f /im explorer.exe && start explorer.exe
REM   Method 3: ie4uinit.exe -ClearIconCache
REM   Method 4: Run refresh_icon_cache.ps1
REM
REM ==============================================================================

echo ================================================
echo Building Paste Guardian
echo ================================================
echo.

REM Clean previous build
echo [1/3] Cleaning previous build...
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"
if exist "PasteGuardian.exe" del /q "PasteGuardian.exe"
echo Done.
echo.

REM Build with PyInstaller using spec file
echo [2/3] Building executable with embedded icon...
echo Using: build.spec (icon=icon.ico)
pyinstaller build.spec

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo Done.
echo.

REM Copy executable to root directory
echo [3/3] Copying executable...
if exist "dist\PasteGuardian.exe" (
    copy "dist\PasteGuardian.exe" "PasteGuardian.exe"
    echo Done.
    echo.
    echo ================================================
    echo Build completed successfully!
    echo Executable: PasteGuardian.exe
    echo Icon: Embedded (icon.ico)
    echo ================================================
    echo.
    echo [TIP] If icon doesn't show in Windows Explorer:
    echo   1. Run: refresh_icon_cache.ps1 (PowerShell)
    echo   2. Or manually: del /f /s /q /a "%%LocalAppData%%\IconCache.db"
    echo   3. Then restart: taskkill /f /im explorer.exe ^&^& start explorer.exe
    echo.
) else (
    echo ERROR: Executable not found!
)

echo.
pause
