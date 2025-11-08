# EMIS Skill - Two Modes of Operation

This Claude Skill supports two modes of operation:

## Mode 1: Backend API (Default, Recommended)

The skill calls a separate backend API service that handles all scraping logic.

**Pros:**
- Centralized credential management
- Better resource management
- Can serve multiple users
- Easier to update scraping logic without updating skill

**Requirements:**
- Backend service must be running (see main project README)
- Backend handles all Playwright dependencies

## Mode 2: Direct Scraping (Fallback)

The skill runs Playwright directly when backend is unavailable.

**Pros:**
- No separate service needed
- Self-contained
- Works immediately if dependencies are installed

**Cons:**
- Requires Playwright installation in Claude Desktop environment
- Heavier dependencies
- Each query launches a browser instance

**Requirements:**
- Install Playwright: `pip install playwright playwright-stealth`
- Install browser: `playwright install chromium`
- Set `EMIS_EMAIL` and `EMIS_PASSWORD` environment variables

## Configuration

### Environment Variables

**For Backend Mode:**
- `EMIS_BACKEND_URL` - Backend API URL (default: http://localhost:38153)
- `EMIS_API_KEY` - Optional API key if backend requires authentication

**For Direct Mode:**
- `EMIS_EMAIL` - Your EMIS portal email
- `EMIS_PASSWORD` - Your EMIS portal password
- `EMIS_USE_DIRECT_FALLBACK` - Enable/disable fallback (default: "true")

### How It Works

1. Skill tries to call backend API first
2. If backend is unavailable AND `EMIS_USE_DIRECT_FALLBACK=true`:
   - Automatically falls back to direct scraping mode
   - Uses Playwright directly in the skill process
3. If both fail, returns error with setup instructions

## Setup

### Backend Mode Setup

See the main project README for backend setup instructions.

### Direct Mode Setup

1. Install dependencies in Claude Desktop's Python environment:
```bash
pip install playwright playwright-stealth
playwright install chromium
```

2. Set environment variables:
```bash
export EMIS_EMAIL="your_email@example.com"
export EMIS_PASSWORD="your_password"
```

3. The skill will automatically use direct mode if backend is unavailable.

## Testing

Test direct mode standalone:
```bash
cd scripts
python run_query_direct.py "test query"
```

Test with fallback:
```bash
# Without backend running, the skill will automatically fall back
python run_query.py "test query"
```

## Troubleshooting

**Direct mode not working:**
- Verify Playwright is installed: `python -c "import playwright; print('OK')"`
- Verify browser is installed: `playwright install chromium`
- Check credentials are set: `echo $EMIS_EMAIL`

**Want to disable fallback:**
- Set `EMIS_USE_DIRECT_FALLBACK=false` to force backend-only mode

