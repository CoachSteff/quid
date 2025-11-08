# Setting Up EMIS MCP Server in Claude Desktop

## 🚀 Quick Start (Easiest Method - 5 Minutes)

### Just Follow These Steps:

**1. Start the Backend**
- **macOS**: Double-click `macos/start-emis-backend.command`
- **Windows**: Double-click `windows\start-emis-backend.bat`

Wait until you see "✅ EMIS Backend Service Running"

**2. Generate MCP Configuration**
- **macOS**: Double-click `macos/generate-mcp-config.command`
- **Windows**: Double-click `windows\generate-mcp-config.bat`
- This auto-detects your Python path
- Generates the correct configuration
- **Copies to clipboard automatically** 📋

**3. Add to Claude Desktop**
- Open Claude Desktop
- Go to: **Settings → Developer → Edit Config**
- **Paste** the configuration (Cmd+V)
- **Save** the file

**4. Restart Claude Desktop**
- Quit completely: **Cmd+Q**
- Reopen Claude Desktop

**5. Test It Works**
Ask Claude: **"Search EMIS for water treatment"**

You should see Claude using the `query_emis` tool! 🎉

---

## Alternative: Manual Configuration

If you prefer to configure manually instead of using the generator:

---

## What You Need

1. ✅ Backend running (http://localhost:38153)
2. ✅ MCP server files (already in `mcp-server/`)
3. ✅ Python 3 installed (check with `which python3`)
4. ⬜ Claude Desktop configuration (we'll do this now)

---

## Step 1: Start the Backend

First, make sure the EMIS backend is running:

- **macOS**: Double-click `macos/start-emis-backend.command`
- **Windows**: Double-click `windows\start-emis-backend.bat`

Wait until you see:
```
✅ EMIS Backend Service Running
```

---

## Step 2: Configure Claude Desktop

### Easy Way: Use the Generator Script ⭐

- **macOS**: Double-click `macos/generate-mcp-config.command`
- **Windows**: Double-click `windows\generate-mcp-config.bat`

This script will:
- Auto-detect your Python path (`/opt/homebrew/bin/python3` or similar)
- Generate the correct configuration with full paths
- Copy it to your clipboard
- Optionally open the Claude config file

Then just paste and save!

---

### Manual Way: Edit Config File Yourself

If you prefer to configure manually:

#### Find Your Claude Config File

The config file is located at:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### Add the EMIS MCP Server

Open the config file and add this configuration:

**Option A: Using uvx with Dependencies (Recommended) ⭐**
```json
{
  "mcpServers": {
    "emis": {
      "command": "uvx",
      "args": [
        "--with", "mcp",
        "--with", "requests",
        "--with", "python-dotenv",
        "python",
        "/Users/steffvanhaverbeke/Library/Mobile Documents/com~apple~CloudDocs/Cursor/1_projects/emis/mcp-server/server.py"
      ],
      "env": {
        "EMIS_BACKEND_URL": "http://localhost:38153"
      }
    }
  }
}
```

**Option B: Using Python with Full Path (Requires installed dependencies)**
```json
{
  "mcpServers": {
    "emis": {
      "command": "/opt/homebrew/bin/python3",
      "args": [
        "/Users/steffvanhaverbeke/Library/Mobile Documents/com~apple~CloudDocs/Cursor/1_projects/emis/mcp-server/server.py"
      ],
      "env": {
        "EMIS_BACKEND_URL": "http://localhost:38153"
      }
    }
  }
}
```

**Important:** 
- Use **full path** to Python: `/opt/homebrew/bin/python3` (run `which python3` to find yours)
- Use **full path** to `server.py` (replace with your actual project location)
- Do NOT use just `"python"` - Claude Desktop can't find it without full path

### If You Already Have Other MCP Servers

If your config file already has other MCP servers, add the EMIS config to the existing `mcpServers` object:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "emis": {
      "command": "/opt/homebrew/bin/python3",
      "args": [
        "/Users/steffvanhaverbeke/Library/Mobile Documents/com~apple~CloudDocs/Cursor/1_projects/emis/mcp-server/server.py"
      ],
      "env": {
        "EMIS_BACKEND_URL": "http://localhost:38153"
      }
    }
  }
}
```

---

## Step 3: Restart Claude Desktop

1. **Quit Claude Desktop completely** (Cmd+Q)
2. **Wait 5 seconds**
3. **Reopen Claude Desktop**

---

## Step 4: Test It Works

Ask Claude:

```
Can you search EMIS for information about water treatment?
```

Claude should now have access to the `query_emis` tool and be able to query the EMIS portal.

---

## Troubleshooting

### "I don't see any EMIS tools"

**Check:**
1. Backend is running: `curl http://localhost:38153/`
2. Config file saved correctly
3. Claude Desktop restarted completely
4. Path to `server.py` is correct (absolute path)

