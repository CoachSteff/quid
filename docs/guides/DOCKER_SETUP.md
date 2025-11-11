# Docker Setup Guide for Quid MCP

**For users who prefer containerized deployment or have system compatibility issues**

---

## Why Use Docker?

✅ **Consistent Environment** - Works the same on all systems  
✅ **No Python Version Issues** - Pre-configured Python 3.12  
✅ **Isolated Dependencies** - Doesn't affect your system  
✅ **Easy Cleanup** - Remove everything with one command  
✅ **System Compatibility** - Bypasses macOS network issues  

---

## Prerequisites

1. **Docker Desktop** installed
   - **macOS**: Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
   - **Windows**: Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
   - **Linux**: Install Docker Engine + Docker Compose

2. **Docker Desktop Running**
   - Start Docker Desktop application
   - Wait for it to be fully running

---

## Quick Start

### 1. Configure Credentials

Create or edit `backend/venv/.env` file (recommended) or `backend/.env`:

```bash
cd backend
# Option 1: Use venv/.env (recommended for security)
mkdir -p venv
cp .env.example venv/.env
# Edit venv/.env with your credentials

# Option 2: Use backend/.env (also works)
# cp .env.example .env
# Edit .env with your credentials
```

**Example `.env` file:**
```bash
# Port Configuration (for native setup)
# Docker overrides to 8000 internally, maps to 8906 externally
PORT=8000
HOST=0.0.0.0

# EMIS Plugin Credentials
EMIS_EMAIL=your_email@example.com
EMIS_PASSWORD=your_password

# Add other plugin credentials as needed
```

### 2. Start Backend with Docker

```bash
# From project root
docker-compose up
```

**First run**: Downloads image, installs dependencies (~5 minutes)  
**Subsequent runs**: Starts immediately (~10 seconds)

### 3. Verify Backend is Running

```bash
curl http://localhost:8906/
```

**Expected output:**
```json
{
  "status": "ok",
  "service": "Quid MCP API",
  "version": "2.0.0"
}
```

**Note**: The backend runs on port 8000 inside the container, but Docker maps it to port 8906 on your host. You access it via `localhost:8906` - the internal port is transparent to you.

### 4. Stop Backend

Press `Ctrl+C` in the terminal, or:

```bash
docker-compose down
```

---

## Usage Modes

### Foreground Mode (Recommended for Testing)

```bash
docker-compose up
```

- Logs visible in terminal
- Press `Ctrl+C` to stop
- Good for debugging

### Background Mode (Daemon)

```bash
docker-compose up -d
```

- Runs in background
- View logs: `docker-compose logs -f`
- Stop: `docker-compose down`

---

## Common Commands

### Start Backend
```bash
docker-compose up -d
```

### Stop Backend
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f quid-backend
```

### Restart Backend
```bash
docker-compose restart
```

### Rebuild Image (after code changes)
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Check Status
```bash
docker-compose ps
```

### Access Backend Shell
```bash
docker-compose exec quid-backend bash
```

---

## Configuration

### Environment Variables

Edit `backend/.env` to configure:

**Port Settings:**
```bash
PORT=8000           # Backend internal port (Docker maps to 8906)
HOST=0.0.0.0        # Bind to all interfaces (required for Docker)
```

**Plugin Credentials:**
```bash
EMIS_EMAIL=your_email@example.com
EMIS_PASSWORD=your_password

# Add other plugins:
# PLUGIN_NAME_API_KEY=your_key
```

**Advanced Options:**
```bash
HEADLESS=true               # Browser headless mode
PLAYWRIGHT_SLOW_MO=500      # Slow down browser for debugging
LOG_LEVEL=INFO              # Logging level
```

### Port Mapping

To use a different external port, edit `docker-compose.yml`:

```yaml
ports:
  - target: 8000       # Container internal port
    published: 9000    # Host external port
    protocol: tcp
```

This maps container port 8000 to host port 9000, so you'd access via `http://localhost:9000/`

---

## Volume Mounts

### Persistent Data

**Sessions** (automatically persisted):
```yaml
volumes:
  - ./backend/data/sessions:/app/data/sessions
```

Session data persists between container restarts.

### Plugin Updates

**Plugins** (read-only mount):
```yaml
volumes:
  - ./plugins:/app/plugins:ro
```

Add new plugins by:
1. Adding to `./plugins/` directory
2. Restart container: `docker-compose restart`

---

