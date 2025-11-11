# Getting Started with Quid MCP

Welcome to **Quid MCP** - your universal content access platform! This guide will get you up and running in minutes.

## What is Quid?

Quid (Latin: "what?") helps AI assistants like Claude access content behind login walls and search engines. Think of it as "Perplexity for protected documents."

**Key Features:**
- 🔌 Plugin-based architecture for multiple content sources
- 🔐 Multiple authentication methods (forms, API keys, OAuth)
- 🤖 Direct integration with Claude Desktop via MCP
- 📊 Extracts tables, documents, PDFs, and more
- ⚖️ Built-in ethical guidelines for responsible use

## Prerequisites

- **Python 3.9+** installed
- **Git** (optional, for cloning)
- **Credentials** for services you want to access (e.g., EMIS account)

## Quick Start (5 Minutes)

### Step 1: Install Quid

```bash
# Clone or download the repository
cd quid

# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install browser
playwright install chromium
```

### Step 2: Configure Credentials

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your favorite editor
```

Add your credentials:
```env
EMIS_EMAIL=your_email@example.com
EMIS_PASSWORD=your_password
PORT=38153
```

### Step 3: Start the Backend

```bash
# Simple start
python app.py

# The server will start on http://localhost:38153
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:38153
```

### Step 4: Test It

Open a new terminal:

```bash
cd backend
source venv/bin/activate  # Activate venv again

# Test query
./scrape query emis "water treatment"
```

**Success!** You should see search results from the EMIS portal.

## Three Ways to Use Quid

### 1. Command Line (Easiest)

Perfect for quick queries and testing.

```bash
# List available plugins
./scrape list

# Query a plugin
./scrape query emis "environmental permits"

# JSON output
./scrape query emis "waste management" --format json

# Check authentication
./scrape check emis
```

### 2. REST API (For Developers)

Integrate Quid into your applications.

```bash
# Health check
curl http://localhost:38153/

# List plugins
curl http://localhost:38153/sites

# Query
curl -X POST http://localhost:38153/query/emis \
  -H "Content-Type: application/json" \
  -d '{"query": "water treatment"}'
```

### 3. MCP Server (For Claude Desktop)

Use Quid directly in Claude Desktop!

#### Setup MCP (One-Time)

1. **Start the backend** (see Step 3 above)

2. **Generate MCP configuration**:
   - **macOS**: Double-click `macos/generate-mcp-config.command`
   - **Windows**: Double-click `windows\generate-mcp-config.bat`
   - **Manual**: See `docs/user/MCP_CLAUDE_DESKTOP_SETUP.md`

3. **Restart Claude Desktop**

#### Use in Claude

Now you can ask Claude:

> "Query EMIS for information about water treatment techniques"

> "What does EMIS say about environmental legislation in Flanders?"

Claude will use Quid to fetch the information!

## Available Plugins

### EMIS (Active)
**Category**: 🌍 Environmental  
**Description**: VITO Environmental Information System (Belgium)  
**Auth**: Simple form login  
**Content**: Environmental legislation, permits, BBT/BAT documents

**Setup**:
```bash
export EMIS_EMAIL=your_email@example.com
export EMIS_PASSWORD=your_password
```

### More Coming Soon!

- 🏥 medicines.org.uk - UK drug information
- ⚖️ Staatsblad Monitor - Belgian official gazette
- 🔬 Research databases
- 📚 Technical documentation portals

**Want to add a plugin?** See [Creating a Plugin](#creating-a-plugin) below!

## Creating a Plugin

Add support for new content sources in 4 easy steps!

### Step 1: Copy Template

```bash
cd plugins
cp -r template my_website
cd my_website
```

### Step 2: Edit config.yaml

```yaml
plugin:
  id: my_website
  name: My Website
  version: 1.0.0
  author: Your Name
  category: medical  # Choose: medical, legal, research, etc.
  
auth:
  scenario: simple_form  # or: api_key, none
  login_url: https://example.com/login
  selectors:
    email_field: 'input[name="email"]'
    password_field: 'input[name="password"]'
    submit_button: 'button[type="submit"]'

extraction:
  strategies:
    - type: table
    - type: content
```

### Step 3: Set Credentials

```bash
export MY_WEBSITE_EMAIL=user@example.com
export MY_WEBSITE_PASSWORD=password
```

### Step 4: Test Your Plugin

```bash
./scrape check my_website
./scrape query my_website "test search"
```

**That's it!** See `plugins/template/README.md` for detailed guide.

## Troubleshooting

### Backend won't start

```bash
# Check if port is in use
lsof -i :38153

# Kill existing process
pkill -f "python.*app.py"

# Try again
python app.py
```

### "Command not found: ./scrape"

```bash
# Make sure you're in the backend directory
cd backend

# Make script executable
chmod +x scrape

