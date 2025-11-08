# Generic Web Scraping Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/Playwright-enabled-45ba4b.svg)](https://playwright.dev/)

A flexible, configuration-driven web scraping framework that can handle **any login-protected website** with minimal setup.

Originally built for the VITO EMIS portal, now refactored into a generic multi-site scraping solution.

> **🚀 Quick Start**: See [docs/user/QUICKSTART.md](docs/user/QUICKSTART.md) for setup guide.

## Key Features

✅ **Multi-Site Support** - Add new sites with simple YAML configuration  
✅ **Multiple Interfaces** - CLI, REST API, and MCP server  
✅ **Pluggable Authentication** - Form-based, OAuth, API tokens, etc.  
✅ **Flexible Extraction** - Tables, articles, structured content  
✅ **Session Management** - Persistent sessions with proper concurrency handling  
✅ **Backwards Compatible** - Existing EMIS integrations still work  

## Architecture

This project provides three ways to use the scraper:

1. **CLI** (`backend/cli.py`) - Command-line interface for terminal use
2. **REST API** (`backend/app.py`) - FastAPI service for HTTP access
3. **MCP Server** (`mcp-server/`) - Model Context Protocol integration for Claude Desktop

All interfaces share the same core scraping framework with configurable authentication and data extraction strategies.

## Quick Start

### Prerequisites

- Python 3.9+ (required)
- Docker and Docker Compose (optional - for containerized deployment)
- Credentials for target sites (e.g., EMIS portal email and password)

### Installation

```bash
# Clone and navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Set up credentials
cp .env.example .env
# Edit .env and add your credentials
```

### Backend Setup

You can run the backend either with Docker or in a local virtual environment. Choose the method that works best for you.

#### Option 1: Docker (Containerized)

1. Navigate to the backend directory:
```bash
cd backend
```

2. Copy the environment template:
```bash
cp .env.example .env
```

3. Edit `.env` and add your EMIS credentials:
```
EMIS_EMAIL=your_email@example.com
EMIS_PASSWORD=your_password
```

4. Run with Docker Compose:
```bash
docker-compose up --build
```

See `backend/SETUP_LOCAL.md` for detailed local virtual environment setup instructions.

### Local Virtual Environment Setup (Recommended)

1. **Create and activate a virtual environment:**
```bash
cd backend
python3 -m venv venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

3. **Set up environment variables:**
```bash
# Copy the example if it doesn't exist
cp .env.example .env

# Edit .env and add your EMIS credentials:
# EMIS_EMAIL=your_email@example.com
# EMIS_PASSWORD=your_password
# PORT=38153
```

4. **Start the server:**
```bash
python app.py
# OR use the helper script:
./start.sh
```

**Note:** The `start.sh` script automatically activates the virtual environment if `venv` or `.venv` exists.

## ⚠️ CRITICAL: Port Configuration

**The server MUST run on port 38153, NOT port 8000!**

### ✅ CORRECT Way to Start (Use This!)
```bash
python app.py
# OR
./start.sh
```

### ❌ WRONG Way (Will Use Port 8000!)
```bash
uvicorn app:app              # ❌ WRONG - uses port 8000
uvicorn app:app --reload     # ❌ WRONG - uses port 8000
```

### If You Must Use Uvicorn Directly
```bash
PORT=38153 uvicorn app:app --port 38153
```

**Why?** When you run `uvicorn app:app` directly, it bypasses the port configuration in `app.py` and defaults to port 8000. The MCP Server and Docker setup expect port 38153.

See `backend/PORT_CONFIGURATION.md` for detailed explanation.

The backend API will be available at `http://localhost:38153` (default port)

## Usage

### 1. Command Line Interface (CLI)

The easiest way to test and use the scraper:

```bash
# List available sites
./scrape list

# Query a site
./scrape query emis "BBT water treatment"

# Different output formats
./scrape query emis "water" --format json
./scrape query emis "water" --format table
./scrape query emis "water" --raw

# Check credentials
./scrape check emis

# View configuration
./scrape config emis
```

**See [docs/user/CLI_USAGE.md](docs/user/CLI_USAGE.md) for complete CLI documentation.**

### 2. REST API

Start the API server:

```bash
# Using Python directly
python app.py

# Or using the helper script
./start.sh

# Or with Docker
docker-compose up
```

API endpoints:

```bash
# Health check
curl http://localhost:38153/

# List sites
curl http://localhost:38153/sites

# Query default site (EMIS)
curl -X POST http://localhost:38153/query \
  -H "Content-Type: application/json" \
  -d '{"query": "BBT water treatment"}'

# Query specific site
curl -X POST http://localhost:38153/query/your_site \
  -H "Content-Type: application/json" \
  -d '{"query": "search term"}'
```

### 3. MCP Server

Connect via Model Context Protocol for AI agent integration with Claude Desktop.

