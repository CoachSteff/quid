# Using the EMIS Skill in Claude Desktop

## Quick Start

Once the EMIS Skill is installed in Claude Desktop, you can use it by simply asking Claude questions about EMIS data. The skill will automatically detect when you're asking about EMIS, BBT, VITO, or Flemish environmental legislation.

## How to Use

### 1. Ask Natural Language Questions

Simply ask Claude questions like:

- **"Find recent BBT updates for water treatment"**
- **"What does EMIS say about waste management legislation in Flanders?"**
- **"Search EMIS for information about air quality regulations"**
- **"Check the EMIS compendium for chemical substance data"**
- **"What are the latest environmental standards for industrial emissions?"**

### 2. Claude Will Automatically Use the Skill

When Claude detects your question is about EMIS data, it will:
1. Automatically call the EMIS Skill
2. Execute a live query against the EMIS portal
3. Return structured results with citations
4. Present the data in a readable format

### 3. What to Expect

- **Response Time:** 10-30 seconds (live query with authentication)
- **Format:** Structured data with tables, summaries, and source citations
- **Data:** Up to 100 results per query from the EMIS portal

---

## Setup Options

The skill supports two modes of operation. Choose the one that works best for you:

### Option 1: Backend API Mode (Recommended) ⭐

**Best for:** Most users, better performance, centralized credentials

**Requirements:**
1. Backend service must be running
2. EMIS credentials configured in backend

**Setup Steps:**

1. **Start the Backend Service:**
   ```bash
   cd backend
   
   # Option A: Using Docker (recommended)
   docker-compose up
   
   # Option B: Using Python directly
   python app.py
   ```

2. **Configure Credentials:**
   - Create `backend/.env` file:
     ```bash
     EMIS_EMAIL=tim.dhaese.27@gmail.com
     EMIS_PASSWORD=Glock179!!
     ```

3. **Verify Backend is Running:**
   - Open browser: http://localhost:38153/
   - Should see API status page

4. **That's it!** The skill will automatically connect to the backend.

**Advantages:**
- ✅ Faster queries (8 seconds with session reuse)
- ✅ Centralized credential management
- ✅ Can serve multiple users
- ✅ Better resource management

---

### Option 2: Direct Scraping Mode (Fallback)

**Best for:** Quick testing, standalone use, no backend setup

**Requirements:**
1. Playwright installed in Claude Desktop's Python environment
2. EMIS credentials as environment variables

**Setup Steps:**

1. **Install Playwright:**
   ```bash
   # In Claude Desktop's Python environment
   pip install playwright playwright-stealth
   playwright install chromium
   ```

2. **Set Environment Variables:**
   
   **On macOS/Linux:**
   ```bash
   export EMIS_EMAIL="tim.dhaese.27@gmail.com"
   export EMIS_PASSWORD="Glock179!!"
   ```
   
   **On Windows (PowerShell):**
   ```powershell
   $env:EMIS_EMAIL="tim.dhaese.27@gmail.com"
   $env:EMIS_PASSWORD="Glock179!!"
   ```
   
   **Note:** These need to be set in Claude Desktop's environment. You may need to:
   - Set them in your shell profile (`.zshrc`, `.bashrc`, etc.)
   - Or configure them in Claude Desktop's settings if supported

3. **The skill will automatically use direct mode if backend is unavailable.**

**Advantages:**
- ✅ No separate service needed
- ✅ Self-contained
- ✅ Works immediately if dependencies are installed

**Disadvantages:**
- ⚠️ Slower (each query launches a browser)
- ⚠️ Requires Playwright in Claude Desktop environment
- ⚠️ Heavier resource usage

---

## How It Works

### Automatic Mode Selection

The skill intelligently chooses the best mode:

1. **First:** Tries to connect to backend API (if `EMIS_BACKEND_URL` is set or defaults to `http://localhost:38153`)
2. **If backend unavailable:** Automatically falls back to direct scraping mode (if `EMIS_USE_DIRECT_FALLBACK=true` and Playwright is installed)
3. **If both fail:** Returns helpful error message with setup instructions

### Session Management

- **Backend Mode:** Sessions are managed by the backend service (reused across queries for 1 hour)
- **Direct Mode:** Each query creates a new session (slower but works standalone)

---

## Example Queries

