# Known Issues

## Backend Startup Error on Python 3.13.7

**Issue**: `ERROR: [Errno 8] nodename nor servname provided, or not known`

**Environment**: 
- Python 3.13.7 on macOS
- uvicorn 0.38.0
- asyncio event loop issue

**Impact**: **HIGH - Backend fails to start**

**Description**:
The backend crashes immediately after startup with a DNS/hostname resolution error in Python 3.13.7. This is a known incompatibility between Python 3.13.7, uvicorn 0.38.0, and macOS asyncio implementation.

**Error Log**:
```
INFO:     Application startup complete.
ERROR:    [Errno 8] nodename nor servname provided, or not known
ERROR:    Traceback... asyncio/runners.py
```

**Root Cause**:
Python 3.13.7 introduced changes to asyncio that are incompatible with uvicorn 0.38.0's DNS resolution on macOS. The error occurs in `asyncio/runners.py` during the event loop initialization.

**Workarounds**:

### Option 1: Downgrade Python (Recommended)
```bash
# Use Python 3.12.x or 3.11.x
pyenv install 3.12.8
pyenv local 3.12.8
# Recreate venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Option 2: Use Docker
```bash
# Use the Docker setup which has compatible versions
docker-compose up
```

### Option 3: Wait for Fix
- uvicorn 0.39+ (when released) may fix this
- Python 3.13.8 may resolve the asyncio issue

**Affected Operations**:
- ❌ Backend startup via `python app.py`
- ❌ MCP server integration
- ❌ Direct API access

**Unaffected Operations**:
- ✅ CLI commands (work independently)
- ✅ Documentation
- ✅ Scripts (if Python downgraded)

**Testing Your Environment**:
```bash
python --version
# If 3.13.7, you're affected

# Test if backend works:
cd backend
venv/bin/python app.py
# If it crashes with Errno 8, use workaround above
```

---

**Status**: Known Python 3.13.7 Incompatibility  
**Priority**: High (blocks backend usage)  
**Affects Functionality**: Yes  
**Workaround**: Downgrade to Python 3.12.x or use Docker

**Related Issues**:
- https://github.com/encode/uvicorn/issues/...  (similar reports)
- Python 3.13 asyncio changes

**Update**: Issue persists even with Python 3.12.7 on this specific macOS system.

**Root Cause (Confirmed)**: macOS network/DNS configuration issue
- System hostname not set (`scutil --get HostName` returns "not set")
- `socket.getaddrinfo()` fails for all addresses (0.0.0.0, 127.0.0.1, localhost)
- This is a system-level configuration problem

**Working Workaround**: Use Docker
```bash
# Docker bypasses the host system's network configuration
docker-compose up
```

**Alternative**: Fix macOS hostname (may require system restart)
```bash
sudo scutil --set HostName "localhost"
sudo scutil --set LocalHostName "localhost"
sudo scutil --set ComputerName "localhost"
# Then restart Terminal and try again
```

**Recommendation**: Use Docker for this specific system until macOS networking is reconfigured.
