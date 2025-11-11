# Quid MCP - Universal Content Access Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/Playwright-enabled-45ba4b.svg)](https://playwright.dev/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-blue.svg)](https://modelcontextprotocol.io/)

**Quid** (Latin: "what?") - A modular platform for AI assistants to access content behind search engines, login walls, and paywalls. Think **"Perplexity for protected documents"**.

Originally built for the VITO EMIS environmental portal, now evolved into a universal content access layer with plugin-based architecture.

## Vision

Democratize information retrieval from protected sources while respecting authentication, security, and ethical boundaries. Enable Claude and other AI assistants to access diverse content platforms through a unified interface.

## Key Features

✅ **Plugin Architecture** - Each content source is a self-contained, installable plugin  
✅ **Multiple Auth Scenarios** - Simple forms, API keys, OAuth 2.0, CAPTCHA, 2FA/MFA  
✅ **Diverse Content Types** - HTML, PDFs, tables, JSON APIs, Markdown  
✅ **Multiple Interfaces** - CLI, REST API, and MCP server for AI assistants  
✅ **Ethical Framework** - Built-in guidelines for responsible content access  
✅ **Open Source** - MIT licensed, community-driven plugin ecosystem  
✅ **Session Management** - Persistent sessions with proper concurrency handling  
✅ **Backwards Compatible** - Existing EMIS integrations still work  

## Use Cases

- 🏥 **Medical/Pharmaceutical**: medicines.org.uk, FDA databases, clinical trials
- ⚖️ **Legal/Compliance**: Staatsblad Monitor, EUR-Lex, legal databases  
- 🔬 **Research**: Academic journals, scientific databases, preprint servers
- 🌍 **Environmental**: EMIS portal, environmental agency data
- 💼 **Business Intelligence**: Industry reports, market research platforms
- 📚 **Technical Documentation**: API docs, developer portals

## Available Plugins

- **EMIS** - VITO Environmental Information System (Belgium)
- **Template** - Starter template for creating new plugins

*More plugins coming soon! Contributions welcome.*

## Getting Started

**New to Quid?** Start here: **[Getting Started Guide](docs/GETTING_STARTED.md)** 🚀

### Prerequisites

- Python 3.9+ installed
- Docker and Docker Compose (optional - for containerized deployment)
- Credentials for target sites (e.g., EMIS portal email and password)

### Installation

**Easy Setup (Recommended):**

For the easiest installation experience, use our platform-specific setup scripts that guide you through the entire process:

**macOS:**
```bash
# Double-click in Finder or run:
open macos/setup-quid.command
```

**Windows:**
```batch
REM Double-click in File Explorer or run:
windows\setup-quid.bat
```

The setup script will prompt you to choose between:
- **Virtual Environment** (Python venv) - Faster, best for development, runs on port 91060
- **Docker** (containerized) - Isolated environment, no Python issues, runs on port 8906

It will then automatically:
1. Check prerequisites (Python or Docker)
2. Set up the environment
3. Prompt for credentials
4. Configure everything for you

**Manual Installation (Advanced):**

If you prefer manual setup:

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Set up credentials:**
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials:
   # EMIS_EMAIL=your_email@example.com
   # EMIS_PASSWORD=your_password
   # PORT=91060
   ```

### Starting the Backend

**Easy Start (Recommended):**

If you used the setup script, starting is just as easy:

**macOS:**
```bash
# Double-click in Finder or run:
open macos/start-quid-backend.command
```

**Windows:**
```batch
REM Double-click in File Explorer or run:
windows\start-quid-backend.bat
```

**Docker (if you chose Docker during setup):**
```bash
docker-compose up
# Or run in background: docker-compose up -d
```

**Ports:**
- Virtual Environment: `http://localhost:91060`
- Docker: `http://localhost:8906`

**Manual Start (Advanced):**

**Option 1: Command Line**
```bash
cd backend
python app.py
```

**Option 2: Helper Script**
```bash
cd backend
./start.sh
```

**To Stop the Backend:**
- **Virtual Environment:** Press `Ctrl+C` in the terminal, or run: `pkill -f "python.*app.py"`
- **Docker:** `docker-compose down`
- **macOS/Windows GUI:** Close the Terminal/Command Prompt window

### Verify Installation

Test the health check endpoint (use the appropriate port for your deployment):

