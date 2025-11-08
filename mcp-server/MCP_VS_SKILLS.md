# MCP Server vs Claude Skills: Comparison and Migration Guide

## Overview

You asked about building a Model Context Protocol (MCP) service instead of using Claude Skills. **Yes, we can build an MCP server**, and it offers several advantages over Claude Skills.

## What is MCP?

Model Context Protocol (MCP) is an **open standard** protocol that allows AI assistants to connect to external tools and data sources. It's similar to how Skills work, but:

- **Standardized**: Works with any MCP-compatible client (Claude, OpenAI Codex, etc.)
- **Open Source**: Not tied to a specific vendor
- **More Flexible**: Better debugging, version control, and integration options

## About Context7

**Important Note**: Context7 is a specific MCP server that fetches documentation and code examples. It's **not** what we need for EMIS backend access. Instead, we've built a **custom MCP server** that wraps your EMIS backend API.

You can use both:
- **Our custom EMIS MCP server**: For querying EMIS portal
- **Context7**: For fetching documentation (optional, separate)

## Comparison: MCP Server vs Claude Skills

| Feature | MCP Server ✅ | Claude Skills |
|---------|--------------|---------------|
| **Protocol** | Standard MCP (open) | Claude-specific (proprietary) |
| **Portability** | Works with any MCP client | Claude-only |
| **Setup** | Configuration file | Skills directory + ZIP |
| **Updates** | Edit code, restart Claude | Reinstall skill ZIP |
| **Debugging** | Standard stdio logging | Limited visibility |
| **Version Control** | Standard Python/Git | ZIP files |
| **Testing** | MCP inspector tools | Manual testing in Claude |
| **Documentation** | Standard MCP docs | Claude-specific docs |
| **Integration** | Any MCP-compatible tool | Claude Desktop only |

## Architecture Comparison

### Claude Skill Architecture
```
Claude Desktop → Skill Script → Backend API → EMIS Portal
     (proprietary protocol)
```

### MCP Server Architecture
```
Claude Desktop → MCP Server → Backend API → EMIS Portal
     (standard MCP protocol)
```

## Advantages of MCP Server

### 1. **Standard Protocol**
- Uses open MCP standard
- Can be used by other MCP-compatible tools
- Future-proof if you switch AI assistants

### 2. **Better Development Experience**
- Standard Python development workflow
- Easy to test with MCP inspector
- Better error messages and logging
- Version control friendly (no ZIP files)

### 3. **Easier Maintenance**
- Update code, restart Claude Desktop
- No need to recreate ZIP files
- Standard debugging tools work

### 4. **More Flexible**
- Can add more tools easily
- Can expose resources (read-only data)
- Can add prompts (pre-defined queries)
- Better integration with development tools

## Migration from Claude Skills (Deprecated)

**Note:** Claude Skills have been deprecated in favor of MCP Server. If you're currently using Claude Skills, here's how to migrate:

### Step 1: Install MCP Server

```bash
cd mcp-server
pip install -r requirements.txt
```

### Step 2: Configure Claude Desktop

Edit `claude_desktop_config.json`:

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

### Step 3: Remove Old Skill

1. Remove the skill from Claude Desktop settings
2. Delete the skill folder from `~/Library/Application Support/Claude/Skills/`

### Step 4: Restart Claude Desktop

The MCP server will be available immediately.

## Using Both MCP Server and Context7

You can use both servers simultaneously:

```json
{
  "mcpServers": {
    "emis-backend": {
      "command": "python3",
      "args": ["/path/to/emis/mcp-server/server.py"],
      "env": {
        "EMIS_BACKEND_URL": "http://localhost:38153"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

## Feature Comparison

### Tools Available

**Claude Skill:**
- One script that calls backend API
- Limited to what's in the script

**MCP Server:**
- `query_emis`: Query EMIS portal (same as skill)
- `check_backend_health`: Check backend status (new!)
- Easy to add more tools

### Resources

**Claude Skill:**
- Not supported

**MCP Server:**
- `emis://backend/config`: Backend configuration info
- Can add more resources as needed

## Testing

### MCP Server Testing

```bash
# Use MCP inspector
uv run mcp dev server.py

# Test backend connection
curl http://localhost:38153/
```

### Claude Skill Testing

- Manual testing in Claude Desktop only
- Limited debugging options

## Recommendations

### Use MCP Server If:
- ✅ You want a standardized, portable solution
- ✅ You want better development experience
- ✅ You might use other MCP-compatible tools
- ✅ You want easier debugging and testing
- ✅ You prefer standard version control workflows

### Use Claude Skills If:
- ⚠️ You only need Claude Desktop integration
- ⚠️ You prefer the simpler ZIP-based workflow
- ⚠️ You don't need to switch AI assistants

## Conclusion

**For EMIS backend access, we recommend using the MCP server** because:

1. It's more flexible and maintainable
2. Uses an open standard protocol
3. Better development and debugging experience
4. Easier to extend with new features
5. Future-proof if you switch AI assistants

The MCP server provides the same functionality as the Claude Skill but with better tooling and a standardized approach.

## Next Steps

1. **Try the MCP Server**: Follow `MCP_SETUP.md` to configure it
2. **Test Both**: Keep the skill temporarily and compare
3. **Migrate**: Once comfortable, remove the skill and use only MCP
4. **Extend**: Add more tools/resources as needed

## Questions?

- See `README.md` for detailed MCP server documentation
- See `MCP_SETUP.md` for setup instructions
- Check main project `QUICKSTART.md` for backend setup

