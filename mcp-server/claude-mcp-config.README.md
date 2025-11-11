# MCP Configuration Template

This directory contains a template file for Claude Desktop MCP configuration.

## Quick Start (Recommended)

**Don't edit this file manually!** Instead, use the generate scripts:

- **macOS**: Double-click `macos/generate-mcp-config.command`
- **Windows**: Double-click `windows\generate-mcp-config.bat`

These scripts will:
- Auto-detect your Python path
- Auto-detect your project location
- Generate a ready-to-use configuration
- Copy it to your clipboard

## Manual Setup (Advanced)

If you prefer to configure manually, use `claude-mcp-config.json.example` as a template:

1. Copy the example file:
   ```bash
   cp claude-mcp-config.json.example claude-mcp-config.json
   ```

2. Replace the placeholders:
   - `YOUR_PROJECT_PATH` → Full path to your project directory
   - `python3` → Your Python executable (or full path if not in PATH)

3. Copy the configuration to Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

## Finding Your Paths

### Project Path
- **macOS/Linux**: Run `pwd` in your project directory
- **Windows**: Run `cd` in your project directory, then copy the path

### Python Path
- **macOS/Linux**: Run `which python3` or `which python`
- **Windows**: Run `where python`

## Important Notes

- The generated `claude-mcp-config.json` file is user-specific and should NOT be committed to git
- Always use absolute paths in Claude Desktop configuration (it doesn't support relative paths)
- The template file (`claude-mcp-config.json.example`) is safe to commit and share

