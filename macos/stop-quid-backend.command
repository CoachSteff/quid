#!/bin/bash
# Quid MCP Backend Stopper
# Double-click this file to stop the Quid MCP backend server

clear

cat << 'EOF'
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              Quid MCP Backend Server Stopper               ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

EOF

echo "Stopping Quid MCP Backend Server..."
echo ""

# Check if server is running
if ! lsof -Pi :91060 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "ℹ️  Backend server is not running (port 91060 is free)"
    echo ""
    read -p "Press Enter to exit..."
    exit 0
fi

# Get PID
PID=$(lsof -Pi :91060 -sTCP:LISTEN -t)

echo "Found server process (PID: $PID)"
echo ""

# Kill the process
echo "Stopping server..."
kill $PID 2>/dev/null

# Wait a moment
sleep 2

# Check if it stopped
if lsof -Pi :91060 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Server still running. Forcing stop..."
    kill -9 $PID 2>/dev/null
    sleep 1
fi

# Final check
if ! lsof -Pi :91060 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Server stopped successfully"
else
    echo "❌ Failed to stop server. Please try manually:"
    echo "   Open Terminal and run: pkill -f 'python.*app.py'"
fi

echo ""
read -p "Press Enter to exit..."
