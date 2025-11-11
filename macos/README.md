# macOS Launcher Scripts

This folder contains **macOS-specific** setup and management scripts for the EMIS backend.

## Available Scripts

### 1. setup-emis.command (Run Once)
**Initial setup script**
- Creates Python virtual environment
- Installs required packages
- Installs Playwright browser
- Sets up `.env` configuration file
- Collects EMIS credentials

### 2. start-quid-backend.command (Primary Launcher)
**Starts the backend server with visual feedback**
- ✅ Checks all prerequisites
- ✅ Validates credentials
- ✅ Handles port conflicts
- ✅ Activates virtual environment
- ✅ Starts FastAPI server on port 91060
- ✅ Shows status and keeps terminal open

**Usage:**
```bash
# Option 1: Double-click in Finder
# Option 2: From terminal
open macos/start-quid-backend.command
```

### 3. stop-quid-backend.command
**Stops the running backend server**
- Finds server process on port 91060
- Gracefully stops the service
- Confirms shutdown

### 4. generate-mcp-config.command
**Generates MCP configuration for Claude Desktop**
- Auto-detects Python installation path
- Auto-detects project directory
- Generates user-specific configuration
- Copies to clipboard for easy pasting
- Optionally opens Claude config file

## How to Use

### First Time Setup:
1. Double-click `setup-emis.command`
2. Follow the prompts
3. Enter your EMIS credentials when asked

### Daily Use:
1. Double-click `start-quid-backend.command`
2. Wait for "✅ Quid MCP Backend Service Running" message
3. Keep the Terminal window open while using
4. Close Terminal or press `Ctrl+C` to stop

### Security Warning on First Run:
If macOS shows "cannot be opened because it is from an unidentified developer":
1. Right-click (or Control-click) the `.command` file
2. Select "Open" from the menu
3. Click "Open" in the security dialog
4. This only needs to be done once per file

## File Locations

```
emis/
├── macos/                           # ← All macOS launchers HERE
│   ├── setup-emis.command          # Initial setup
│   ├── start-quid-backend.command  # ✅ Use this to start
│   ├── stop-quid-backend.command   # Stop server
│   └── generate-mcp-config.command # MCP setup
├── backend/
│   ├── app.py                      # Main backend server
│   ├── start.sh                    # Alternative Linux/Mac launcher
│   └── venv/                       # Virtual environment
└── README.md                       # Main documentation
```

## Requirements

- **macOS:** 10.13 (High Sierra) or later
- **Python:** 3.9+ installed
- **Terminal:** System Terminal app
- **Network:** Internet connection for initial setup

## Troubleshooting

### "Command not found" or "Permission denied"
The file may not be executable. Fix with:
```bash
chmod +x macos/*.command
```

### "Port 91060 already in use"
The launcher will detect this and offer to restart the server. Choose option 1.

### "Virtual environment not found"
Run `setup-emis.command` first to create the environment.

### Backend won't start
Check the logs:
```bash
tail -f /tmp/quid-backend.log
```

## Alternative Launch Methods

If you prefer command-line:
```bash
# From project root
cd backend
python app.py

# Or using the helper script
cd backend
./start.sh
```

Both methods work identically - the `.command` files just provide a nicer visual interface.