**Quick Setup:**
1. Start the backend (see above)
2. **macOS**: Double-click `macos/generate-mcp-config.command`<br>**Windows**: Double-click `windows\generate-mcp-config.bat`
3. Add the configuration to Claude Desktop settings
4. Restart Claude Desktop

See [MCP_CLAUDE_DESKTOP_SETUP.md](MCP_CLAUDE_DESKTOP_SETUP.md) for detailed setup instructions.

## Adding a New Site

1. **Create configuration** (`backend/sites/your_site.yaml`):
```yaml
site_id: your_site
name: Your Website
base_url: https://example.com

auth:
  type: form_based
  login_url: https://example.com/login
  selectors:
    email_field: 'input[name="email"]'
    password_field: 'input[name="password"]'
    submit_button: 'button[type="submit"]'
  success_indicators:
    - type: url_change
      pattern: "!login"

extraction:
  strategies:
    - type: table
      selector: 'table.results'
    - type: content
      selector: 'main'
```

2. **Set credentials**:
```bash
export YOUR_SITE_EMAIL=user@example.com
export YOUR_SITE_PASSWORD=password
```

3. **Test it**:
```bash
./scrape check your_site
./scrape query your_site "test search"
```

**See [docs/user/GENERIC_FRAMEWORK.md](docs/user/GENERIC_FRAMEWORK.md) for complete documentation.**

## Project Structure

```
emis/
├── backend/                    # Core scraping framework
│   ├── core/                  # Framework components
│   │   ├── scraper.py        # Generic scraper
│   │   ├── session_manager.py # Session handling
│   │   └── config_loader.py  # Config management
│   ├── auth/                  # Authentication strategies
│   │   ├── base.py
│   │   └── strategies/
│   ├── extractors/            # Data extraction
│   │   ├── table.py
│   │   └── content.py
│   ├── sites/                 # Site configurations
│   │   ├── emis.yaml
│   │   └── example.yaml
│   ├── cli.py                # Command-line interface
│   ├── app.py                # REST API server
│   └── scrape                # CLI wrapper script
├── mcp-server/               # MCP integration
├── macos/                     # macOS setup scripts (.command files)
├── windows/                   # Windows setup scripts (.bat files)
├── docs/                      # Documentation
│   ├── user/                 # User guides
│   │   ├── QUICKSTART.md
│   │   ├── CLI_USAGE.md
│   │   └── GENERIC_FRAMEWORK.md
│   ├── development/          # Developer docs
│   │   └── REFACTORING_SUMMARY.md
│   └── archived/             # Historical docs
├── examples/                  # Example scripts and configs
│   ├── example.yaml
│   ├── basic_usage.sh
│   └── batch_scraping.py
├── LICENSE                    # MIT License
├── CONTRIBUTING.md            # Contribution guidelines
├── SECURITY.md                # Security policy
└── CHANGELOG.md               # Version history
```

## Testing

### Quick Test with CLI

```bash
cd backend

# List sites
./scrape list

# Test query
./scrape query emis "test"

# Verbose output
./scrape -v query emis "test"
```

### Test API

```bash
# Start server
python app.py

# In another terminal
curl http://localhost:38153/sites
curl -X POST http://localhost:38153/query/emis \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

### Debug Mode

```bash
# Watch browser in action
HEADLESS=false ./scrape query emis "test"

# Slow motion
PLAYWRIGHT_SLOW_MO=2000 ./scrape query emis "test"
```

## Security Notes

- Never commit `.env` files or credentials
- Session data is stored locally in `backend/data/session.json`
- The backend uses Playwright with stealth plugins to avoid detection
- All scraping respects rate limits and uses human-like delays

## Troubleshooting

### Backend Connection Issues

**Error**: "Could not connect to backend API"
- **Solution**: The backend service is not running. Start it with `docker-compose up` or `python app.py`
- See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions

### Other Common Issues

- **Backend won't start**: Check that EMIS credentials are set in `.env`
- **Login fails**: Verify credentials are correct and account is active
- **MCP Server can't connect**: Ensure backend is running and `EMIS_BACKEND_URL` is correct
- **Timeout errors**: EMIS portal may be slow; backend allows up to 120 seconds
- **Port conflicts**: Change `PORT` in `.env` if 38153 is already in use

For more troubleshooting help, see [QUICKSTART.md](QUICKSTART.md).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Ways to contribute:
- Add new site configurations
- Report bugs or request features
- Improve documentation
- Add new authentication/extraction strategies

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Playwright](https://playwright.dev/) for browser automation
- Originally developed for the VITO EMIS portal
- Inspired by the need for a generic, maintainable web scraping solution

## Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/discussions)
- **Security**: See [SECURITY.md](SECURITY.md) for reporting vulnerabilities

---

**⭐ Star this repository if you find it useful!**

