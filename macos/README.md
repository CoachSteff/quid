# macOS Scripts

This folder contains macOS-specific setup and management scripts for the EMIS backend.

## Scripts

- **setup-emis.command** - Initial setup script (run once)
  - Creates Python virtual environment
  - Installs required packages
  - Sets up configuration file
  - Collects EMIS credentials

- **start-emis-backend.command** - Starts the backend server
  - Checks prerequisites
  - Activates virtual environment
  - Starts the FastAPI server on port 38153

- **stop-emis-backend.command** - Stops the backend server
  - Finds running server process
  - Gracefully stops the service

- **generate-mcp-config.command** - Generates MCP configuration for Claude Desktop
  - Auto-detects Python path
  - Generates correct configuration
  - Copies to clipboard
  - Optionally opens Claude config file

## Usage

Simply double-click any `.command` file to run it. If macOS shows a security warning:
1. Right-click the file
2. Select "Open"
3. Click "Open" in the dialog

## Requirements

- macOS 10.13 or later
- Python 3.9+ installed
- Terminal access (for running scripts)