### "Connection refused" or "Backend unavailable"

**Solution:**
1. Start backend: 
   - **macOS**: Double-click `macos/start-emis-backend.command`
   - **Windows**: Double-click `windows\start-emis-backend.bat`
2. Verify: Open http://localhost:38153 in browser
3. Should see: `{"status":"ok",...}`

### "ModuleNotFoundError: No module named 'mcp'"

**Solution:**
Install MCP dependencies:
```bash
cd mcp-server
pip install -r requirements.txt
```

---

## What Tools Will Be Available

Once configured, Claude will have these tools:

### 1. `query_emis(query: str)`
Query the VITO EMIS portal for environmental and energy data.

**Example:**
```
query_emis("BBT water treatment")
```

**Returns:**
- Status (success/error)
- Citation (source, URL, timestamp)
- Summary (AI-generated)
- Raw data (100 structured results)

### 2. `check_backend_health()`
Check if the EMIS backend service is running and accessible.

**Example:**
```
check_backend_health()
```

**Returns:**
- Status (healthy/unavailable/error)
- Backend URL
- Message

---

## Expected Performance

- **First query:** ~28 seconds (authentication)
- **Subsequent queries:** ~8 seconds (session reuse)
- **Data per query:** Up to 100 structured results
- **Session duration:** 1 hour

---

## Configuration Options

### Change Backend URL

If your backend is on a different port or host:

```json
{
  "mcpServers": {
    "emis": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "EMIS_BACKEND_URL": "http://localhost:8080"
      }
    }
  }
}
```

### Add API Key (if needed)

If your backend requires an API key:

```json
{
  "mcpServers": {
    "emis": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "EMIS_BACKEND_URL": "http://localhost:38153",
        "EMIS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

---

## Quick Reference

### Start Backend
- **macOS**: Double-click `macos/start-emis-backend.command`
- **Windows**: Double-click `windows\start-emis-backend.bat`

### Stop Backend
- **macOS**: Double-click `macos/stop-emis-backend.command`
- **Windows**: Double-click `windows\stop-emis-backend.bat`

### Config File Location
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### MCP Server Location
```
/path/to/emis/mcp-server/server.py
```

### Test Backend
```bash
curl http://localhost:38153/
```

---

## Summary

1. ✅ Start backend (double-click launcher)
2. ✅ Add MCP config to Claude Desktop
3. ✅ Restart Claude Desktop
4. ✅ Test with "search EMIS for..."

**Result:** Claude will now have access to the `query_emis` tool and can query the EMIS portal directly!

---

## Need Help?

If it's still not working:

1. **Check backend logs:**
   ```bash
   tail -f /tmp/emis-backend.log
   ```

2. **Check MCP server logs:**
   - Look in Claude Desktop's console/logs
   - Check for connection errors

3. **Verify Python path:**
   ```bash
   which python
   # Should show Python 3.x
   ```

4. **Test MCP server manually:**
   ```bash
   cd mcp-server
   python server.py
   # Should start without errors
   ```
