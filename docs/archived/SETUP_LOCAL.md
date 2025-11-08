# Local Virtual Environment Setup Guide

This guide explains how to set up and run the EMIS backend in a local virtual environment (without Docker).

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Step-by-Step Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Or if you prefer a different name:
python3 -m venv .venv
```

### 3. Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt, indicating the virtual environment is active.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI and Uvicorn (web framework)
- Playwright (browser automation)
- Other required packages

### 5. Install Playwright Browsers

```bash
playwright install chromium
```

This downloads the Chromium browser needed for scraping.

### 6. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Copy example if it exists
cp .env.example .env

# Or create manually
touch .env
```

Edit `.env` and add your configuration:

```env
# EMIS Portal Credentials (REQUIRED)
EMIS_EMAIL=your_email@example.com
EMIS_PASSWORD=your_password

# EMIS Portal URLs (optional, defaults shown)
EMIS_BASE_URL=https://emis.vito.be
EMIS_LOGIN_URL=https://navigator.emis.vito.be

# Server Port (optional, defaults to 38153)
PORT=38153

# CORS Origins (optional, defaults to localhost)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# API Key (optional, for authentication)
API_KEY=your_optional_api_key

# Session File Path (optional, defaults to data/session.json)
SESSION_FILE=data/session.json

# Playwright Configuration (optional)
# Set to false to show browser window (default: true - headless/hidden)
HEADLESS=true
# Slow motion delay in milliseconds (default: 500)
PLAYWRIGHT_SLOW_MO=500
```

### 7. Create Data Directory

The session file will be stored in `data/` directory:

```bash
mkdir -p data
```

### 8. Start the Server

**Option A: Use Python directly (Recommended)**
```bash
python app.py
```

**Option B: Use the helper script**
```bash
./start.sh
```

The helper script (`start.sh`) will:
- Automatically activate the virtual environment if it exists
- Load environment variables from `.env`
- Start the server on the correct port (38153)

### 9. Verify Server is Running

In another terminal, test the health endpoint:

```bash
curl http://localhost:38153/
```

You should see:
```json
{"status":"ok","service":"EMIS Scraping API"}
```

## Troubleshooting

### Virtual Environment Not Activating

Make sure you're in the `backend` directory and the venv exists:

```bash
ls -la venv/  # Should show venv directory
source venv/bin/activate  # Try activating manually
```

### Dependencies Not Found

If you get import errors, make sure:
1. Virtual environment is activated (`(venv)` in prompt)
2. Dependencies are installed: `pip install -r requirements.txt`

### Port Already in Use

If port 38153 is already in use:

```bash
# Find what's using the port
lsof -i :38153

# Kill the process or change PORT in .env
```

### Playwright Browser Not Found

Make sure you ran:
```bash
playwright install chromium
```

### Environment Variables Not Loading

- Check that `.env` file exists in `backend/` directory
- Verify `python-dotenv` is installed: `pip list | grep python-dotenv`
- Check `.env` file format (no spaces around `=`)

## Daily Usage

Once set up, daily usage is simple:

```bash
cd backend
source venv/bin/activate  # If not already activated
python app.py
```

Or use the helper script (which handles venv activation automatically):

```bash
cd backend
./start.sh
```

## Deactivating Virtual Environment

When you're done working:

```bash
deactivate
```

## Updating Dependencies

If `requirements.txt` changes:

```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

## Virtual Environment Best Practices

1. **Never commit `venv/`** - Add it to `.gitignore`
2. **Always activate venv** before running the server
3. **Keep requirements.txt updated** when adding new packages
4. **Use the same Python version** across team members

## Differences from Docker Setup

| Aspect | Local Venv | Docker |
|--------|-----------|--------|
| Python version | System Python | Docker image Python |
| Dependencies | Installed in venv | Installed in container |
| Browser | System Playwright | Container Playwright |
| Port | Local 38153 | Mapped 38153:38153 |
| Data directory | `backend/data/` | Container `/app/data/` |

Both setups work identically - use whichever you prefer!