### Environmental Regulations
```
"What are the latest BBT guidelines for wastewater treatment?"
"Find EMIS data on air quality standards for industrial facilities"
"What does EMIS say about waste management regulations?"
```

### Chemical Substances
```
"Search EMIS for information about chemical substance CAS 66-27-3"
"Find BBT data for methylmethanesulfonate"
"What are the environmental standards for mitomycin C?"
```

### Legislation
```
"What are the Flemish environmental legislation updates?"
"Check EMIS for recent changes to waste disposal regulations"
"Find information about environmental permits in Flanders"
```

---

## Troubleshooting

### Skill Not Responding

**Check Backend (if using Backend Mode):**
```bash
# Verify backend is running
curl http://localhost:38153/

# Check backend logs
cd backend
docker-compose logs
# OR
tail -f logs/app.log
```

**Check Direct Mode (if using Direct Mode):**
```bash
# Verify Playwright is installed
python -c "import playwright; print('OK')"

# Verify browser is installed
playwright install chromium

# Check credentials
echo $EMIS_EMAIL
echo $EMIS_PASSWORD
```

### Connection Errors

**Error: "Could not connect to backend API"**
- Backend service is not running
- Backend URL is incorrect
- Firewall blocking port 38153

**Solution:**
1. Start backend: `cd backend && python app.py`
2. Check URL: Verify `EMIS_BACKEND_URL` matches your backend
3. Check port: Ensure port 38153 is accessible

**Error: "Direct scraping failed"**
- Playwright not installed
- Browser not installed
- Credentials not set

**Solution:**
1. Install Playwright: `pip install playwright playwright-stealth`
2. Install browser: `playwright install chromium`
3. Set credentials: `export EMIS_EMAIL=...` and `export EMIS_PASSWORD=...`

### Authentication Errors

**Error: "Login failed" or "Authentication failed"**
- Credentials are incorrect
- EMIS portal is down
- Session expired

**Solution:**
1. Verify credentials are correct
2. Check EMIS portal is accessible: https://navigator.emis.vito.be
3. Try again (session may have expired)

### Slow Performance

**Queries taking too long (>30 seconds)**
- Network latency
- EMIS portal is slow
- First query (authentication takes ~28 seconds)

**Solution:**
- Subsequent queries should be faster (8 seconds with session reuse)
- Use Backend Mode for better performance
- Check network connection

---

## Configuration

### Environment Variables

**For Backend Mode:**
- `EMIS_BACKEND_URL` - Backend API URL (default: `http://localhost:38153`)
- `EMIS_API_KEY` - Optional API key if backend requires authentication

**For Direct Mode:**
- `EMIS_EMAIL` - Your EMIS portal email
- `EMIS_PASSWORD` - Your EMIS portal password
- `EMIS_USE_DIRECT_FALLBACK` - Enable/disable fallback (default: `"true"`)

### Disabling Direct Fallback

If you want to force backend-only mode:

```bash
export EMIS_USE_DIRECT_FALLBACK=false
```

This will prevent the skill from falling back to direct scraping if the backend is unavailable.

---

## Best Practices

1. **Use Backend Mode** for regular use (better performance)
2. **Be patient** - First query takes ~28 seconds (authentication)
3. **Subsequent queries** are faster (~8 seconds with session reuse)
4. **Respect rate limits** - Don't spam queries
5. **Always check citations** - Data comes from live EMIS portal queries

---

## Getting Help

If you encounter issues:

1. **Check the logs:**
   - Backend logs: `backend/logs/` or `docker-compose logs`
   - Claude Desktop console (if available)

2. **Verify setup:**
   - Backend is running (if using Backend Mode)
   - Credentials are correct
   - Network connectivity

3. **Test manually:**
   ```bash
   # Test backend API
   curl -X POST http://localhost:38153/query \
     -H "Content-Type: application/json" \
     -d '{"query":"test"}'
   
   # Test CLI directly
   cd backend
   ./scrape query emis "test"
   ```

---

## Summary

✅ **Just ask Claude questions about EMIS data** - it's that simple!

The skill will automatically:
- Detect when you need EMIS data
- Connect to the backend (or use direct mode)
- Execute authenticated queries
- Return structured results with citations

**Recommended Setup:** Use Backend Mode for best performance and reliability.

