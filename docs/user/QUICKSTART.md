# EMIS Quick Start Guide

## Prerequisites

- Python 3.9+ installed
- EMIS portal credentials (email and password)
- (Optional) Claude Desktop installed (for MCP Server method)

## Quick Setup (5 minutes)

### Step 1: Setup Backend (One-time)

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Edit `.env` and add your EMIS credentials:
```
EMIS_EMAIL=your_email@example.com
EMIS_PASSWORD=your_password
PORT=38153
```

### Step 2: Start the Backend

Start the backend server:
```bash
python app.py
```

Or use Docker:
```bash
docker-compose up -d
```

The backend will be available at `http://localhost:38153`

### Step 3: Verify Backend is Running

Test the health check endpoint:
```bash
curl http://localhost:38153/
```

You should see:
```json
{"status": "ok", "service": "Generic Web Scraping API", "version": "1.0.0"}
```

---

## Choose Your Method

Now that the backend is running, choose how you want to use EMIS:

### Method 1: MCP Server (Claude Desktop) ⭐ Recommended for Claude Users

**Best for:** Natural language queries through Claude Desktop

**Setup:**
1. Make sure backend is running (Step 2 above)
2. **macOS**: Double-click `macos/generate-mcp-config.command`<br>**Windows**: Double-click `windows\generate-mcp-config.bat`
3. Copy the generated configuration
4. Open Claude Desktop → Settings → Developer → Edit Config
5. Paste the configuration into the `mcpServers` section
6. Save and restart Claude Desktop

**Usage:**
Just ask Claude:
- "Search EMIS for water treatment"
- "What does EMIS say about waste management?"
- "Find recent BBT updates in EMIS"

**See:** [MCP_CLAUDE_DESKTOP_SETUP.md](../../MCP_CLAUDE_DESKTOP_SETUP.md) for detailed instructions

---

### Method 2: Command Line Interface (CLI) ⭐ Recommended for Quick Queries

**Best for:** Fast, direct queries from terminal

**Setup:**
No extra setup needed! Just make sure the backend is running.

**Usage:**
```bash
# Navigate to backend directory
cd backend

# List available sites
./scrape list

# Query EMIS
./scrape query emis "water treatment"

# Different output formats
./scrape query emis "water" --format json
./scrape query emis "water" --format table
./scrape query emis "water" --raw

# Check credentials
./scrape check emis
```

**See:** [CLI_USAGE.md](CLI_USAGE.md) for complete CLI documentation

---

### Method 3: REST API

**Best for:** Integration with other applications

**Usage:**
```bash
# Health check
curl http://localhost:38153/

# List sites
curl http://localhost:38153/sites

# Query EMIS
curl -X POST http://localhost:38153/query/emis \
  -H "Content-Type: application/json" \
  -d '{"query": "water treatment"}'
```

---

## Troubleshooting

### Backend Won't Start

**Issue**: Port 38153 is already in use
**Solution**: Change the port in `.env`:
```
PORT=38154
```
Then update `EMIS_BACKEND_URL` in MCP configuration if using MCP Server.

### Connection Refused Error

**Issue**: MCP Server or API can't connect to backend
**Solutions**:
1. Verify backend is running: `curl http://localhost:38153/`
2. Check if backend is on a different port
3. Ensure `EMIS_BACKEND_URL` environment variable matches your backend URL

### Authentication Errors

**Issue**: 401 Unauthorized or 500 errors
**Solutions**:
1. Verify EMIS credentials in `.env` are correct
2. Check backend logs for detailed error messages
3. Test credentials with CLI: `./scrape check emis`

### Docker Issues

**Issue**: Container fails to start
**Solutions**:
1. Check Docker is running: `docker ps`
2. View logs: `docker-compose logs`
3. Rebuild container: `docker-compose up --build`

---

## Configuration

### Environment Variables

**Backend** (in `backend/.env`):
- `EMIS_EMAIL` - Your EMIS portal email (required)
- `EMIS_PASSWORD` - Your EMIS portal password (required)
- `PORT` - Backend port (default: 38153)
- `HEADLESS` - Browser visibility (default: true)
- `PLAYWRIGHT_SLOW_MO` - Delay between actions in ms (default: 0)

**MCP Server** (in Claude Desktop config):
- `EMIS_BACKEND_URL` - Backend API URL (default: http://localhost:38153)

---

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   CLI/MCP   │  HTTP   │ Backend API  │ Playwright│ EMIS Portal │
│   Client    │────────▶│ (FastAPI)    │─────────▶│ (emis.vito) │
│             │         │ Port 38153   │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
```

All interfaces share the same core scraping framework with configurable authentication and data extraction strategies.

---

## Next Steps

- **CLI Users**: See [CLI_USAGE.md](CLI_USAGE.md) for complete CLI documentation
- **MCP Users**: See [MCP_CLAUDE_DESKTOP_SETUP.md](../../MCP_CLAUDE_DESKTOP_SETUP.md) for detailed MCP setup
- **Framework Users**: See [GENERIC_FRAMEWORK.md](GENERIC_FRAMEWORK.md) for adding new sites
- **General**: See [README.md](../../README.md) for project overview

---

## Support

If you encounter issues:
1. Check backend logs: `docker-compose logs` or console output
2. Verify all environment variables are set correctly
3. Test backend directly with curl: `curl http://localhost:38153/`
4. Test with CLI: `./scrape check emis`
5. Ensure EMIS credentials are valid and account is active
