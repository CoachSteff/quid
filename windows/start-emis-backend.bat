@echo off
REM EMIS Backend Launcher for Windows
REM Double-click this file to start the EMIS backend server

setlocal enabledelayedexpansion

REM Get the directory where this script is located (go up one level to project root)
set "SCRIPT_DIR=%~dp0..\"
cd /d "%SCRIPT_DIR%backend"

cls

echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║              EMIS Backend Server Launcher                  ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Starting EMIS Backend Server...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Error: Virtual environment not found!
    echo.
    echo Please run setup first:
    echo   1. Double-click: windows\setup-emis.bat
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found!
    echo.
    echo Creating .env from template...
    
    if exist ".env.example" (
        copy .env.example .env >nul
        echo ✅ Created .env file
        echo.
        echo ⚠️  IMPORTANT: You need to add your credentials!
        echo.
        echo Please edit the file: backend\.env
        echo And add your EMIS email and password.
        echo.
        pause
    ) else (
        echo ❌ Error: .env.example not found!
        echo.
        pause
        exit /b 1
    )
)

REM Check if port 38153 is already in use
netstat -ano | findstr ":38153" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  Port 38153 is already in use!
    echo.
    echo Options:
    echo   1. Kill existing process and restart (default)
    echo   2. Exit (existing server is still running)
    echo.
    set /p choice="Choose option [1/2] (default: 1): "
    
    if "!choice!"=="" set choice=1
    
    if "!choice!"=="1" (
        echo.
        echo Killing existing process...
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":38153"') do (
            taskkill /F /PID %%a >nul 2>&1
        )
        timeout /t 2 /nobreak >nul
        echo ✅ Process killed
        echo.
    ) else (
        echo.
        echo Exiting. Backend is already running at http://localhost:38153
        echo.
        pause
        exit /b 0
    )
)

REM Activate virtual environment and start server
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🚀 Starting EMIS Backend Server...
echo.
timeout /t 2 /nobreak >nul

call venv\Scripts\activate.bat
start /b python app.py > %TEMP%\emis-backend.log 2>&1

REM Wait for server to start
echo ⏳ Waiting for server to start...
timeout /t 3 /nobreak >nul

REM Check if server is responding
curl -s http://localhost:38153/ >nul 2>&1
if not errorlevel 1 (
    cls
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║                                                            ║
    echo ║            ✅ EMIS Backend Service Running                 ║
    echo ║                                                            ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo 🎉 SUCCESS! The backend is now running and ready to use.
    echo.
    echo 📍 Service Information:
    echo    • URL: http://localhost:38153
    echo    • Status: ✅ Running
    echo    • Performance: ~8 seconds per query
    echo.
    echo 🔧 Ready for Use:
    echo    The EMIS backend is now accessible and can be used with:
    echo    • MCP Server in Claude Desktop (recommended)
    echo    • Command Line Interface (CLI)
    echo    • Direct API calls
    echo.
    echo 📊 What This Service Provides:
    echo    • Authenticated access to EMIS Portal
    echo    • Fast queries with session reuse
    echo    • 100 structured results per query
    echo    • Automatic session management
    echo.
    echo ℹ️  To Stop the Service:
    echo    • Close this window, OR
    echo    • Press Ctrl+C, OR
    echo    • Double-click: windows\stop-emis-backend.bat
    echo.
    echo 📖 Logs are saved to: %TEMP%\emis-backend.log
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo Keep this window open while using the EMIS backend service.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo.
    echo Press Ctrl+C to stop the service...
    
    REM Keep window open and monitor
    :loop
    timeout /t 5 /nobreak >nul
    curl -s http://localhost:38153/ >nul 2>&1
    if errorlevel 1 (
        echo.
        echo 🛑 EMIS Backend service stopped.
        echo.
        pause
        exit /b 0
    )
    goto loop
) else (
    echo.
    echo ❌ Failed to start backend
    echo.
    echo Check the logs for details:
    echo   type %TEMP%\emis-backend.log
    echo.
    pause
)

