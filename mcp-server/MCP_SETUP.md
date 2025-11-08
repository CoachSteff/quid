# MCP Server Setup Guide for EMIS Backend

This guide explains how to set up the EMIS MCP server to work with Claude Desktop.

## Quick Setup

### 1. Install Dependencies

```bash
cd mcp-server
pip install -r requirements.txt
```

### 2. Ensure Backend is Running

The MCP server requires the EMIS backend API to be running:

```bash
cd ../backend
python app.py
# Or use Docker: docker-compose up
```

The backend should be accessible at `http://localhost:38153` (default).

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

Add the EMIS MCP server configuration:

```json
{
  "mcpServers": {
    "emis-backend": {
      "command": "python3",
      "args": [
        "/absolute/path/to/emis/mcp-server/server.py"
      ],
      "env": {
        "EMIS_BACKEND_URL": "http://localhost:38153"
      }
    }
  }
}
```

**Important:** Replace `/absolute/path/to/emis/mcp-server/server.py` with the actual absolute path to your `server.py` file.

### 4. Restart Claude Desktop

After saving the configuration, restart Claude Desktop completely.

## Using the MCP Server

Once configured, you can use the MCP server in Claude Desktop by asking:

- "Query EMIS for recent BBT updates for water treatment"
- "What does EMIS say about waste management legislation?"
- "Check EMIS backend health"

Claude will automatically use the `query_emis` tool when it detects EMIS-related queries.

## Troubleshooting

### Server Not Appearing

1. **Check Configuration JSON**: Ensure the JSON is valid (no trailing commas, proper quotes)

2. **Check Python Path**: Verify `python3` is in your PATH, or use full path:
   ```json
   "command": "/usr/bin/python3"
   ```

3. **Check File Path**: Ensure the path to `server.py` is absolute and correct

4. **Check Permissions**: Ensure `server.py` is executable:
   ```bash
   chmod +x mcp-server/server.py
   ```

### Backend Connection Errors

1. **Verify Backend is Running**:
   ```bash
   curl http://localhost:38153/
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
   "command": "/absolute/path/to/venv/bin/python"
   ```

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
curl http://localhost:38153/

# Test a query
curl -X POST http://localhost:38153/query \
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

- `EMIS_BACKEND_URL`: Backend API URL (default: `http://localhost:38153`)
- `EMIS_API_KEY`: Optional API key for backend authentication

You can set these in:
1. The Claude Desktop config `env` section (recommended)
2. A `.env` file in `mcp-server/` directory
3. System environment variables

## Next Steps

- See `README.md` for more detailed documentation
- See main project `QUICKSTART.md` for backend setup
- Check `backend/README.md` for backend API documentation

