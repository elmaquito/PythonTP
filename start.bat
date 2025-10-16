@echo off
echo.
echo =================================================
echo   Restaurant Access Control System
echo =================================================
echo.
echo Choose version to run:
echo [1] Full Application (with authentication)
echo [2] Demo Version (quick start, no dependencies)
echo [3] Launcher Menu
echo [4] Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting full application...
    ".venv\Scripts\python.exe" main.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo Starting demo version...
    ".venv\Scripts\python.exe" demo.py
    pause
) else if "%choice%"=="3" (
    echo.
    echo Starting launcher menu...
    ".venv\Scripts\python.exe" launcher.py
    pause
) else if "%choice%"=="4" (
    echo.
    echo Goodbye!
    exit /b 0
) else (
    echo.
    echo Invalid choice. Please run the script again.
    pause
)