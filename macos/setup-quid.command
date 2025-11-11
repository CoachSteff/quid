#!/bin/bash
# Quid MCP Setup Script
# Double-click this file to set up the Quid MCP backend

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/backend"

clear

cat << 'EOF'
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              Quid MCP Backend Setup                        ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

EOF

echo "This will set up the Quid MCP backend on your computer."
echo ""
echo "Choose your deployment method:"
echo ""
echo "  1. Virtual Environment (Python venv) - Recommended (default)"
echo "     • Direct Python installation"
echo "     • Faster startup (~2 seconds)"
echo "     • Best for development"
echo "     • Port: 91060"
echo ""
echo "  2. Docker (containerized)"
echo "     • Isolated environment"
echo "     • No Python version issues"
echo "     • Requires Docker Desktop"
echo "     • Port: 8906"
echo ""
read -p "Choose deployment method [1/2] (default: 1): " DEPLOYMENT_METHOD

# Default to 1 if empty
if [ -z "$DEPLOYMENT_METHOD" ]; then
    DEPLOYMENT_METHOD="1"
    echo "Using default: Option 1 (Virtual Environment)"
fi

echo ""

# Validate choice
if [ "$DEPLOYMENT_METHOD" != "1" ] && [ "$DEPLOYMENT_METHOD" != "2" ]; then
    echo "❌ Invalid option. Please run setup again and choose 1 or 2."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Docker deployment path
