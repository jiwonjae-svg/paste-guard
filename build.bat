@echo off
REM Build Paste Guardian executable
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

REM Build with PyInstaller
echo [2/3] Building executable...
pyinstaller --clean --onefile --noconsole --name PasteGuardian ^
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
    main.py

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
    echo ================================================
) else (
    echo ERROR: Executable not found!
)

echo.
pause
