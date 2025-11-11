@echo off
REM Quid MCP Backend Stopper for Windows
REM Double-click this file to stop the Quid MCP backend server

cls

echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║              Quid MCP Backend Server Stopper               ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Stopping Quid MCP Backend Server...
echo.

REM Check if server is running on port 38153
netstat -ano | findstr ":91060" >nul 2>&1
if errorlevel 1 (
    echo ℹ️  Backend server is not running (port 91060 is free)
    echo.
    pause
    exit /b 0
)

REM Get PID and kill process
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":38153"') do (
    set PID=%%a
    echo Found server process (PID: !PID!)
    echo.
    echo Stopping server...
    taskkill /F /PID !PID! >nul 2>&1
)

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Final check
netstat -ano | findstr ":91060" >nul 2>&1
if errorlevel 1 (
    echo ✅ Server stopped successfully
) else (
    echo ⚠️  Server still running. Trying force stop...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":38153"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 1 /nobreak >nul
    
    netstat -ano | findstr ":91060" >nul 2>&1
    if errorlevel 1 (
        echo ✅ Server stopped successfully
    ) else (
        echo ❌ Failed to stop server. Please try manually:
        echo    Open Command Prompt and run: taskkill /F /IM python.exe /FI "WINDOWTITLE eq app.py"
    )
)

echo.
pause

