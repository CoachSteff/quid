# Quid MCP Quick Reference

**Version**: 2.0.0-alpha  
**Last Updated**: November 8, 2025

## What is Quid MCP?

**Quid** (Latin: "what?") is a modular platform for AI assistants to access content behind search engines, login walls, and paywalls. Think "Perplexity for protected documents."

## Quick Start

### 1. Installation

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Credentials

```bash
cp .env.example .env
# Edit .env and add:
# EMIS_EMAIL=your_email@example.com
# EMIS_PASSWORD=your_password
```

### 3. Start Backend

```bash
python app.py
# Server starts on http://localhost:38153
```

### 4. Test Query

```bash
./scrape query emis "water treatment"
```

## Plugin System

### Available Plugins

| Plugin | Category | Auth | Status |
|--------|----------|------|--------|
| `emis` | Environmental | Simple Form | ✅ Active |
| `template` | - | - | 📝 Template |

### Plugin Structure

```
plugins/my_plugin/
├── config.yaml   # Plugin configuration
└── README.md     # Documentation
```

## Authentication Scenarios

| Scenario | Description | Example |
|----------|-------------|---------|
| `simple_form` | Username/password | EMIS portal |
| `api_key` | API key auth | REST APIs |
| `none` | Public access | No auth required |
| `oauth2` | OAuth 2.0 | 🔜 Coming soon |
| `captcha` | With CAPTCHA | 🔜 Coming soon |
| `mfa` | Two-factor auth | 🔜 Coming soon |

## CLI Commands

### Basic Usage

```bash
# List available sites/plugins
./scrape list

# Query a plugin
./scrape query <plugin_id> "search term"

# Different output formats
./scrape query emis "search" --format json
./scrape query emis "search" --format table
./scrape query emis "search" --raw

# Check authentication
./scrape check <plugin_id>

# View configuration
./scrape config <plugin_id>

# Verbose output
./scrape -v query emis "search"
```

### Debug Mode

```bash
# Watch browser in action
HEADLESS=false ./scrape query emis "test"

# Slow motion
PLAYWRIGHT_SLOW_MO=2000 ./scrape query emis "test"
```

## REST API

### Health Check

```bash
curl http://localhost:38153/
```

### List Plugins

```bash
curl http://localhost:38153/sites
```

### Query Plugin

```bash
curl -X POST http://localhost:38153/query/emis \
  -H "Content-Type: application/json" \
  -d '{"query": "search term"}'
```

## MCP Server (Claude Desktop)

### Quick Setup

1. Start backend: `python app.py`
2. Run config generator:
   - macOS: `open macos/generate-mcp-config.command`
   - Windows: `windows\generate-mcp-config.bat`
3. Restart Claude Desktop

### Usage in Claude

```
"Query EMIS for water treatment information"
"What does EMIS say about environmental permits?"
```

## Creating a Plugin

### 1. Copy Template

```bash
cd plugins
cp -r template my_plugin
cd my_plugin
```

### 2. Edit config.yaml

```yaml
plugin:
  id: my_plugin
  name: My Website
  version: 1.0.0
  category: medical
  
auth:
  scenario: simple_form  # or api_key, none
  
extraction:
  strategies:
    - type: table
    - type: content
```

### 3. Set Credentials

```bash
export MY_PLUGIN_EMAIL=user@example.com
export MY_PLUGIN_PASSWORD=password
```

### 4. Test Plugin

```bash
./scrape check my_plugin
./scrape query my_plugin "test"
```

## Configuration

### Plugin Config (`config.yaml`)

```yaml
plugin:
  id: unique_id
  name: Display Name
  version: 1.0.0
  author: Your Name
  category: medical|legal|research|environmental|business|technical
  tags: [keywords]
  
rate_limit:
  requests_per_minute: 10
  concurrent_sessions: 1
  
auth:
  scenario: simple_form|api_key|oauth2|captcha|mfa|none
  
extraction:
  strategies:
    - type: table
    - type: content
    - type: documents
    - type: raw
```

### Environment Variables

```bash
# Per-plugin credentials
{PLUGIN_ID}_EMAIL=email@example.com
{PLUGIN_ID}_PASSWORD=password
{PLUGIN_ID}_API_KEY=api_key_here

# Backend settings
PORT=38153
HEADLESS=true
PLAYWRIGHT_SLOW_MO=500
```

## Extraction Strategies

| Type | Description | Use Case |
|------|-------------|----------|
| `table` | HTML tables | Tabular data |
| `content` | Structured HTML | Articles, pages |
| `documents` | PDFs, downloads | Document links |
| `raw` | Plain text | Fallback |

## Troubleshooting

### Backend Won't Start

```bash
# Check if port is in use
lsof -i :38153

# Kill existing process
pkill -f "python.*app.py"
```

### Authentication Fails

```bash
# Check credentials
./scrape check <plugin_id>

# Verify environment variables
echo $EMIS_EMAIL
echo $EMIS_PASSWORD

# Try verbose mode
./scrape -v query <plugin_id> "test"
```

### Browser Issues

```bash
# Reinstall Playwright
playwright install chromium

# Check browser availability
playwright install --dry-run
```

## Directory Structure

```
quid/
├── backend/
│   ├── core/              # Plugin system, auth registry
│   ├── auth/              # Auth strategies
│   ├── extractors/        # Content extractors
│   ├── sites/             # Legacy configs (deprecated)
│   ├── app.py            # REST API
│   └── cli.py            # CLI interface
├── plugins/
│   ├── emis/             # EMIS plugin
│   └── template/         # Plugin template
├── mcp-server/           # MCP server
├── docs/                 # Documentation
└── examples/             # Example scripts
```

## Useful Links

- **Documentation**: `docs/` directory
- **Plugin Template**: `plugins/template/`
- **Ethical Guidelines**: `docs/guides/ETHICAL_GUIDELINES.md`
- **Changelog**: `CHANGELOG.md`
- **Contributing**: `CONTRIBUTING.md`

## Common Use Cases

### Academic Research

```bash
# Query environmental portal
./scrape query emis "environmental impact assessment"
```

### Legal Research

```yaml
# Create legal database plugin
category: legal
auth:
  scenario: simple_form
```

### Medical Information

```yaml
# Create medical database plugin
category: medical
auth:
  scenario: api_key
```

## Best Practices

1. **Respect Rate Limits**: Use conservative `requests_per_minute`
2. **Test Thoroughly**: Test plugins before sharing
3. **Document Well**: Clear README helps others
4. **Follow Ethics**: Read ethical guidelines
5. **Use Appropriate Auth**: Choose right auth scenario

## Support

- **Issues**: GitHub Issues (when published)
- **Discussions**: GitHub Discussions (when published)
- **Documentation**: `docs/` directory
- **Security**: See `SECURITY.md`

## Version History

- **v2.0.0-alpha** (2025-11-08): Plugin system, new auth strategies
- **v1.1.0** (2025-11-08): Enhanced documentation
- **v1.0.0** (2024-11-06): Initial public release

---

**Need help?** Check the documentation in `docs/` or open an issue on GitHub.
