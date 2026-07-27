@echo off
echo.
echo  Hostel Feedback System
echo  ======================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python is not installed or not in PATH.
    echo  Download from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install dependencies if needed
echo  Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo  Starting server at http://localhost:5000
echo  Press Ctrl+C to stop.
echo.

python app.py

pause
