@echo off
REM Generate MCP Configuration for Claude Desktop (Windows)
REM This script creates the correct configuration snippet for your system

setlocal enabledelayedexpansion

REM Get the directory where this script is located (go up one level to project root)
set "SCRIPT_DIR=%~dp0..\"

cls

echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║          EMIS MCP Configuration Generator                  ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo This will generate the correct MCP server configuration
echo for your Claude Desktop settings.
echo.
echo.
echo Detecting system configuration...
echo.

REM Find Python path
where python >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found!
    echo.
    echo Please install Python 3.9 or higher:
    echo   https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%i in ('where python') do set PYTHON_PATH=%%i
echo ✅ Found Python: %PYTHON_PATH%

REM Check if uvx is available
where uvx >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%i in ('where uvx') do set UVX_PATH=%%i
    echo ✅ Found uvx: !UVX_PATH! (recommended - handles dependencies)
    set USE_UVX=true
) else (
    echo ℹ️  uvx not found (will use Python - may need to install dependencies)
    set USE_UVX=false
)

REM Get server directory and path (SCRIPT_DIR is already project root)
set "MCP_DIR=%SCRIPT_DIR%mcp-server"
set "SERVER_PATH=%MCP_DIR%\server.py"

REM Convert to Windows path format
set "SERVER_PATH=!SERVER_PATH:/=\!"

echo ✅ Found server.py: !SERVER_PATH!

REM Get backend URL
set BACKEND_URL=http://localhost:38153
echo ✅ Backend URL: !BACKEND_URL!

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Generated Configuration
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Generate config based on what's available
if "!USE_UVX!"=="true" (
    echo Using uvx with dependencies (recommended - creates isolated environment)
    echo.
    (
        echo {
        echo   "mcpServers": {
        echo     "emis": {
        echo       "command": "uvx",
        echo       "args": [
        echo         "--with", "mcp",
        echo         "--with", "requests",
        echo         "--with", "python-dotenv",
        echo         "python",
        echo         "!SERVER_PATH!"
        echo       ],
        echo       "env": {
        echo         "EMIS_BACKEND_URL": "!BACKEND_URL!"
        echo       }
        echo     }
        echo   }
        echo }
    ) > "%SCRIPT_DIR%claude-mcp-config.json"
) else (
    echo Using Python with full path: %PYTHON_PATH%
    echo ⚠️  Note: You may need to install dependencies manually
    echo.
    (
        echo {
        echo   "mcpServers": {
        echo     "emis": {
        echo       "command": "%PYTHON_PATH:\=/%",
        echo       "args": [
        echo         "!SERVER_PATH!"
        echo       ],
        echo       "env": {
        echo         "EMIS_BACKEND_URL": "!BACKEND_URL!"
        echo       }
        echo     }
        echo   }
        echo }
    ) > "%SCRIPT_DIR%claude-mcp-config.json"
)

type "%SCRIPT_DIR%claude-mcp-config.json"

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ✅ Configuration saved to: claude-mcp-config.json
echo.

REM Copy to clipboard using PowerShell
powershell -Command "Get-Content '%SCRIPT_DIR%claude-mcp-config.json' | Set-Clipboard" >nul 2>&1
if not errorlevel 1 (
    echo ✅ Configuration copied to clipboard!
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Next Steps
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 1. Open Claude Desktop settings:
echo    Claude Desktop → Settings → Developer → Edit Config
echo.
echo 2. Add the configuration above to your config file:
echo    Location: %APPDATA%\Claude\claude_desktop_config.json
echo.
echo    • If file is empty, paste the entire configuration
echo    • If you have other MCP servers, add just the 'emis' section
echo.
echo 3. Save the file
echo.
echo 4. Restart Claude Desktop completely (close and reopen)
echo.
echo 5. Test by asking: 'Search EMIS for water treatment'
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set /p open_config="Would you like to open the Claude config file now? [Y/n]: "

if /i "!open_config!"=="" set open_config=y
if /i "!open_config!"=="y" (
    set "CLAUDE_CONFIG=%APPDATA%\Claude\claude_desktop_config.json"
    
    REM Create directory if it doesn't exist
    if not exist "%APPDATA%\Claude" mkdir "%APPDATA%\Claude"
    
    REM Create file if it doesn't exist
    if not exist "!CLAUDE_CONFIG!" (
        echo {"mcpServers":{}} > "!CLAUDE_CONFIG!"
        echo ✅ Created Claude config file
    )
    
    REM Open in notepad
    start notepad "!CLAUDE_CONFIG!"
    echo ✅ Opened config file in editor
    echo.
    echo 📝 Paste the configuration and save the file.
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Remember:
echo   1. Backend must be running (windows\start-emis-backend.bat)
echo   2. Restart Claude Desktop after saving config
echo   3. Configuration has been copied to clipboard (paste it!)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause

