@echo off
REM EMIS Setup Script for Windows
REM Double-click this file to set up the EMIS backend

setlocal enabledelayedexpansion

REM Get the directory where this script is located (go up one level to project root)
set "SCRIPT_DIR=%~dp0..\"
cd /d "%SCRIPT_DIR%backend"

cls

echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║                 EMIS Backend Setup                         ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo This will set up the EMIS backend on your computer.
echo.
echo Steps:
echo   1. Create Python virtual environment
echo   2. Install required packages
echo   3. Install Playwright browser
echo   4. Create .env configuration file
echo.
pause

REM Step 1: Check Python version
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Step 1: Checking Python version
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo.
    echo Please install Python 3.9 or higher:
    echo   https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Found: %PYTHON_VERSION%
echo ✅ Python check passed

REM Step 2: Create virtual environment
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Step 2: Creating virtual environment
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

if exist "venv" (
    echo ⚠️  Virtual environment already exists
    set /p recreate="Recreate it? [y/N] (default: N): "
    
    if /i "!recreate!"=="y" (
        echo Removing old virtual environment...
        rmdir /s /q venv
    ) else (
        echo Keeping existing virtual environment
    )
)

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        echo.
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Using existing virtual environment
)

REM Step 3: Install packages
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Step 3: Installing Python packages
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo This may take a few minutes...
echo.

call venv\Scripts\activate.bat
python -m pip install --upgrade pip > %TEMP%\emis-setup.log 2>&1
python -m pip install -r requirements.txt >> %TEMP%\emis-setup.log 2>&1

if errorlevel 1 (
    echo ❌ Failed to install packages
    echo.
    echo Check the log: %TEMP%\emis-setup.log
    echo.
    pause
    exit /b 1
)
echo ✅ Packages installed successfully

REM Step 4: Install Playwright browser
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Step 4: Installing Playwright browser
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo Installing Chromium browser...
python -m playwright install chromium >> %TEMP%\emis-setup.log 2>&1

if errorlevel 1 (
    echo ❌ Failed to install browser
    echo.
    echo Check the log: %TEMP%\emis-setup.log
    echo.
    pause
    exit /b 1
)
echo ✅ Browser installed successfully

REM Step 5: Create .env file and collect credentials
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Step 5: Setting up configuration and credentials
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set RECONFIGURE=false

if exist ".env" (
    echo ⚠️  Configuration file (.env) already exists
    set /p overwrite="Reconfigure credentials? [y/N] (default: N): "
    
    if /i "!overwrite!"=="y" (
        set RECONFIGURE=true
    ) else (
        echo Keeping existing .env file
        echo ✅ Configuration preserved
    )
) else (
    set RECONFIGURE=true
)

if "!RECONFIGURE!"=="true" (
    echo.
    echo How would you like to configure your credentials?
    echo.
    echo   1. Enter credentials in terminal (recommended - default)
    echo   2. Edit .env file manually
    echo.
    set /p config_choice="Choose option [1/2] (default: 1): "
    
    if "!config_choice!"=="" set config_choice=1
    
    if "!config_choice!"=="1" (
        REM Option 1: Terminal input
        echo.
        echo Please provide your EMIS Portal credentials:
        echo.
        echo Note: Your credentials will be stored securely in backend\.env
        echo       (This file is never shared or committed to version control)
        echo.
        
        set /p EMIS_URL="EMIS Portal URL [https://navigator.emis.vito.be]: "
        if "!EMIS_URL!"=="" set EMIS_URL=https://navigator.emis.vito.be
        
        set /p EMIS_EMAIL="Email address: "
        if "!EMIS_EMAIL!"=="" (
            echo ⚠️  Email cannot be empty
            set /p EMIS_EMAIL="Email address: "
        )
        
        set /p EMIS_PASSWORD="Password: "
        if "!EMIS_PASSWORD!"=="" (
            echo ⚠️  Password cannot be empty
            set /p EMIS_PASSWORD="Password: "
        )
        
        set /p EMIS_PASSWORD_CONFIRM="Confirm password: "
        
        if not "!EMIS_PASSWORD!"=="!EMIS_PASSWORD_CONFIRM!" (
            echo ❌ Passwords do not match!
            echo.
            pause
            exit /b 1
        )
        
        REM Create .env file
        (
            echo # EMIS Portal Configuration
            echo EMIS_URL=!EMIS_URL!
            echo.
            echo # EMIS Portal Credentials
            echo EMIS_EMAIL=!EMIS_EMAIL!
            echo EMIS_PASSWORD=!EMIS_PASSWORD!
            echo.
            echo # API Configuration
            echo PORT=38153
            echo.
            echo # Browser Configuration
            echo HEADLESS=true
            echo.
            echo # Session Configuration
            echo SESSION_TTL=3600
        ) > .env
        
        echo.
        echo ✅ Credentials saved to backend\.env
        echo.
        echo 📝 Your configuration:
        echo    URL:   !EMIS_URL!
        echo    Email: !EMIS_EMAIL!
        echo    Password: ••••••••
        
    ) else if "!config_choice!"=="2" (
        REM Option 2: Manual .env editing
        echo.
        echo Creating .env template file...
        
        (
            echo # EMIS Portal Configuration
            echo EMIS_URL=https://navigator.emis.vito.be
            echo.
            echo # EMIS Portal Credentials
            echo # IMPORTANT: Replace these with your actual credentials
            echo EMIS_EMAIL=your_email@example.com
            echo EMIS_PASSWORD=your_password_here
            echo.
            echo # API Configuration
            echo PORT=38153
            echo.
            echo # Browser Configuration
            echo HEADLESS=true
            echo.
            echo # Session Configuration
            echo SESSION_TTL=3600
        ) > .env
        
        echo ✅ Created .env template
        echo.
        echo Opening .env file for editing...
        echo.
        
        start notepad .env
        
        echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        echo ⚠️  IMPORTANT: Edit the .env file now
        echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        echo.
        echo File location:
        echo   %SCRIPT_DIR%backend\.env
        echo.
        echo Required changes:
        echo   • EMIS_EMAIL: Replace with your EMIS email
        echo   • EMIS_PASSWORD: Replace with your EMIS password
        echo   • EMIS_URL: Optional (default is fine for most users)
        echo.
        echo Example:
        echo   EMIS_EMAIL=john.doe@company.com
        echo   EMIS_PASSWORD=MySecurePassword123
        echo.
        pause
    ) else (
        echo.
        echo ❌ Invalid option. Please run setup again.
        echo.
        pause
        exit /b 1
    )
)

REM Final summary
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ✅ Setup Complete!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🎉 EMIS Backend is ready to use!
echo.
echo Next step: Start the backend service
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo To start the backend:
echo   → Double-click: windows\start-emis-backend.bat
echo.
set /p start_now="Start backend now? [Y/n] (default: Y): "

if /i "!start_now!"=="" set start_now=y
if /i "!start_now!"=="n" (
    echo.
    echo To start later:
    echo   1. Double-click: windows\start-emis-backend.bat
    echo   2. Backend will run on: http://localhost:38153
    echo   3. Ready for use in Claude Desktop!
    echo.
    pause
    exit /b 0
)

echo.
echo Starting EMIS Backend...
echo.
cd /d "%SCRIPT_DIR%"
call "%SCRIPT_DIR%windows\start-emis-backend.bat"

