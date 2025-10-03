@echo off
title ADHD Productivity Enforcer - FOCUS MODE
color 0C
echo.
echo  ==========================================
echo   🔒 PRODUCTIVITY ENFORCER - JAIL MODE
echo  ==========================================
echo.
echo  WARNING: This will block ALL distracting websites and apps!
echo  Only work/study tools will be accessible.
echo.
echo  BLOCKED: Reddit, YouTube (except educational), Games, Social Media
echo  ALLOWED: VS Code, IDEs, NeetCode, Lectures, GeeksforGeeks
echo.

:: Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo  ✅ Running with admin privileges
    goto :show_menu
) else (
    echo  ❌ ADMIN PRIVILEGES REQUIRED!
    echo  Right-click this file and select "Run as Administrator"
    echo.
    pause
    exit /b
)

:show_menu
echo  📋 Choose your focus session:
echo.
echo  [1] 8-hour WORK DAY (Full productivity jail)
echo  [2] 4-hour STUDY SESSION
echo  [3] 2-hour FOCUS BLOCK  
echo  [4] Custom duration
echo  [5] EMERGENCY DISABLE (Stop blocking)
echo  [6] Exit
echo.

set /p choice="Enter choice (1-6): "

cd /d "%~dp0"

if "%choice%"=="1" (
    echo.
    echo  🔒 Starting 8-hour productivity jail...
    python productivity_enforcer.py
) else if "%choice%"=="2" (
    echo.
    echo  📚 Starting 4-hour study session...
    python productivity_enforcer.py
) else if "%choice%"=="3" (
    echo.
    echo  ⏰ Starting 2-hour focus block...
    python productivity_enforcer.py
) else if "%choice%"=="4" (
    echo.
    echo  ⚙️ Starting custom session...
    python productivity_enforcer.py
) else if "%choice%"=="5" (
    echo.
    echo  🚨 EMERGENCY DISABLE - Removing all blocks...
    python -c "from productivity_enforcer import ProductivityEnforcer; ProductivityEnforcer().stop_enforcement()"
    echo.
    echo  ✅ All restrictions removed!
    pause
) else if "%choice%"=="6" (
    echo  Goodbye! 👋
    exit /b
) else (
    echo  ❌ Invalid choice
    pause
    goto :show_menu
)

echo.
echo  Press any key to exit...
pause >nul