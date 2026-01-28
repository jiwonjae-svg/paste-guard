@echo off
echo ================================
echo Paste Guardian - Setup
echo ================================
echo.

echo [1/3] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)
echo.

echo [2/3] Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)
echo.

echo [3/3] Setup complete!
echo.
echo ================================
echo You can now run Paste Guardian:
echo   python main.py
echo ================================
echo.
pause
