# MCP Server Setup Guide for Quid Backend

This guide explains how to set up the Quid MCP server to work with Claude Desktop.

## Quick Setup

### 1. Install Dependencies

```bash
cd mcp-server
pip install -r requirements.txt
```

### 2. Ensure Backend is Running

The MCP server requires the Quid backend API to be running:

```bash
cd ../backend
python app.py
# Or use Docker: docker-compose up
```

The backend should be accessible at `http://localhost:91060` (default).

### 3. Configure Claude Desktop

Edit Claude Desktop's configuration file:

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

Add the Quid MCP server configuration:

```json
{
  "mcpServers": {
    "quid-backend": {
      "command": "YOUR_PYTHON_PATH",
      "args": [
        "YOUR_PROJECT_PATH/mcp-server/server.py"
      ],
      "env": {
        "QUID_BACKEND_URL": "http://localhost:91060"
      }
    }
  }
}
```

**Important:** 
- Replace `YOUR_PYTHON_PATH` with your Python executable (e.g., `python3`, `python`, or full path like `/usr/bin/python3`)
- Replace `YOUR_PROJECT_PATH` with the full absolute path to your project directory
- **Easiest way**: Use the generate scripts (`macos/generate-mcp-config.command` or `windows\generate-mcp-config.bat`) which auto-detect these paths!

### 4. Restart Claude Desktop

After saving the configuration, restart Claude Desktop completely.

## Using the MCP Server

Once configured, you can use the MCP server in Claude Desktop by asking:

- "Query EMIS for recent BBT updates for water treatment"
- "What does EMIS say about waste management legislation?"
- "Check backend health"

Claude will automatically use the `query_emis` tool when it detects EMIS-related queries.

## Troubleshooting

### Server Not Appearing

1. **Check Configuration JSON**: Ensure the JSON is valid (no trailing commas, proper quotes)

2. **Check Python Path**: Verify Python is in your PATH, or use full path:
   ```json
   "command": "YOUR_PYTHON_PATH"
   ```
   Find your Python path:
   - macOS/Linux: `which python3`
   - Windows: `where python`

3. **Check File Path**: Ensure the path to `server.py` is absolute and correct (replace `YOUR_PROJECT_PATH` with your actual project location)

4. **Check Permissions**: Ensure `server.py` is executable:
   ```bash
   chmod +x mcp-server/server.py
   ```

### Backend Connection Errors

1. **Verify Backend is Running**:
   ```bash
   curl http://localhost:91060/
   ```

2. **Check Backend URL**: Ensure `EMIS_BACKEND_URL` in the config matches your backend

3. **Check Backend Logs**: Look for errors in the backend console

### Python Import Errors

If you see import errors:

1. **Install Dependencies**:
   ```bash
   pip install "mcp[cli]" requests python-dotenv
   ```

2. **Check Python Version**: Requires Python 3.8+
   ```bash
   python3 --version
   ```

3. **Use Virtual Environment**: Consider using a venv:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

   Then use the venv Python in config:
   ```json
   "command": "YOUR_PROJECT_PATH/venv/bin/python"
   ```
   Replace `YOUR_PROJECT_PATH` with your actual project directory path.

## Alternative: Using MCP CLI

If you have the MCP CLI installed, you can use:

```bash
cd mcp-server
uv run mcp install server.py
```

This will automatically configure Claude Desktop for you.

## Testing the Server

### Test Backend Connection

```bash
# Test backend health
curl http://localhost:91060/

# Test a query
curl -X POST http://localhost:91060/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'
```

### Test MCP Server Directly

You can test the MCP server using the MCP inspector:

```bash
# Install MCP CLI if not already installed
pip install "mcp[cli]"

# Run server in dev mode
cd mcp-server
uv run mcp dev server.py
```

## Environment Variables

The MCP server supports these environment variables:

- `QUID_BACKEND_URL`: Backend API URL (default: `http://localhost:91060`)
- `EMIS_API_KEY`: Optional API key for backend authentication

You can set these in:
1. The Claude Desktop config `env` section (recommended)
2. A `.env` file in `mcp-server/` directory
3. System environment variables

## Next Steps

- See `README.md` for more detailed documentation
- See main project `QUICKSTART.md` for backend setup
- Check `backend/README.md` for backend API documentation

