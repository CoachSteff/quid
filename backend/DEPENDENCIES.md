# Dependency Documentation

This document explains the dependencies used in the Generic Web Scraping Framework and any compatibility considerations.

## Core Dependencies

### Web Framework
- **fastapi** (0.104.1) - Modern async web framework for the REST API
- **uvicorn[standard]** (0.24.0) - ASGI server with WebSocket support

### Browser Automation
- **playwright** (1.40.0) - Cross-browser automation library
- **playwright-stealth** (1.0.6) - Anti-detection plugin for Playwright

### Data & Configuration
- **pydantic** (2.5.0) - Data validation and settings management
- **python-dotenv** (1.0.0) - Environment variable loading from .env files
- **pyyaml** (6.0.1) - YAML configuration file parsing

### Build Tools
- **setuptools** (>=65.0.0,<81.0.0) - Package installation and distribution

## Version Compatibility Notes

### playwright-stealth

**Pinned Version**: 1.0.6

**Why Pinned:**
- Version 1.0.6 uses `stealth_async()` function API
- Version 2.0+ changed to `Stealth()` class with `apply_stealth_async()` method
- Breaking API change between major versions

**Code Compatibility:**
The framework includes automatic fallback handling in `core/scraper.py`:

```python
try:
    from playwright_stealth import stealth_async
except ImportError:
    # Fallback for v2.0+
    from playwright_stealth import Stealth
    async def stealth_async(context):
        stealth = Stealth()
        await stealth.apply_stealth_async(context)
```

**Upgrading:**
If you want to upgrade to playwright-stealth 2.0+:
```bash
pip install playwright-stealth>=2.0.0
```
The code will automatically use the v2.0+ API.

**Staying on 1.0.6:**
Current pinned version works reliably:
```bash
pip install playwright-stealth==1.0.6
```

### Python Version

**Minimum Required**: Python 3.9+

**Tested With**:
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

**Why 3.9+:**
- Uses modern async/await features
- Type hints with `from __future__ import annotations`
- Pydantic 2.x requires Python 3.7+, but we use features from 3.9+

### Playwright Browser

**Required Browser**: Chromium

**Installation:**
```bash
playwright install chromium
```

**Optional Browsers:**
The framework is configured for Chromium but could be adapted for Firefox or WebKit:
```python
# In core/scraper.py
browser = await p.chromium.launch(...)  # Current
browser = await p.firefox.launch(...)   # Alternative
browser = await p.webkit.launch(...)    # Alternative
```

## Installation

### Standard Installation

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Chromium browser
playwright install chromium
```

### Docker Installation

```bash
cd backend
docker-compose up --build
```

The Dockerfile handles all dependencies including browser installation.

## Dependency Issues & Solutions

### Issue: playwright-stealth Import Error

**Symptoms:**
```
ImportError: cannot import name 'stealth_async'
AttributeError: module 'playwright_stealth' has no attribute 'stealth_async'
```

**Cause:** Version mismatch or incomplete installation

**Solution:**
```bash
# Reinstall pinned version
pip uninstall playwright-stealth
pip install playwright-stealth==1.0.6

# Verify
python3 -c "import playwright_stealth; print(playwright_stealth.__version__)"
```

### Issue: Playwright Browser Not Found

**Symptoms:**
```
playwright._impl._api_types.Error: Executable doesn't exist
```

**Cause:** Playwright browsers not installed

**Solution:**
```bash
playwright install chromium

# Or install all browsers
playwright install
```

### Issue: FastAPI Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Cause:** Dependencies not installed in virtual environment

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Issue: SSL Certificate Errors

**Symptoms:**
```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Cause:** System SSL certificates not configured

**Solution (macOS):**
```bash
# Install certificates
/Applications/Python\ 3.x/Install\ Certificates.command
```

**Solution (Linux):**
```bash
# Update CA certificates
sudo apt-get install ca-certificates
```

## Development Dependencies

For development and testing, you may want additional packages:

```bash
# Code formatting
pip install black ruff

# Type checking
pip install mypy

# Testing
pip install pytest pytest-asyncio pytest-cov

# Documentation
pip install mkdocs mkdocs-material
```

## Upgrading Dependencies

### Check for Updates

```bash
# Show outdated packages
pip list --outdated

# Check specific package
pip show playwright
```

### Upgrade Safely

```bash
# Upgrade specific package
pip install --upgrade fastapi

# Test thoroughly after upgrading
./scrape list
./scrape query emis "test"
```

### Regenerate requirements.txt

If you modify dependencies:

```bash
# From current environment
pip freeze > requirements.txt

# Or manually edit requirements.txt with specific versions
```

## Security Updates

### Checking for Vulnerabilities

```bash
# Using pip-audit (install first)
pip install pip-audit
pip-audit

# Using safety
pip install safety
safety check
```

### Update Security Patches

```bash
# Update to latest patch version
pip install --upgrade playwright==1.40.*
pip install --upgrade fastapi==0.104.*
```

## Platform-Specific Notes

### macOS

- Chromium installation may require Rosetta 2 on Apple Silicon
- Use `arch -x86_64` prefix if needed

```bash
arch -x86_64 playwright install chromium
```

### Linux

- May need additional system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install libnss3 libatk-bridge2.0-0 libx11-xcb1 libxcomposite1 \
  libxdamage1 libxrandr2 libgbm1 libasound2

# Fedora/RHEL
sudo dnf install nss atk at-spi2-atk cups-libs libdrm mesa-libgbm
```

### Windows

- Use PowerShell or CMD for commands
- Virtual environment activation: `venv\Scripts\activate`
- May need Visual C++ redistributables

## Docker Considerations

The Dockerfile includes all dependencies:

```dockerfile
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium
```

**Note:** `--with-deps` installs system dependencies required by Chromium.

## Troubleshooting Checklist

When encountering dependency issues:

1. ✅ **Virtual environment activated?**
   ```bash
   which python  # Should show venv path
   ```

2. ✅ **Dependencies installed?**
   ```bash
   pip list | grep playwright
   ```

3. ✅ **Browser installed?**
   ```bash
   playwright install chromium
   ```

4. ✅ **Correct Python version?**
   ```bash
   python --version  # Should be 3.9+
   ```

5. ✅ **Requirements up to date?**
   ```bash
   pip install -r requirements.txt
   ```

## Related Documentation

- [CLI Usage Guide](../docs/user/CLI_USAGE.md) - Troubleshooting section
- [Quick Start](../docs/user/QUICKSTART.md) - Installation guide
- [Contributing](../CONTRIBUTING.md) - Development setup

## References

- [Playwright Documentation](https://playwright.dev/python/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [playwright-stealth GitHub](https://github.com/AtuboDad/playwright_stealth)