if [ "$DEPLOYMENT_METHOD" = "2" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Docker Deployment Selected"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Check Docker prerequisites
    echo "Checking Docker prerequisites..."
    echo ""
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found!"
        echo ""
        echo "Please install Docker Desktop:"
        echo "  https://www.docker.com/products/docker-desktop/"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo "❌ docker-compose not found!"
        echo ""
        echo "Please install Docker Desktop (includes docker-compose):"
        echo "  https://www.docker.com/products/docker-desktop/"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker Desktop is not running!"
        echo ""
        echo "Please start Docker Desktop and try again."
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
    
    echo "✅ Docker is installed and running"
    echo ""
    
    # Navigate to project root for docker-compose
    # SCRIPT_DIR is macos/, so go up one level to project root
    cd "$SCRIPT_DIR/.."
    
    # Check/create .env file in backend directory
    if [ ! -f "backend/.env" ]; then
        echo "Creating .env configuration file..."
        echo ""
        
        if [ -f "backend/.env.example" ]; then
            # Prompt for credentials
            echo "Please provide your plugin credentials (EMIS example):"
            echo ""
            echo "Note: Your credentials will be stored in backend/.env"
            echo ""
            
            read -p "EMIS Portal URL [https://navigator.emis.vito.be]: " EMIS_URL
            if [ -z "$EMIS_URL" ]; then
                EMIS_URL="https://navigator.emis.vito.be"
            fi
            
            read -p "Email address: " EMIS_EMAIL
            while [ -z "$EMIS_EMAIL" ]; do
                echo "⚠️  Email cannot be empty"
                read -p "Email address: " EMIS_EMAIL
            done
            
            echo -n "Password: "
            read -s EMIS_PASSWORD
            echo ""
            while [ -z "$EMIS_PASSWORD" ]; do
                echo "⚠️  Password cannot be empty"
                echo -n "Password: "
                read -s EMIS_PASSWORD
                echo ""
            done
            
            echo -n "Confirm password: "
            read -s EMIS_PASSWORD_CONFIRM
            echo ""
            
            if [ "$EMIS_PASSWORD" != "$EMIS_PASSWORD_CONFIRM" ]; then
                echo "❌ Passwords do not match!"
                echo ""
                read -p "Press Enter to exit..."
                exit 1
            fi
            
            # Create .env file
            cat > backend/.env << ENVEOF
# EMIS Portal Configuration
EMIS_URL=$EMIS_URL

# EMIS Portal Credentials
EMIS_EMAIL=$EMIS_EMAIL
EMIS_PASSWORD=$EMIS_PASSWORD

# API Configuration (Docker uses port 8000 internally, mapped to 8906)
PORT=8000
HOST=0.0.0.0

# Browser Configuration
HEADLESS=true

# Session Configuration
SESSION_TTL=3600
ENVEOF
            
            echo ""
            echo "✅ Credentials saved to backend/.env"
            echo ""
        else
            echo "❌ backend/.env.example not found!"
            echo ""
            read -p "Press Enter to exit..."
            exit 1
        fi
    else
        echo "✅ Using existing backend/.env configuration"
        echo ""
        echo "📝 Current settings:"
        if grep -q "^EMIS_URL=" backend/.env 2>/dev/null; then
            EXISTING_URL=$(grep "^EMIS_URL=" backend/.env | cut -d'=' -f2)
            echo "   EMIS URL: $EXISTING_URL"
        fi
        if grep -q "^EMIS_EMAIL=" backend/.env 2>/dev/null; then
            EXISTING_EMAIL=$(grep "^EMIS_EMAIL=" backend/.env | cut -d'=' -f2)
            echo "   Email: $EXISTING_EMAIL"
        fi
        if grep -q "^PORT=" backend/.env 2>/dev/null; then
            EXISTING_PORT=$(grep "^PORT=" backend/.env | cut -d'=' -f2)
            echo "   Port: $EXISTING_PORT"
        fi
        echo "   Password: ••••••••"
        echo ""
        echo "To change credentials, edit backend/.env or delete it and run setup again."
        echo ""
    fi
    
    # Build and start Docker container
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Building Docker Container"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "This may take a few minutes on first run..."
    echo ""
    
    docker-compose up --build -d
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Docker container started successfully"
        echo ""
        
        # Wait for container to be ready
        echo "⏳ Waiting for backend to be ready..."
        sleep 5
        
        # Check if backend is responding
        if curl -s http://localhost:8906/ > /dev/null 2>&1; then
            echo "✅ Backend is responding"
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "✅ Setup Complete!"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "🎉 Quid MCP Backend is running in Docker!"
            echo ""
            echo "📍 Service Information:"
            echo "   • URL: http://localhost:8906"
            echo "   • Status: ✅ Running"
            echo "   • Deployment: Docker"
            echo ""
            echo "🔧 Docker Commands:"
            echo "   • View logs: docker-compose logs -f"
            echo "   • Stop: docker-compose down"
            echo "   • Restart: docker-compose restart"
            echo ""
            echo "Next step: Configure MCP in Claude Desktop"
            echo ""
            read -p "Press Enter to exit..."
        else
            echo "⚠️  Backend container started but not responding yet"
            echo ""
            echo "Check logs with: docker-compose logs -f"
            echo ""
            read -p "Press Enter to exit..."
        fi
    else
        echo ""
        echo "❌ Failed to start Docker container"
        echo ""
        echo "Check logs with: docker-compose logs"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
    
    exit 0
fi

# Virtual Environment deployment path (existing code continues)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Virtual Environment Deployment Selected"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Steps:"
echo "  1. Create Python virtual environment"
echo "  2. Install required packages"
echo "  3. Install Playwright browser"
echo "  4. Create .env configuration file"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Return to backend directory for venv setup
cd "$SCRIPT_DIR/backend"

# Step 1: Check Python version
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Checking Python version"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo ""
    echo "Please install Python 3.9 or higher:"
    echo "  https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "Found: $PYTHON_VERSION"
echo "✅ Python check passed"

# Step 2: Create virtual environment
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Creating virtual environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
    read -p "Recreate it? [y/N] (default: N): " recreate
    
    # Default to N if empty
    if [ -z "$recreate" ]; then
        recreate="n"
    fi
    
    if [ "$recreate" = "y" ] || [ "$recreate" = "Y" ]; then
        echo "Removing old virtual environment..."
        rm -rf venv
    else
        echo "Keeping existing virtual environment"
    fi
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created"
    else
        echo "❌ Failed to create virtual environment"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
else
    echo "✅ Using existing virtual environment"
fi

# Step 3: Install packages
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Installing Python packages"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "This may take a few minutes..."
echo ""

venv/bin/pip install --upgrade pip > /tmp/quid-setup.log 2>&1
venv/bin/pip install -r requirements.txt >> /tmp/quid-setup.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Packages installed successfully"
else
    echo "❌ Failed to install packages"
    echo ""
    echo "Check the log: /tmp/quid-setup.log"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Step 4: Install Playwright browser
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Installing Playwright browser"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Installing Chromium browser..."
venv/bin/playwright install chromium >> /tmp/quid-setup.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Browser installed successfully"
else
    echo "❌ Failed to install browser"
    echo ""
    echo "Check the log: /tmp/quid-setup.log"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Step 5: Create .env file and collect credentials
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Setting up configuration and credentials"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

RECONFIGURE=false

if [ -f ".env" ]; then
    echo "⚠️  Configuration file (.env) already exists"
    read -p "Reconfigure credentials? [y/N] (default: N): " overwrite
    
    # Default to N if empty
    if [ -z "$overwrite" ]; then
        overwrite="n"
    fi
    
    if [ "$overwrite" = "y" ] || [ "$overwrite" = "Y" ]; then
        RECONFIGURE=true
    else
        echo "Keeping existing .env file"
        echo "✅ Configuration preserved"
    fi
else
    RECONFIGURE=true
fi

if [ "$RECONFIGURE" = true ]; then
    echo ""
    echo "How would you like to configure your credentials?"
    echo ""
    echo "  1. Enter credentials in terminal (recommended - default)"
    echo "  2. Edit .env file manually"
    echo ""
    read -p "Choose option [1/2] (default: 1): " config_choice
    
    # Default to option 1 if empty
    if [ -z "$config_choice" ]; then
        config_choice="1"
        echo "Using default: Option 1 (terminal entry)"
    fi
    
    if [ "$config_choice" = "1" ]; then
        # Option 1: Terminal input
        echo ""
        echo "Please provide your plugin credentials (EMIS plugin example):"
        echo ""
        echo "Note: Your credentials will be stored securely in backend/.env"
        echo "      (This file is never shared or committed to version control)"
        echo ""
        
        # Get EMIS Portal URL
        read -p "EMIS Portal URL [https://navigator.emis.vito.be]: " EMIS_URL
        if [ -z "$EMIS_URL" ]; then
            EMIS_URL="https://navigator.emis.vito.be"
        fi
        
        # Get Email
        read -p "Email address: " EMIS_EMAIL
        while [ -z "$EMIS_EMAIL" ]; do
            echo "⚠️  Email cannot be empty"
            read -p "Email address: " EMIS_EMAIL
        done
        
        # Get Password (hidden input)
        echo -n "Password: "
        read -s EMIS_PASSWORD
        echo ""
        while [ -z "$EMIS_PASSWORD" ]; do
            echo "⚠️  Password cannot be empty"
            echo -n "Password: "
            read -s EMIS_PASSWORD
            echo ""
        done
        
        # Confirm password
        echo -n "Confirm password: "
        read -s EMIS_PASSWORD_CONFIRM
        echo ""
        
        if [ "$EMIS_PASSWORD" != "$EMIS_PASSWORD_CONFIRM" ]; then
            echo "❌ Passwords do not match!"
            echo ""
            read -p "Press Enter to exit..."
            exit 1
        fi
        
        # Create .env file
        cat > .env << ENVEOF
# EMIS Portal Configuration
EMIS_URL=$EMIS_URL

# EMIS Portal Credentials
EMIS_EMAIL=$EMIS_EMAIL
EMIS_PASSWORD=$EMIS_PASSWORD

# API Configuration
PORT=91060

# Browser Configuration
HEADLESS=true

# Session Configuration
SESSION_TTL=3600
ENVEOF
        
        echo ""
        echo "✅ Credentials saved to backend/.env"
        echo ""
        echo "📝 Your configuration:"
        echo "   URL:   $EMIS_URL"
        echo "   Email: $EMIS_EMAIL"
        echo "   Password: ••••••••"
        
    elif [ "$config_choice" = "2" ]; then
        # Option 2: Manual .env editing
        echo ""
        echo "Creating .env template file..."
        
        # Create .env template
        cat > .env << 'ENVEOF'
# EMIS Portal Configuration
EMIS_URL=https://navigator.emis.vito.be

# EMIS Portal Credentials
# IMPORTANT: Replace these with your actual credentials
EMIS_EMAIL=your_email@example.com
EMIS_PASSWORD=your_password_here

# API Configuration
PORT=91060

# Browser Configuration
HEADLESS=true

# Session Configuration
SESSION_TTL=3600
ENVEOF
        
        echo "✅ Created .env template"
        echo ""
        echo "Opening .env file for editing..."
        echo ""
        
        # Try to open with default text editor
        if command -v open &> /dev/null; then
            open -e .env 2>/dev/null || open .env 2>/dev/null || true
        fi
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "⚠️  IMPORTANT: Edit the .env file now"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "File location:"
        echo "  $SCRIPT_DIR/backend/.env"
        echo ""
        echo "Required changes:"
        echo "  • EMIS_EMAIL: Replace with your EMIS email"
        echo "  • EMIS_PASSWORD: Replace with your EMIS password"
        echo "  • EMIS_URL: Optional (default is fine for most users)"
        echo ""
        echo "Example:"
        echo "  EMIS_EMAIL=john.doe@company.com"
        echo "  EMIS_PASSWORD=MySecurePassword123"
        echo ""
        read -p "Press Enter after you've saved your credentials..."
        
        # Verify credentials were set
        if grep -q "your_email@example.com" .env 2>/dev/null || grep -q "your_password_here" .env 2>/dev/null; then
            echo ""
            echo "⚠️  Warning: It looks like you haven't updated the credentials yet."
            echo ""
            read -p "Continue anyway? [y/N] (default: N): " continue_anyway
            
            # Default to N if empty
            if [ -z "$continue_anyway" ]; then
                continue_anyway="n"
            fi
            
            if [ "$continue_anyway" != "y" ] && [ "$continue_anyway" != "Y" ]; then
                echo ""
                echo "Setup cancelled. Please edit backend/.env and run setup again."
                echo ""
                read -p "Press Enter to exit..."
                exit 1
            fi
        else
            echo ""
            echo "✅ Credentials appear to be configured"
        fi
    else
        echo ""
        echo "❌ Invalid option. Please run setup again."
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Final summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Quid MCP Backend is ready to use!"
echo ""
echo "Next step: Start the backend service"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To start the backend:"
echo "  → Double-click: macos/start-quid-backend.command"
echo ""
echo "Or press Enter now to start it automatically..."
echo ""
read -p "Start backend now? [Y/n] (default: Y): " start_now

# Default to Y if empty
if [ -z "$start_now" ]; then
    start_now="y"
fi

if [ "$start_now" = "y" ] || [ "$start_now" = "Y" ]; then
    echo ""
    echo "Starting Quid MCP Backend..."
    echo ""
    cd "$SCRIPT_DIR"
    exec macos/start-quid-backend.command
else
    echo ""
    echo "To start later:"
    echo "  1. Double-click: macos/start-quid-backend.command"
    echo "  2. Backend will run on: http://localhost:91060"
    echo "  3. Ready for use in Claude Desktop!"
    echo ""
    read -p "Press Enter to exit..."
fi
