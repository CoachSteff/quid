# Troubleshooting Guide

Common issues and solutions for the Generic Web Scraping Framework.

## Backend Connection Issues

### Backend Won't Start

**Error**: Port 91060 is already in use

**Solution**: 
1. Change the port in `.env`:
   ```
   PORT=38154
   ```
2. Update `EMIS_BACKEND_URL` in MCP configuration if using MCP Server
3. Or kill the existing process:
   ```bash
   # Find process
   ps aux | grep app.py
   
   # Kill it
   pkill -f app.py
   ```

### Connection Refused Error

**Error**: MCP Server or API can't connect to backend

**Solutions**:
1. Verify backend is running: `curl http://localhost:91060/`
2. Check if backend is on a different port
3. Ensure `EMIS_BACKEND_URL` environment variable matches your backend URL

### ModuleNotFoundError: No module named 'fastapi'

**Cause**: Running with system Python instead of venv Python

**Solution**: Use one of the correct methods:
```bash
# Option 1: Use start script
cd backend
./start.sh

# Option 2: Use venv Python directly
cd backend
venv/bin/python app.py

# Option 3: Activate venv first
cd backend
source venv/bin/activate
python app.py
```

## Authentication Issues

### Authentication Errors

**Error**: 401 Unauthorized or 500 errors

**Solutions**:
1. Verify EMIS credentials in `.env` are correct
2. Check backend logs for detailed error messages
3. Test credentials with CLI: `./scrape check emis`

### Login Fails

**Error**: Cannot log in to site

**Solutions**:
1. Verify credentials are correct and account is active
2. Test with visible browser: `HEADLESS=false ./scrape query emis "test"`
3. Check if site structure changed (selectors may need updating)
4. Verify credentials format in `.env` (no extra spaces)

## Port Configuration

### Server Running on Wrong Port

**Problem**: Server is on port 8000 instead of 91060

**Solution**:
1. Stop the server (Ctrl+C or kill process)
2. Check your `.env` file - it should have `PORT=91060`
3. Restart using the correct method:
   ```bash
   python app.py  # NOT uvicorn app:app
   ```
4. Verify it's on the correct port:
   ```bash
   curl http://localhost:38153/
   ```

**Why?** When you run `uvicorn app:app` directly, it bypasses the port configuration in `app.py` and defaults to port 8000. Always use `python app.py` instead.

## CLI Issues

### Command Not Found

**Error**: `./scrape: command not found`

**Solution**:
```bash
# Make sure script is executable
chmod +x backend/scrape

# Or call Python directly
python3 backend/cli.py list
```

### Import Errors

**Error**: `ModuleNotFoundError` or import failures

**Solution 1**: Use the wrapper script (recommended)
```bash
cd backend
./scrape list  # This handles Python path correctly
```

**Solution 2**: Activate virtual environment
```bash
cd backend
source venv/bin/activate
python3 cli.py list
```

**Solution 3**: Check dependencies are installed
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
```

### Site ID Mismatch Error

**Problem**: Configuration file site_id doesn't match filename

**Error message**:
```
ERROR: Failed to load config for site 'example': Site ID mismatch
```

**Cause**: The `site_id` in the YAML file must match the filename (without .yaml)

**Solution**:
```bash
# If file is example.yaml, ensure:
site_id: example  # NOT example_site

# Or rename file to match site_id:
mv example.yaml example_site.yaml  # If site_id is example_site
```

**Rule**: `sites/[FILENAME].yaml` must have `site_id: [FILENAME]`

## Browser Issues

### Playwright Browser Not Found

**Error**: Browser executable not found

**Solution**:
```bash
# Reinstall Playwright browsers
playwright install chromium

# Verify installation
playwright --version
```

### Browser Crashes or Timeouts

**Error**: Browser timeout or crashes

**Solutions**:
1. Test with visible browser to see what's happening:
   ```bash
   HEADLESS=false ./scrape query emis "test"
   ```
2. Increase timeout in site YAML configuration
3. Check network connectivity: `ping emis.vito.be`
4. Try slow motion mode to debug:
   ```bash
   PLAYWRIGHT_SLOW_MO=2000 ./scrape query emis "test"
   ```

## Data Extraction Issues

### Selector Not Found Errors

**Problem**: Page elements can't be located

**Debug Steps**:
```bash
# 1. View current selectors
./scrape config emis | jq '.extraction.strategies'