**Virtual Environment:**
```bash
curl http://localhost:91060/
```

**Docker:**
```bash
curl http://localhost:8906/
```

You should see:
```json
{"status": "ok", "service": "Quid MCP API", "version": "2.0.0"}
```

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

Start the API server (see above), then use (replace `PORT` with your deployment port: `91060` for venv or `8906` for Docker):

```bash
# Health check
curl http://localhost:PORT/

# List legacy sites
curl http://localhost:PORT/sites

# List plugins
curl http://localhost:PORT/plugins

# Get plugin details
curl http://localhost:PORT/plugins/emis

# Enable/disable plugin
curl -X POST http://localhost:PORT/plugins/emis/enable
curl -X POST http://localhost:PORT/plugins/emis/disable

# Query default site (EMIS)
curl -X POST http://localhost:PORT/query \
  -H "Content-Type: application/json" \
  -d '{"query": "BBT water treatment"}'

# Query specific site (plugin or legacy)
curl -X POST http://localhost:PORT/query/your_site \
  -H "Content-Type: application/json" \
  -d '{"query": "search term"}'
```

**Examples:**
```bash
# Virtual Environment (port 91060)
curl http://localhost:91060/plugins
curl http://localhost:91060/plugins/emis

# Docker (port 8906)
curl http://localhost:8906/plugins
curl http://localhost:8906/plugins/emis
```

### 3. MCP Server

Connect via Model Context Protocol for AI agent integration with Claude Desktop.

**Quick Setup:**
1. Start the backend (see above)
2. **macOS**: Double-click `macos/generate-mcp-config.command`  
   **Windows**: Double-click `windows\generate-mcp-config.bat`
3. Add the configuration to Claude Desktop settings
4. Restart Claude Desktop

**See [MCP Setup Guide](docs/user/MCP_CLAUDE_DESKTOP_SETUP.md) for detailed setup instructions.**

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

**See [docs/advanced/GENERIC_FRAMEWORK.md](docs/advanced/GENERIC_FRAMEWORK.md) for complete framework documentation.**

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
│   ├── advanced/             # Advanced features
│   ├── troubleshooting/      # Troubleshooting guides
│   ├── testing/              # Testing scenarios
│   └── development/          # Developer docs
├── examples/                  # Example scripts and configs
├── LICENSE                    # MIT License
├── CONTRIBUTING.md            # Contribution guidelines
├── SECURITY.md                # Security policy
└── CHANGELOG.md               # Version history
```

## Quick Testing

### Test with CLI

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

## Documentation

### 📚 Essential Guides

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Complete beginner's guide (start here!)
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Command cheat sheet
- **[Roadmap](docs/ROADMAP.md)** - Development roadmap and future plans
- **[Changelog](CHANGELOG.md)** - Version history and updates

### 🔌 Plugin Development

- **[Plugin Template](plugins/template/)** - Create your own plugins
- **[EMIS Plugin](plugins/emis/)** - Example plugin documentation
- **[Ethical Guidelines](docs/guides/ETHICAL_GUIDELINES.md)** - Responsible use framework

### 📖 User Guides

- **[CLI Usage](docs/user/CLI_USAGE.md)** - Complete CLI guide with examples
- **[MCP Setup](docs/user/MCP_CLAUDE_DESKTOP_SETUP.md)** - Setting up MCP server for Claude Desktop
- **[Troubleshooting](docs/troubleshooting/)** - Common issues and solutions

### 🛠️ Developer Guides

- **[Generic Framework](docs/advanced/GENERIC_FRAMEWORK.md)** - Adding new sites and extending the framework
- **[Advanced Features](docs/advanced/)** - Advanced configuration and customization
- **[Testing](docs/testing/)** - Testing scenarios and best practices

## Security Notes

- Never commit `.env` files or credentials
- Session data is stored locally in `backend/data/sessions/`
- The backend uses Playwright with stealth plugins to avoid detection
- All scraping respects rate limits and uses human-like delays

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
- Evolved into Quid MCP - a universal content access platform
- Inspired by the need to democratize information access for AI assistants
- Community-driven with contributions welcome

## Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/yourusername/generic-web-scraper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/generic-web-scraper/discussions)
- **Security**: See [SECURITY.md](SECURITY.md) for reporting vulnerabilities

---

**⭐ Star this repository if you find it useful!**
