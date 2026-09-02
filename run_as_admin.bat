@echo off
title Foco - Admin Setup
color 0A

echo.
echo  ====================================
echo   Foco
echo  ====================================
echo.
echo  This will launch the tracker with admin privileges
echo  for better window and application detection.
echo.

:: Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo  Running with admin privileges
    goto :run_app
) else (
    echo  Requesting admin privileges...
    echo.
    
    :: Request admin privileges
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:run_app
echo  Starting Foco...
echo.

:: Change to script directory
cd /d "%~dp0"

:: Run the Python application
python app_launcher.py

if %errorLevel% neq 0 (
    echo.
    echo  Error running the application.
    echo  Make sure Python and required packages are installed:
    echo  pip install psutil pywin32
    echo.
)

echo.
echo  Press any key to exit...
pause >nul