# Try again
./scrape list
```

### Authentication fails

```bash
# Verify credentials
./scrape check emis

# Check environment variables
echo $EMIS_EMAIL
echo $EMIS_PASSWORD

# Try verbose mode for details
./scrape -v query emis "test"
```

### Browser issues

```bash
# Reinstall Playwright
playwright install chromium

# Check installation
playwright install --dry-run
```

### Still stuck?

- Check `docs/troubleshooting/` directory
- Open an issue on GitHub
- See `docs/QUICK_REFERENCE.md` for more help

## Next Steps

### Learn More

- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Command cheat sheet
- **[Ethical Guidelines](docs/guides/ETHICAL_GUIDELINES.md)** - Responsible use
- **[Plugin Development](plugins/template/README.md)** - Create your own plugins
- **[Roadmap](ROADMAP.md)** - What's coming next

### Contribute

- **Create plugins** for new content sources
- **Report issues** or suggest features
- **Improve documentation**
- **Share your use cases**

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Stay Updated

- ⭐ Star the project on GitHub
- 👀 Watch for updates
- 📢 Join discussions

## Use Cases

### Academic Research
```bash
./scrape query emis "environmental impact assessment"
# Access research databases through your institutional login
```

### Legal Research
```bash
# Create plugin for legal database
# Query case law and regulations
```

### Medical Information
```bash
# Create plugin for drug databases
# Access pharmaceutical information
```

### Environmental Data
```bash
./scrape query emis "waste management legislation"
# Query environmental databases
```

## Ethical Use

Quid is designed for **responsible, ethical access** to content:

✅ **Do:**
- Use your own legitimate credentials
- Respect rate limits
- Follow terms of service
- Cite sources
- Use for personal research and AI assistance

❌ **Don't:**
- Share credentials
- Bypass paywalls to avoid payment
- Extract content for resale
- Violate terms of service
- Overwhelm servers with requests

Read full [Ethical Guidelines](docs/guides/ETHICAL_GUIDELINES.md)

## Support

### Documentation
- `docs/` directory - Comprehensive guides
- `README.md` - Project overview
- `QUICK_REFERENCE.md` - Command reference

### Community
- GitHub Issues - Bug reports and feature requests
- GitHub Discussions - Questions and ideas
- Contributing guidelines - How to help

### Updates
- `CHANGELOG.md` - Version history
- `ROADMAP.md` - Future plans

## FAQs

### Q: Is Quid legal?
**A:** Yes, when used responsibly with your own credentials to access content you're authorized to view. Always respect terms of service.

### Q: Do I need to be a programmer?
**A:** No! The CLI and MCP server are user-friendly. Plugin creation does require basic YAML editing.

### Q: Can I use Quid for commercial purposes?
**A:** The code is MIT licensed, but respect the terms of service of websites you access. Quid is designed for personal research, not bulk commercial extraction.

### Q: How is this different from web scraping?
**A:** Quid uses your own authenticated sessions to access content you have permission to view. It's like automating your browser, not bypassing restrictions.

### Q: Will this get me banned from websites?
**A:** Not if used responsibly! Quid respects rate limits, uses human-like delays, and only accesses what you're authorized to see.

### Q: Can I contribute plugins?
**A:** Absolutely! We welcome community plugins. See the contribution guidelines.

## Quick Command Reference

```bash
# Backend
python app.py                    # Start server
pkill -f "python.*app.py"       # Stop server

# CLI
./scrape list                    # List plugins
./scrape query <id> "search"    # Query plugin
./scrape check <id>             # Test auth
./scrape config <id>            # Show config

# Debug
HEADLESS=false ./scrape ...     # Watch browser
./scrape -v ...                 # Verbose output

# Plugins
cd plugins && cp -r template my_plugin  # Create plugin
./scrape check my_plugin        # Test plugin
```

## Architecture Overview

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   Claude    │   MCP   │   Quid MCP   │  Auth   │   Website    │
│  Desktop    │────────▶│   Backend    │────────▶│   Content    │
│             │         │              │         │              │
└─────────────┘         └──────────────┘         └──────────────┘
                              │
                              │ Plugins
                              ▼
                    ┌──────────────────┐
                    │  • EMIS          │
                    │  • Your Plugin   │
                    │  • Template      │
                    └──────────────────┘
```

## What's New in v2.0

**Major transformation!**

- 🔌 Plugin-based architecture
- 🔐 Multiple auth scenarios (API keys, OAuth, etc.)
- 📝 Plugin template for easy creation
- ⚖️ Ethical guidelines framework
- 📚 Comprehensive documentation
- ✅ 100% backwards compatible with v1.x

See [CHANGELOG.md](CHANGELOG.md) for details.

---

**Ready to start?** Jump to [Quick Start](#quick-start-5-minutes)

**Questions?** See [Support](#support)

**Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md)

---

*Happy querying! 🚀*
