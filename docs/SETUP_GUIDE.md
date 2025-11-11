# Quid MCP Setup Guide

**Quick setup for both technical and non-technical users**

---

## Easy Setup (Recommended)

### macOS Users

1. **Double-click**: `macos/setup-quid.command`
2. **Choose deployment method**:
   - Option 1: Virtual Environment (faster, best for development)
   - Option 2: Docker (isolated, no Python issues)
3. Follow the prompts to enter credentials
4. Done! Backend will be configured and ready

### Windows Users

1. **Double-click**: `windows\setup-quid.bat`
2. **Choose deployment method**:
   - Option 1: Virtual Environment (faster, best for development)
   - Option 2: Docker (isolated, no Python issues)
3. Follow the prompts to enter credentials
4. Done! Backend will be configured and ready

---

## Deployment Options Comparison

| Feature | Virtual Environment | Docker |
|---------|-------------------|--------|
| **Port** | 91060 | 8906 |
| **Setup Time** | 2-5 minutes | 5-10 minutes (first time) |
| **Startup Time** | ~2 seconds | ~10 seconds |
| **Prerequisites** | Python 3.9+ | Docker Desktop |
| **Isolation** | Shares system Python | Fully isolated |
| **Best For** | Development, testing | Production, compatibility issues |
| **Python Version** | Uses system Python | Uses Python 3.12 (in container) |

---

## Prerequisites

### For Virtual Environment (Option 1)

- **Python 3.9+** installed
  - macOS: `brew install python3` or download from [python.org](https://www.python.org/downloads/)
  - Windows: Download from [python.org](https://www.python.org/downloads/)

### For Docker (Option 2)

- **Docker Desktop** installed and running
  - macOS: Download from [docker.com](https://www.docker.com/products/docker-desktop/)
  - Windows: Download from [docker.com](https://www.docker.com/products/docker-desktop/)

---

## What the Setup Script Does

### Virtual Environment Path

1. ✅ Checks Python version
2. ✅ Creates Python virtual environment
3. ✅ Installs required packages
4. ✅ Installs Playwright browser (Chromium)
5. ✅ Collects your credentials
6. ✅ Creates `.env` configuration file
7. ✅ Offers to start the backend

### Docker Path

1. ✅ Checks Docker is installed and running
2. ✅ Collects your credentials
3. ✅ Creates `.env` configuration file
4. ✅ Builds Docker image
5. ✅ Starts Docker container
6. ✅ Verifies backend is responding

---

## Starting the Backend

### After Virtual Environment Setup

**macOS:**
```bash
open macos/start-quid-backend.command
```

**Windows:**
```batch
windows\start-quid-backend.bat
```

**Or manually:**
```bash
cd backend
python app.py
```

### After Docker Setup

```bash
docker-compose up
```

Or run in background:
```bash
docker-compose up -d
```

---

## Verification

### Check if Backend is Running

**Virtual Environment:**
```bash
curl http://localhost:91060/
```

**Docker:**
```bash
curl http://localhost:8906/
```

### Expected Response

```json
{
  "status": "ok",
  "service": "Quid MCP API",
  "version": "2.0.0"
}
```

---

## Managing Your Deployment

### Virtual Environment Commands

**Start:**
```bash
cd backend
python app.py
```

**Stop:**
- Press `Ctrl+C` in terminal
- Or: `pkill -f "python.*app.py"`

**Update dependencies:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Docker Commands

**Start (foreground):**
```bash
docker-compose up
```

**Start (background):**
```bash
docker-compose up -d
```

**Stop:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**Restart:**
```bash
docker-compose restart
```

**Rebuild (after code changes):**
```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## Changing Credentials

### Virtual Environment

Edit `backend/.env`:
```bash
# macOS/Linux
nano backend/.env

# Windows
notepad backend\.env
```

Then restart the backend.

### Docker

1. Edit `backend/.env`
2. Restart container:
   ```bash
   docker-compose restart
   ```

---

## Troubleshooting

### Virtual Environment Issues

**Problem: Python not found**
- Install Python 3.9+ from [python.org](https://www.python.org/downloads/)

**Problem: pip install fails**
- Try: `python3 -m pip install -r requirements.txt`
- Or: `pip3 install -r requirements.txt`

**Problem: Port 91060 already in use**
- Stop existing backend: `pkill -f "python.*app.py"`
- Or change port in `backend/.env`: `PORT=XXXXX`

### Docker Issues

**Problem: Docker not found**
- Install Docker Desktop and start it

**Problem: Docker daemon not running**
- Start Docker Desktop application

**Problem: Port 8906 already in use**
- Stop existing container: `docker-compose down`
- Or change port in `docker-compose.yml`

**Problem: Container won't start**
- Check logs: `docker-compose logs`
- Try rebuilding: `docker-compose build --no-cache`

### Common Issues (Both)

**Problem: Setup script says credentials already exist**
- The script found existing `.env` file
- To reconfigure: delete `backend/.env` and run setup again
- Or manually edit `backend/.env`

**Problem: Backend starts but doesn't respond**
- Wait 10 seconds (Docker takes longer to start)
- Check if port is correct (91060 for venv, 8906 for Docker)
- Check firewall settings

---

## Re-running Setup

If you need to change deployment method or reconfigure:

1. **Clean up existing setup:**
   - Virtual Environment: `rm -rf backend/venv backend/.env`
   - Docker: `docker-compose down -v`

2. **Run setup script again:**
   - macOS: `open macos/setup-quid.command`
   - Windows: `windows\setup-quid.bat`

3. **Choose your preferred deployment method**

---

## Next Steps

After setup completes:

1. ✅ Backend is running
2. ✅ Test with: `curl http://localhost:PORT/` (replace PORT)
3. ✅ Configure MCP in Claude Desktop (see [MCP Setup Guide](user/MCP_CLAUDE_DESKTOP_SETUP.md))
4. ✅ Start using Quid with Claude!

---

## Support

- **Documentation**: [docs/](../docs/)
- **Troubleshooting**: [docs/troubleshooting/](troubleshooting/)
- **Docker Guide**: [docs/guides/DOCKER_SETUP.md](guides/DOCKER_SETUP.md)
- **CLI Usage**: [docs/user/CLI_USAGE.md](user/CLI_USAGE.md)

---

**Status**: Production Ready  
**Last Updated**: 2025-11-08  
**Tested On**: macOS, Windows with both venv and Docker
