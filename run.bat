@echo off
echo ================================
echo Starting Paste Guardian...
echo ================================
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Paste Guardian
    echo Please make sure you have run setup.bat first
    pause
)