# 2. Watch browser with slow motion
HEADLESS=false PLAYWRIGHT_SLOW_MO=2000 ./scrape -v query emis "test"

# 3. Check if site structure changed
# Update selectors in sites/emis.yaml if needed
```

### No Results Returned

**Problem**: Query succeeds but returns no data

**Solutions**:
1. Check if site structure changed - selectors may need updating
2. Verify search query is correct
3. Test with verbose mode: `./scrape -v query emis "test"`
4. Check extraction strategies in site configuration

## MCP Server Issues

### "I don't see any EMIS tools"

**Check**:
1. Backend is running: `curl http://localhost:38153/`
2. Config file saved correctly
3. Claude Desktop restarted completely
4. Path to `server.py` is correct (absolute path)

### "Connection refused" or "Backend unavailable"

**Solution**:
1. Start backend: 
   - **macOS**: Double-click `macos/start-quid-backend.command`
   - **Windows**: Double-click `windows\start-quid-backend.bat`
2. Verify: Open http://localhost:38153 in browser
3. Should see: `{"status":"ok",...}`

### "ModuleNotFoundError: No module named 'mcp'"

**Solution**:
Install MCP dependencies:
```bash
cd mcp-server
pip install -r requirements.txt
```

## Performance Issues

### Slow Queries

**Expected Performance**:
- **First query:** ~28 seconds (authentication)
- **Subsequent queries:** ~8 seconds (session reuse)

**If slower than expected**:
1. Check network connectivity
2. Verify session is being reused (check logs)
3. Test with visible browser to see where it's slow
4. Check if site is experiencing high load

### High Memory Usage

**Problem**: Backend using too much memory

**Solutions**:
1. Restart backend periodically
2. Clear old session files: `rm backend/data/sessions/*.json`
3. Check for memory leaks in logs

## Environment Variables

### Environment Variables Not Loading

**Problem**: Changes to `.env` not taking effect

**Solutions**:
- Check that `.env` file exists in `backend/` directory
- Verify `python-dotenv` is installed: `pip list | grep python-dotenv`
- Check `.env` file format (no spaces around `=`)
- Restart backend after changing `.env`

### Wrong Credentials Being Used

**Problem**: Backend using wrong credentials

**Check**:
1. Verify `.env` file has correct credentials
2. Check for environment variables set in shell: `env | grep EMIS`
3. Shell variables override `.env` file
4. Restart backend after changing credentials

## Docker Issues

### Container Fails to Start

**Solutions**:
1. Check Docker is running: `docker ps`
2. View logs: `docker-compose logs`
3. Rebuild container: `docker-compose up --build`
4. Check `.env` file exists and has correct credentials

### Port Conflicts with Docker

**Problem**: Port 38153 already in use

**Solution**:
1. Stop other services using port 38153
2. Or change port in `docker-compose.yml` and `.env`

## Getting More Help

### Debug Mode

Enable verbose logging:
```bash
# CLI verbose mode
./scrape -v query emis "test"

# Watch browser
HEADLESS=false ./scrape query emis "test"

# Slow motion for debugging
PLAYWRIGHT_SLOW_MO=2000 ./scrape query emis "test"
```

### Check Logs

**Backend logs**: Check terminal output where backend is running

**MCP Server logs**: Check Claude Desktop console/logs

**CLI logs**: Use `-v` flag for verbose output

### Verify Configuration

```bash
# Check site configuration
./scrape config emis

# Check credentials
./scrape check emis

# List available sites
./scrape list
```

## Still Having Issues?

1. Check backend logs for detailed error messages
2. Test with visible browser (`HEADLESS=false`) to see what's happening
3. Verify all prerequisites are installed
4. Check [GitHub Issues](https://github.com/yourusername/generic-web-scraper/issues) for similar problems
5. Review [Advanced Configuration](docs/advanced/GENERIC_FRAMEWORK.md) for customization options

