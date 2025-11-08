# Playwright Visibility Settings

The Playwright browser automation runs in **headless mode by default** (no browser window visible) for better performance and to avoid visual distractions.

## Changes Made

### 1. Browser Window (Headless by Default) ✅
- **Default**: Browser window is hidden (`headless=True`)
- **Configurable**: Set `HEADLESS=false` environment variable to show browser window

### 2. Slow Motion Mode ✅
- **Default**: 500ms delay between actions (`PLAYWRIGHT_SLOW_MO=500`)
- Makes actions visible and easier to follow
- Configurable via `PLAYWRIGHT_SLOW_MO` environment variable (in milliseconds)

### 3. Enhanced Logging ✅
- Added detailed logging at each step:
  - Browser launch
  - Login process (navigating, filling fields, submitting)
  - Search execution
  - Data extraction
  - URLs visited

### 4. Keep Browser Open (Debug Mode) ✅
- Set `PLAYWRIGHT_KEEP_OPEN=true` to keep browser open for 30 seconds after completion
- Useful for inspecting the final state of the page
- Default: browser closes immediately

## Configuration

### Environment Variables

**In backend/.env or environment:**
```bash
# Browser visibility (default: true - headless/hidden)
# Set to false to show browser window
HEADLESS=true

# Slow motion delay in milliseconds (default: 500)
PLAYWRIGHT_SLOW_MO=500

# Keep browser open after completion (default: false)
PLAYWRIGHT_KEEP_OPEN=false
```

### Examples

**Default (headless mode - no browser visible):**
```bash
HEADLESS=true
# Or simply omit HEADLESS (defaults to true)
```

**Visible browser with slow motion (for debugging):**
```bash
HEADLESS=false
PLAYWRIGHT_SLOW_MO=1000  # 1 second delay
```

**Visible but fast:**
```bash
HEADLESS=false
PLAYWRIGHT_SLOW_MO=100  # 100ms delay
```

**Debug mode (visible + keep open):**
```bash
HEADLESS=false
PLAYWRIGHT_KEEP_OPEN=true
```

## What You'll See

**By default (headless mode):**
- Browser runs in the background
- No browser window appears
- All operations happen silently
- Faster execution

**When running in visible mode (`HEADLESS=false`):**

1. **Browser window opens** - Chromium browser launches
2. **Login page loads** - Navigates to EMIS login
3. **Form filling** - Email and password fields are filled (with delay)
4. **Form submission** - Login button is clicked
5. **Navigation** - After login, navigates to search page
6. **Search execution** - Query is entered and search is performed
7. **Results page** - Final page with data is displayed
8. **Browser closes** - Automatically closes after extraction (unless KEEP_OPEN=true)

## Logging Output

You'll see logs like:
```
2024-12-28 10:30:15 - scraper - INFO - [trace_20241228103015] Launching browser (headless=True, slow_mo=500ms)
2024-12-28 10:30:16 - scraper - INFO - [trace_20241228103015] Starting login process
2024-12-28 10:30:16 - scraper - INFO - [trace_20241228103015] Navigating to login page: https://emis.vito.be/en/user/login
2024-12-28 10:30:18 - scraper - INFO - [trace_20241228103015] Login page loaded: https://emis.vito.be/en/user/login
2024-12-28 10:30:18 - scraper - INFO - [trace_20241228103015] Filling email field
2024-12-28 10:30:19 - scraper - INFO - [trace_20241228103015] Filling password field
2024-12-28 10:30:20 - scraper - INFO - [trace_20241228103015] Submitting login form
2024-12-28 10:30:23 - scraper - INFO - [trace_20241228103015] Post-login URL: https://emis.vito.be/en/dashboard
2024-12-28 10:30:23 - scraper - INFO - [trace_20241228103015] Login successful
```

## Troubleshooting

**Want to see the browser window (for debugging):**
- Set `HEADLESS=false` in your `.env` file or environment
- Verify Playwright browsers are installed: `playwright install chromium`

**Actions too fast to see:**
- Increase `PLAYWRIGHT_SLOW_MO` (e.g., `PLAYWRIGHT_SLOW_MO=2000` for 2 seconds)

**Want to inspect the final page:**
- Set `PLAYWRIGHT_KEEP_OPEN=true` - browser stays open for 30 seconds

**Running in Docker:**
- Headless mode (default) works perfectly in Docker - no display server needed
- To show browser in Docker, you'll need X11/display server or use VNC/Xvfb
- For production, keep `HEADLESS=true` (default)

