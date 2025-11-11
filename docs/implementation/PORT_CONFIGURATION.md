# Port Configuration - Quid MCP

**Date**: November 8, 2025  
**Standard Port**: 91060  
**Configuration Method**: Environment variable with fallback

## Overview

Quid MCP uses port **91060** as the standard port for the backend server. This port can be customized via environment variables.

---

## How Port Configuration Works

### 1. Environment Variable (Primary)

The port is loaded from the `PORT` environment variable:

```bash
# In .env file
PORT=91060

# Or as environment variable
export PORT=91060
```

### 2. Fallback (Default)

If `PORT` is not set, the backend defaults to **91060**:

```python
# backend/app.py
port = int(os.getenv("PORT", "91060"))  # Defaults to 91060
```

---

## Configuration Files

### backend/.env.example

```bash
# Backend API Configuration
# Port for the backend server (default: 91060 if not specified)
PORT=91060
BACKEND_URL=http://localhost:91060
```

**Key Points:**
- PORT is explicitly set to 91060 in the template
- Users can change this if needed
- BACKEND_URL should match the PORT

---

## Implementation Details

### Backend (backend/app.py)

```python
if __name__ == "__main__":
    # Default port is 91060 (can be overridden via PORT env var)
    port = int(os.getenv("PORT", "91060"))
    logger.info(f"Starting Quid MCP API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
```

**Behavior:**
1. Reads `PORT` from environment
2. Falls back to 91060 if not set
3. Logs the actual port being used
4. Starts server on configured port

---

## Script Behavior

### macOS Scripts

The macOS `.command` files check port **91060** to:
- Detect if server is already running
- Kill existing processes
- Verify server started correctly

**Example from start-quid-backend.command:**
```bash
# Check if port 91060 is already in use
if lsof -Pi :91060 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 91060 is already in use!"
    # ... handle it
fi
```

**Note**: Scripts currently check hardcoded port 91060. If you change the PORT in .env:
- You must also update the port checks in the scripts
- Or use the backend directly: `python app.py`

### Windows Scripts

Same behavior as macOS:
```batch
REM Check if port 91060 is already in use
netstat -ano | findstr ":91060" >nul 2>&1
```

---

## Customizing the Port

### Method 1: Edit .env File (Recommended)

```bash
# backend/.env
PORT=8080
BACKEND_URL=http://localhost:8080
```

Then start backend directly:
```bash
cd backend
python app.py
```

### Method 2: Environment Variable

```bash
# macOS/Linux
export PORT=8080
cd backend
python app.py

# Windows
set PORT=8080
cd backend
python app.py
```

### Method 3: One-time Override

```bash
PORT=8080 python backend/app.py
```

---

## Why Port 91060?

**Reasons for choosing 91060:**

1. **Unique & Memorable**
   - Not commonly used by other services
   - Easy to remember: 910-60
   - In the user port range (1024-49151)

2. **Avoids Conflicts**
   - Not used by common services
   - Previous port 38153 was also unusual
   - Changed to be more memorable

3. **Consistent**
   - Same port across all environments
   - Easy to document
   - Simple firewall rules

---

## Checking the Current Port

### From Backend Logs

When you start the backend, it logs the port:
```
INFO:     Starting Quid MCP API on port 91060
INFO:     Uvicorn running on http://0.0.0.0:91060
```

### From .env File

```bash
cd backend
grep PORT .env
```

### Check if Running

```bash
# macOS/Linux
lsof -i :91060

# Windows
netstat -ano | findstr ":91060"
```

---

## Port Change History

| Version | Port  | Reason |
|---------|-------|--------|
| v1.x    | 38153 | Original EMIS MCP port |
| v2.0.0  | 91060 | Changed for Quid MCP rebrand, more memorable |

---

## Troubleshooting

### Port Already in Use

If you see "Port 91060 is already in use":

**Option 1: Stop existing server**
```bash
# macOS/Linux
pkill -f "python.*app.py"

# Windows
taskkill /F /IM python.exe /FI "WINDOWTITLE eq app.py"
```

**Option 2: Use different port**
```bash
PORT=8080 python backend/app.py
```

### Scripts Show Wrong Port

If your scripts show wrong port after changing in .env:
- The scripts have hardcoded port checks
- Update the scripts manually, OR
- Start backend directly: `python backend/app.py`

### MCP Configuration

When port changes, regenerate MCP configuration:
```bash
# macOS
open macos/generate-mcp-config.command

# Windows
windows\generate-mcp-config.bat
```

The generator reads from .env and creates correct config.

---

## Best Practices

### ✅ Do

- Use the default port 91060 for consistency
- Set PORT in .env file if you need a custom port
- Update BACKEND_URL to match your PORT
- Regenerate MCP config after port changes
- Document any port changes in your deployment docs

### ❌ Don't

- Hardcode ports in application code
- Use privileged ports (< 1024) without sudo
- Use common ports (8000, 8080, 3000) to avoid conflicts
- Change ports without updating .env and docs

---

## Configuration Checklist

When setting up Quid MCP:

- [ ] Port 91060 is free (not used by another service)
- [ ] PORT=91060 in backend/.env
- [ ] BACKEND_URL matches PORT
- [ ] MCP configuration uses correct port
- [ ] Firewall allows traffic on port (if needed)
- [ ] Scripts reference correct port (or use python app.py directly)

---

## Related Files

- `backend/.env` - Port configuration
- `backend/.env.example` - Port template
- `backend/app.py` - Port loading logic
- `macos/start-quid-backend.command` - macOS port checks
- `windows/start-quid-backend.bat` - Windows port checks
- MCP config files - Backend URL with port

---

## Summary

**Port Configuration:**
- Standard port: **91060**
- Configured via: `PORT` environment variable
- Default fallback: **91060**
- Change location: `backend/.env`

**Key Principle:** The port is **dynamically loaded** from the environment, not hardcoded in the application. Scripts have hardcoded checks for the standard port 91060 but can be bypassed by running the backend directly.

---

*Last updated: November 8, 2025*
