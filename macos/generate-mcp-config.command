#!/bin/bash
# Generate MCP Configuration for Claude Desktop
# This script creates the correct configuration snippet for your system

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

clear

cat << 'EOF'
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║          EMIS MCP Configuration Generator                  ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

This will generate the correct MCP server configuration
for your Claude Desktop settings.

EOF

echo ""
echo "Detecting system configuration..."
echo ""

# Find Python path
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    PYTHON_PATH=$(which python)
fi

if [ -z "$PYTHON_PATH" ]; then
    echo "❌ Error: Python not found!"
    echo ""
    echo "Please install Python 3.9 or higher:"
    echo "  https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Found Python: $PYTHON_PATH"

# Check if uvx is available
UVX_PATH=$(which uvx 2>/dev/null)
if [ -n "$UVX_PATH" ]; then
    echo "✅ Found uvx: $UVX_PATH (recommended - handles dependencies)"
    USE_UVX=true
else
    echo "ℹ️  uvx not found (will use Python - may need to install dependencies)"
    USE_UVX=false
fi

# Get server directory and path
MCP_DIR="$SCRIPT_DIR/mcp-server"
SERVER_PATH="$MCP_DIR/server.py"
echo "✅ Found server.py: $SERVER_PATH"

# Get backend URL
BACKEND_URL="http://localhost:38153"
echo "✅ Backend URL: $BACKEND_URL"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Generated Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Generate config based on what's available
if [ "$USE_UVX" = true ]; then
    echo "Using uvx with dependencies (recommended - creates isolated environment)"
    echo ""
    CONFIG=$(cat << CONFIGEOF
{
  "mcpServers": {
    "emis": {
      "command": "uvx",
      "args": [
        "--with", "mcp",
        "--with", "requests",
        "--with", "python-dotenv",
        "python",
        "$SERVER_PATH"
      ],
      "env": {
        "EMIS_BACKEND_URL": "$BACKEND_URL"
      }
    }
  }
}
CONFIGEOF
)
else
    echo "Using Python with full path: $PYTHON_PATH"
    echo "⚠️  Note: You may need to install dependencies manually"
    echo ""
    CONFIG=$(cat << CONFIGEOF
{
  "mcpServers": {
    "emis": {
      "command": "$PYTHON_PATH",
      "args": [
        "$SERVER_PATH"
      ],
      "env": {
        "EMIS_BACKEND_URL": "$BACKEND_URL"
      }
    }
  }
}
CONFIGEOF
)
fi

echo "$CONFIG"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save to file
CONFIG_FILE="$SCRIPT_DIR/claude-mcp-config.json"
echo "$CONFIG" > "$CONFIG_FILE"
echo "✅ Configuration saved to: claude-mcp-config.json"

# Copy to clipboard if available
if command -v pbcopy &> /dev/null; then
    echo "$CONFIG" | pbcopy
    echo "✅ Configuration copied to clipboard!"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next Steps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Open Claude Desktop settings:"
echo "   Claude Desktop → Settings → Developer → Edit Config"
echo ""
echo "2. Add the configuration above to your config file:"
echo "   Location: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "   • If file is empty, paste the entire configuration"
echo "   • If you have other MCP servers, add just the 'emis' section"
echo ""
echo "3. Save the file"
echo ""
echo "4. Restart Claude Desktop completely (Cmd+Q, then reopen)"
echo ""
echo "5. Test by asking: 'Search EMIS for water treatment'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Would you like to open the Claude config file now? [Y/n]: " open_config

# Default to Y if empty
if [ -z "$open_config" ]; then
    open_config="y"
fi

if [ "$open_config" = "y" ] || [ "$open_config" = "Y" ]; then
    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
    
    # Create directory if it doesn't exist
    mkdir -p "$HOME/Library/Application Support/Claude"
    
    # Create file if it doesn't exist
    if [ ! -f "$CLAUDE_CONFIG" ]; then
        echo '{"mcpServers":{}}' > "$CLAUDE_CONFIG"
        echo "✅ Created Claude config file"
    fi
    
    # Open in editor
    if command -v open &> /dev/null; then
        open -e "$CLAUDE_CONFIG" 2>/dev/null || open "$CLAUDE_CONFIG" 2>/dev/null
        echo "✅ Opened config file in editor"
        echo ""
        echo "📝 Paste the configuration and save the file."
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Remember:"
echo "  1. Backend must be running (macos/start-emis-backend.command)"
echo "  2. Restart Claude Desktop after saving config"
echo "  3. Configuration has been copied to clipboard (paste it!)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Press Enter to exit..."
