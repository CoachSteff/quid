# Windows Scripts

This folder contains Windows-specific setup and management scripts for the EMIS backend.

## Scripts

- **setup-emis.bat** - Initial setup script (run once)
  - Creates Python virtual environment
  - Installs required packages
  - Sets up configuration file
  - Collects EMIS credentials

- **start-emis-backend.bat** - Starts the backend server
  - Checks prerequisites
  - Activates virtual environment
  - Starts the FastAPI server on port 38153

- **stop-emis-backend.bat** - Stops the backend server
  - Finds running server process
  - Gracefully stops the service

- **generate-mcp-config.bat** - Generates MCP configuration for Claude Desktop
  - Auto-detects Python path
  - Generates correct configuration
  - Copies to clipboard using PowerShell
  - Optionally opens Claude config file in Notepad

## Usage

Simply double-click any `.bat` file to run it. Windows may show a security warning - click "Run" or "More info" → "Run anyway".

## Requirements

- Windows 10 or later
- Python 3.9+ installed
- Command Prompt access (for running scripts)

## Notes

- Scripts use Windows batch syntax
- Paths use backslashes (`\`) as Windows requires
- PowerShell is used for clipboard operations
- Notepad is used for opening configuration files

