@echo off
echo MAR-PD Installer for Windows
echo =============================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed!
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install requests beautifulsoup4 lxml colorama tqdm fake-useragent

REM Create directories
echo Creating directories...
if not exist "data" mkdir data
if not exist "data\cache" mkdir data\cache
if not exist "results" mkdir results
if not exist "results\exports" mkdir results\exports
if not exist "results\logs" mkdir results\logs

echo.
echo Installation complete!
echo.
echo To run MAR-PD:
echo   python main.py
echo.
pause