## Troubleshooting

### Backend Won't Start

**Check logs:**
```bash
docker-compose logs quid-backend
```

**Common issues:**
- Missing `.env` file → Copy from `.env.example`
- Port already in use → Change port in `docker-compose.yml`
- Docker not running → Start Docker Desktop

### Can't Access Backend

**Test from inside container:**
```bash
docker-compose exec quid-backend curl http://localhost:8000/
```

**Test from host:**
```bash
curl http://localhost:8906/
```

**If internal works but external doesn't:**
- Check firewall settings
- Verify port mapping in `docker-compose.yml`

### Credentials Not Working

**Check if .env is loaded:**
```bash
docker-compose exec quid-backend env | grep EMIS
```

Should show your credentials (masked in logs).

**If not showing:**
- Verify `backend/.env` exists
- Check `env_file:` in `docker-compose.yml`
- Rebuild: `docker-compose up --build`

### High Memory Usage

Playwright browsers use memory. To limit:

Edit `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
```

### Need to Update Code

```bash
# Rebuild image with new code
docker-compose build --no-cache
docker-compose up -d
```

---

## MCP Integration with Docker

### Configure Claude Desktop

Use the Docker-based backend URL in your MCP configuration:

```json
{
  "mcpServers": {
    "quid-backend": {
      "command": "python3",
      "args": [
        "/path/to/mcp-server/server.py"
      ],
      "env": {
        "QUID_BACKEND_URL": "http://localhost:8906"
      }
    }
  }
}
```

**Note**: The MCP server itself runs on host, connects to Docker backend.

---

## Comparison: Docker vs Native

| Feature | Docker | Native |
|---------|--------|--------|
| Setup Time | 5 min (first time) | 2 min |
| Startup Time | ~10 sec | ~2 sec |
| System Impact | Isolated | Direct |
| Memory Usage | ~500MB extra | Normal |
| Compatibility | Universal | System-dependent |
| Cleanup | Easy (one command) | Manual |
| Updates | Rebuild image | Update packages |

**Use Docker when:**
- You have system compatibility issues
- You want isolated environment
- You deploy to servers
- You want easy cleanup

**Use Native when:**
- You have a compatible system
- You want maximum performance
- You frequently modify code
- You're comfortable with Python

---

## Advanced Topics

### Custom Dockerfile

For modifications, edit `Dockerfile`:

```dockerfile
# Add system packages
RUN apt-get update && apt-get install -y \
    your-package \
    && rm -rf /var/lib/apt/lists/*

# Add Python packages
RUN pip install additional-package
```

Then rebuild:
```bash
docker-compose build --no-cache
```

### Multi-Container Setup

Add other services in `docker-compose.yml`:

```yaml
services:
  quid-backend:
    # ... existing config ...
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Production Deployment

For production, add:

```yaml
quid-backend:
  # ... existing config ...
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        memory: 512M
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

---

## Maintenance

### Update Docker Image

```bash
# Pull latest base image
docker-compose pull

# Rebuild with latest
docker-compose build --no-cache
docker-compose up -d
```

### Clean Up

**Remove stopped containers:**
```bash
docker-compose down
```

**Remove all (including volumes):**
```bash
docker-compose down -v
```

**Clean Docker cache:**
```bash
docker system prune -a
```

---

## Security Notes

**Credentials:**
- Never commit `.env` files
- Use Docker secrets for production
- Rotate credentials regularly

**Network:**
- Backend binds to `0.0.0.0` inside container (required)
- Exposed only on localhost by default
- Use reverse proxy (nginx) for external access

**Updates:**
- Keep Docker Desktop updated
- Rebuild image for security patches
- Monitor dependencies

---

## Quick Reference

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Restart
docker-compose restart

# Rebuild
docker-compose build --no-cache && docker-compose up -d

# Status
docker-compose ps

# Shell access
docker-compose exec quid-backend bash

# Clean up
docker-compose down -v
```

---

## Support

**Docker Issues:**
- Check Docker Desktop is running
- Verify Docker version: `docker --version`
- Check logs: `docker-compose logs`

**Backend Issues:**
- Same as native setup
- Check `docs/troubleshooting/README.md`

**Performance Issues:**
- Allocate more resources in Docker Desktop settings
- Consider native setup for development

---

**Status**: Production Ready  
**Tested On**: macOS, Windows, Linux  
**Docker Version**: 20.10+  
**Compose Version**: 2.0+
