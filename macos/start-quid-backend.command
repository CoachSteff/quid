#!/bin/bash
# Quid MCP Backend Launcher
# Double-click this file to start the Quid MCP backend server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/../backend"

# Clear screen for clean output
clear

# Print banner
cat << 'EOF'
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║                Quid MCP Backend Server                     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

EOF

echo "Starting Quid MCP Backend Server..."
echo "Port: 91060"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found!"
    echo ""
    echo "Please run setup first:"
    echo "  1. Open Terminal"
    echo "  2. Navigate to: $SCRIPT_DIR"
    echo "  3. Run: cd backend && python3 -m venv venv"
    echo "  4. Run: venv/bin/pip install -r requirements.txt"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo ""
    echo "Creating .env from template..."
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file"
        echo ""
        echo "⚠️  IMPORTANT: You need to add your credentials!"
        echo ""
        echo "Please edit the file: backend/.env"
        echo "And add your plugin credentials (e.g., EMIS_EMAIL, EMIS_PASSWORD)."
        echo ""
        read -p "Press Enter after you've added your credentials..."
    else
        echo "❌ Error: .env.example not found!"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Check if credentials are set
if ! grep -q "EMIS_EMAIL=.*@" .env 2>/dev/null || ! grep -q "EMIS_PASSWORD=..*" .env 2>/dev/null; then
    echo "⚠️  Warning: Plugin credentials not configured in .env file!"
    echo ""
    echo "Please edit: backend/.env"
    echo "And set credentials for your plugins:"
    echo "  EMIS_EMAIL=your_email@example.com"
    echo "  EMIS_PASSWORD=your_password"
    echo "  # Add credentials for other plugins as needed"
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

# Check if port 91060 is already in use
if lsof -Pi :91060 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 91060 is already in use!"
    echo ""
    echo "Options:"
    echo "  1. Kill existing process and restart (default)"
    echo "  2. Exit (existing server is still running)"
    echo ""
    read -p "Choose option [1/2] (default: 1): " choice
    
    # Default to 1 if empty
    if [ -z "$choice" ]; then
        choice="1"
        echo "Using default: Option 1 (restart)"
    fi
    
    if [ "$choice" = "1" ]; then
        echo ""
        echo "Killing existing process..."
        pkill -f "python.*app.py" 2>/dev/null
        sleep 2
        echo "✅ Process killed"
        echo ""
    else
        echo ""
        echo "Exiting. Backend is already running at http://localhost:91060"
        echo ""
        read -p "Press Enter to exit..."
        exit 0
    fi
fi

# Activate virtual environment and start server
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Starting Quid MCP Backend Server..."
echo ""
sleep 2

source venv/bin/activate
python app.py > /tmp/quid-backend.log 2>&1 &
BACKEND_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 3

# Check if server is responding
if curl -s http://localhost:91060/ > /dev/null 2>&1; then
    clear
    cat << 'EOF'
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║            ✅ Quid MCP Backend Service Running             ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

🎉 SUCCESS! The backend is now running and ready to use.

📍 Service Information:
   • URL: http://localhost:91060
   • Status: ✅ Running (PID: BACKEND_PID_PLACEHOLDER)
   • Performance: ~8 seconds per query

🔧 Ready for Use:
   The Quid MCP backend is now accessible and can be used with:
   • MCP Server in Claude Desktop (recommended)
   • Command Line Interface (CLI)
   • Direct API calls

📊 What This Service Provides:
   • Plugin-based access to protected content sources
   • Fast queries with session reuse
   • 100 structured results per query
   • Automatic session management

ℹ️  To Stop the Service:
   • Close this terminal window, OR
   • Press Ctrl+C, OR
   • Run: pkill -f "python.*app.py"

📖 Logs are saved to: /tmp/quid-backend.log

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Keep this window open while using the Quid MCP backend service.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
    # Replace placeholder with actual PID
    sed -i '' "s/BACKEND_PID_PLACEHOLDER/$BACKEND_PID/" /dev/stdout 2>/dev/null || true
    
    # Wait for user to stop
    echo "Press Ctrl+C to stop the service..."
    wait $BACKEND_PID
else
    echo ""
    echo "❌ Failed to start backend"
    echo ""
    echo "Check the logs for details:"
    echo "  tail /tmp/quid-backend.log"
    echo ""
    kill $BACKEND_PID 2>/dev/null
fi

# This will only execute if the server stops
echo ""
echo "🛑 Quid MCP Backend service stopped."
echo ""
read -p "Press Enter to exit..."
