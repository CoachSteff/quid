# EMIS MCP Server

A Model Context Protocol (MCP) server that provides access to the VITO EMIS portal through the EMIS backend API.

## Overview

This MCP server allows Claude (and other MCP-compatible AI assistants) to query the EMIS portal without using Claude Skills. Instead, it uses the standardized MCP protocol for better integration and control.

## Advantages over Claude Skills

- **Standardized Protocol**: Uses MCP, an open standard supported by multiple AI assistants
- **Better Integration**: Direct integration with Claude Desktop MCP configuration
- **More Flexible**: Can be used by any MCP-compatible client, not just Claude
- **Easier Debugging**: Standard stdio transport for easy testing and debugging
- **Version Control**: Easier to manage and version alongside your backend code

## Prerequisites

1. **EMIS Backend Running**: The backend API must be running (see main project README)
   - Default URL: `http://localhost:38153`
   - Can be configured via `EMIS_BACKEND_URL` environment variable

2. **Python 3.8+**: Required for running the MCP server

3. **Dependencies**: Install with `pip install -r requirements.txt`

## Installation

### 1. Install Dependencies

```bash
cd mcp-server
pip install -r requirements.txt
```

Or using uv (recommended):

```bash
uv add "mcp[cli]" requests python-dotenv
```

### 2. Configure Environment (Optional)

Create a `.env` file in the `mcp-server` directory or use environment variables:

```bash
# Backend API URL (default: http://localhost:38153)
EMIS_BACKEND_URL=http://localhost:38153

# Optional: API key if backend requires authentication
EMIS_API_KEY=your_api_key_here
```

The server will also look for `.env` files in parent directories (e.g., `backend/.env`).

## Setup with Claude Desktop

### Method 1: Using MCP CLI (Recommended)

1. Install the MCP server in Claude Desktop:

```bash
cd mcp-server
uv run mcp install server.py
```

Or with pip:

```bash
python -m mcp install server.py
```

This will automatically configure Claude Desktop to use the MCP server.

### Method 2: Manual Configuration

1. Edit Claude Desktop's MCP configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the EMIS MCP server configuration:

```json
{
  "mcpServers": {
    "emis-backend": {
      "command": "python",
      "args": [
        "/absolute/path/to/mcp-server/server.py"
      ],
      "env": {
        "EMIS_BACKEND_URL": "http://localhost:38153",
        "EMIS_API_KEY": "optional_api_key"
      }
    }
  }
}
```

3. Restart Claude Desktop

## Usage

Once configured, you can use the MCP server in Claude Desktop by asking questions like:

- "Query EMIS for recent BBT updates for water treatment"
- "What does EMIS say about waste management legislation in Flanders?"
- "Search EMIS for information about environmental permits"
- "Check EMIS backend health"

The MCP server provides two tools:

1. **query_emis**: Execute queries against the EMIS portal
2. **check_backend_health**: Check if the backend service is running

## Testing the Server

### Test with MCP Inspector

```bash
# Start the server in test mode
python server.py

# Or use the MCP CLI
uv run mcp dev server.py
```

### Test Backend Connection

```bash
# Check if backend is running
curl http://localhost:38153/

# Test a query
curl -X POST http://localhost:38153/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'
```

## Troubleshooting

### Backend Connection Errors

If you see "Could not connect to EMIS backend":

1. **Verify backend is running**:
   ```bash
   curl http://localhost:38153/
   ```

2. **Check backend URL**: Ensure `EMIS_BACKEND_URL` matches your backend configuration

3. **Check backend logs**: Look at backend console output for errors

### MCP Server Not Appearing in Claude

1. **Check configuration file**: Verify the JSON is valid in `claude_desktop_config.json`

2. **Check Python path**: Ensure the Python executable path is correct in the config

3. **Check permissions**: Ensure the server.py file is executable

4. **Restart Claude Desktop**: Always restart after configuration changes

5. **Check logs**: Look for errors in Claude Desktop's console/logs

### API Key Authentication

If your backend requires an API key:

1. Set `EMIS_API_KEY` in your environment or `.env` file
2. Ensure the backend is configured to accept this API key
3. The MCP server will automatically include the API key in requests

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐         ┌─────────────┐
│ Claude      │  MCP    │ MCP Server   │  HTTP   │ Backend API   │ Playwright│ EMIS Portal │
│ Desktop     │────────▶│ (server.py) │────────▶│ (FastAPI)     │─────────▶│ (emis.vito) │
│             │         │              │         │ Port 38153    │         │             │
└─────────────┘         └──────────────┘         └──────────────┘         └─────────────┘
```

The MCP server acts as a bridge between Claude Desktop (using MCP protocol) and your backend API (using HTTP).

## Development

### Running in Development Mode

```bash
# Use MCP development server
uv run mcp dev server.py

# Or run directly with stdio (for testing)
python server.py
```

### Adding New Tools

To add new tools to the MCP server, use the `@mcp.tool()` decorator:

```python
@mcp.tool()
def my_new_tool(param: str) -> dict:
    """Tool description"""
    # Your implementation
    return {"result": "data"}
```

### Adding Resources

To add resources (read-only data), use the `@mcp.resource()` decorator:

```python
@mcp.resource("emis://resource/{id}")
def get_resource(id: str) -> str:
    """Get resource data"""
    return json.dumps({"id": id, "data": "..."})
```

## Comparison: MCP Server vs Claude Skill

| Feature | MCP Server | Claude Skill |
|---------|-----------|--------------|
| Protocol | Standard MCP | Claude-specific |
| Setup | MCP config file | Skills directory |
| Portability | Works with any MCP client | Claude-only |
| Debugging | Standard stdio | Skill-specific |
| Version Control | Standard Python | ZIP package |
| Updates | Restart Claude Desktop | Reinstall skill |

## Next Steps

- See main project `README.md` for backend setup
- See `QUICKSTART.md` for quick setup guide
- See `docs/archived/emis-skill-specification.md` for historical Claude Skill architecture (deprecated)

