# Apple Calendar MCP Server Troubleshooting Guide

## Issue Summary

The Apple Calendar MCP server (`shadowfax92/apple-calendar-mcp`) is failing to start with the error:

```
sh: mcp-apple-calendars: command not found
```

This occurs after npm attempts to install the package from GitHub.

## Root Cause

The MCP server configuration is trying to execute `mcp-apple-calendars`, but this command is not available in your PATH. This typically happens when:

1. The package wasn't installed globally
2. The binary/executable name differs from what's configured
3. The package structure doesn't expose a CLI command as expected
4. The npm package installation didn't complete successfully

## Error Pattern in Log

The log shows a repeating pattern:
1. ✅ Server initializes successfully
2. ⚠️ npm warns: package will be installed from GitHub
3. ❌ `mcp-apple-calendars` command not found
4. ❌ Server disconnects unexpectedly

## Solutions

### Solution 1: Check Package Installation

First, verify if the package is installed and what executables it provides:

```bash
# Check if npm can find the package
npm list -g github:shadowfax92/apple-calendar-mcp

# Or try installing it globally manually
npm install -g github:shadowfax92/apple-calendar-mcp

# Check what binaries it provides
npm list -g --depth=0 | grep apple-calendar
```

### Solution 2: Find the Correct Executable Name

The executable name might be different. Check the package's `package.json` or try:

```bash
# After installing, check node_modules/.bin for available commands
npm install github:shadowfax92/apple-calendar-mcp
ls node_modules/.bin/ | grep -i calendar
```

Common variations might be:
- `mcp-apple-calendar` (singular)
- `apple-calendar-mcp`
- `@shadowfax92/apple-calendar-mcp`

### Solution 3: Use npx Instead

If the package doesn't expose a global command, try using `npx` to run it:

**Update your Claude Desktop config** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "apple-calendar-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "github:shadowfax92/apple-calendar-mcp"
      ]
    }
  }
}
```

The `-y` flag auto-accepts npm installation prompts.

### Solution 4: Use Node.js Directly

If the package has a main entry point, run it with Node.js:

```json
{
  "mcpServers": {
    "apple-calendar-mcp": {
      "command": "node",
      "args": [
        "-e",
        "require('github:shadowfax92/apple-calendar-mcp')"
      ]
    }
  }
}
```

Or if it has a specific entry file:

```json
{
  "mcpServers": {
    "apple-calendar-mcp": {
      "command": "node",
      "args": [
        "/path/to/node_modules/github:shadowfax92/apple-calendar-mcp/dist/index.js"
      ]
    }
  }
}
```

### Solution 5: Install via MCP Installer (Recommended)

Use the MCP installer tool if available:

```bash
# Check if mcp-installer is available
npx @modelcontextprotocol/installer install github:shadowfax92/apple-calendar-mcp
```

### Solution 6: Check Package Repository

Verify the package exists and check its README for installation instructions:

1. Visit: `https://github.com/shadowfax92/apple-calendar-mcp`
2. Check the README for specific installation steps
3. Look for any required dependencies or setup steps

### Solution 7: Alternative Apple Calendar MCP Servers

If the package has issues, consider alternative implementations:

1. **@foxychat-mcp/apple-calendar** (from npm search results)
   ```bash
   npm install -g @foxychat-mcp/apple-calendar
   ```

2. Check other Apple Calendar MCP servers on:
   - https://www.pulsemcp.com/servers/apple-calendars
   - https://modelcontextprotocol.io/servers

## Debugging Steps

### 1. Check Current Configuration

Find your Claude Desktop config file:
```bash
# macOS
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | grep -A 10 apple-calendar
```

### 2. Test Command Manually

Try running the command manually to see the exact error:

```bash
# Test if command exists
which mcp-apple-calendars

# Try with npx
npx -y github:shadowfax92/apple-calendar-mcp

# Check npm cache
npm cache verify
```

### 3. Check npm/node Versions

Ensure you have compatible versions:

```bash
node --version  # Should be 18+ for most MCP servers
npm --version   # Should be 9+
```

### 4. Clear npm Cache

Sometimes npm cache issues can cause problems:

```bash
npm cache clean --force
```

### 5. Check Logs for More Details

Monitor the log file in real-time:

```bash
tail -f ~/Library/Logs/Claude/mcp-server-shadowfax92/apple-calendar-mcp.log
```

## Verification

After making changes:

1. **Restart Claude Desktop completely** (quit and reopen)
2. **Check the log file** for new entries
3. **Test the MCP server** by asking Claude to access your calendar

## Expected Behavior

When working correctly, you should see:
- ✅ Server initializes successfully
- ✅ No "command not found" errors
- ✅ Server stays connected
- ✅ Calendar tools are available in Claude

## Additional Resources

- [MCP Debugging Documentation](https://modelcontextprotocol.io/docs/tools/debugging)
- [Claude Desktop MCP Setup](https://claude.ai/docs/mcp)
- [MCP Server Development Guide](https://modelcontextprotocol.io/docs)

## Next Steps

1. Try Solution 3 (npx) first - it's the most likely to work
2. If that fails, check the GitHub repository for specific instructions
3. Consider using an alternative Apple Calendar MCP server if issues persist
4. Report the issue to the package maintainer if the package appears broken

