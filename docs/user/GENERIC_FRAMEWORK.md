# Generic Web Scraping Framework

## Overview

This project has been refactored from an EMIS-specific scraper into a **generic, configurable web scraping framework** that can handle any login-protected website with minimal configuration.

## Key Features

✅ **Multi-Site Support** - Configure multiple sites via YAML files
✅ **Pluggable Authentication** - Support for form-based, OAuth, API tokens, etc.
✅ **Flexible Data Extraction** - Table extraction, content extraction, custom strategies
✅ **Session Management** - Persistent sessions with file locking for concurrency
✅ **Proper Error Handling** - HTTP status codes, detailed error messages
✅ **Resource Cleanup** - Context managers ensure browser cleanup
✅ **Backwards Compatible** - Existing EMIS API endpoints still work

## Architecture

```
backend/
├── core/                    # Core framework components
│   ├── scraper.py          # Generic scraper with strategy pattern
│   ├── session_manager.py  # Session persistence with file locking
│   └── config_loader.py    # YAML configuration loader
├── auth/                    # Authentication strategies
│   ├── base.py            # Auth interface
│   └── strategies/
│       └── form_based.py  # Form-based login
├── extractors/             # Data extraction strategies
│   ├── base.py            # Extractor interface
│   ├── registry.py        # Auto-discovery
│   ├── table.py           # Table extraction
│   └── content.py         # Content extraction
├── credentials/            # Credential management
│   └── manager.py         # Per-site credentials
├── sites/                  # Site configurations
│   ├── emis.yaml          # EMIS configuration
│   └── example.yaml       # Template
└── api/                    # API layer
    └── models.py          # Request/response models
```

## Adding a New Site

### Step 1: Create Site Configuration

Create a YAML file in `backend/sites/your_site.yaml`:

```yaml
site_id: your_site
name: Your Website
description: Description of the site
base_url: https://example.com

# Authentication (optional for public sites)
auth:
  type: form_based  # or 'none'
  login_url: https://example.com/login
  selectors:
    email_field: 'input[name="email"]'
    password_field: 'input[name="password"]'
    submit_button: 'button[type="submit"]'
  success_indicators:
    - type: url_change
      pattern: "!login"
  failure_indicators:
    - type: element_present
      selector: '.error-message'

# Search configuration
search:
  url: https://example.com/search
  selectors:
    search_input: 'input[name="q"]'
    search_button: 'button[type="submit"]'

# Data extraction
extraction:
  strategies:
    - type: table
      selector: 'table.results'
      extract_headers: true
    - type: content
      selector: 'main'
      max_length: 5000
```

### Step 2: Set Credentials

Set environment variables:
```bash
export YOUR_SITE_EMAIL=user@example.com
export YOUR_SITE_PASSWORD=your_password
```

Or use fallback credentials in code (for development):
```python
# In app.py startup_event()
cred_manager.register_fallback('your_site', {
    'email': 'dev@example.com',
    'password': 'devpass123'
})
```

### Step 3: Query the Site

```bash
curl -X POST http://localhost:38153/query/your_site \
  -H "Content-Type: application/json" \
  -d '{"query": "search term"}'
```

## API Endpoints

### GET /
Health check endpoint
```bash
curl http://localhost:38153/
```

### GET /sites
List all available sites
```bash
curl http://localhost:38153/sites
```

### POST /query
Query default site (EMIS) - backwards compatible
```bash
curl -X POST http://localhost:38153/query \
  -H "Content-Type: application/json" \
  -d '{"query": "BBT water treatment"}'
```

### POST /query/{site_id}
Query specific site
```bash
curl -X POST http://localhost:38153/query/your_site \
  -H "Content-Type: application/json" \
  -d '{"query": "search term"}'
```

## Configuration Reference

### Authentication Types

#### form_based
Traditional username/password forms
```yaml
auth:
  type: form_based
  login_url: https://example.com/login
  selectors:
    email_field: 'input[name="email"]'
    password_field: 'input[name="password"]'
    submit_button: 'button[type="submit"]'
```

#### none
Public sites without authentication
```yaml
auth:
  type: none
```

### Extraction Strategies

#### table
Extract data from HTML tables
```yaml
- type: table
  selector: 'table.results'  # Optional specific table
  extract_headers: true
  max_rows: 100
```

#### content
Extract structured or unstructured content
```yaml
- type: content
  selector: 'main.content'
  fields:                    # Optional structured extraction
    title: 'h1'
    items: '.item'
  max_length: 5000
```

### Success/Failure Indicators

#### url_change
Check if URL changed after login
```yaml
success_indicators:
  - type: url_change
    pattern: "!login"  # '!' means NOT containing
```

#### element_present
Check if element exists
```yaml
success_indicators:
  - type: element_present
    selector: '.user-dashboard'
```

#### element_absent
Check if element is NOT present
```yaml
failure_indicators:
  - type: element_absent
    selector: '.login-form'
```

## Credential Management

Credentials are resolved in this order:

1. **Per-site environment variables** (recommended)
   ```bash
   export YOUR_SITE_EMAIL=user@example.com
   export YOUR_SITE_PASSWORD=password
   ```

2. **Generic environment variables** (backwards compat)
   ```bash
   export EMIS_EMAIL=user@example.com
   export EMIS_PASSWORD=password
   ```

3. **Hardcoded fallbacks** (development only)
   ```python
   cred_manager.register_fallback('site', {...})
   ```

## Error Handling

The framework uses proper HTTP status codes:

- **200 OK** - Successful query
- **400 Bad Request** - Invalid query or configuration
- **401 Unauthorized** - Authentication failed
- **404 Not Found** - Site not configured
- **500 Internal Server Error** - Scraping error
- **504 Gateway Timeout** - Query took too long

## Improvements Over Original

### Fixed Issues
✅ Session file race conditions (added file locking)
✅ Resource leaks (context managers)
✅ Error handling (proper HTTP codes)
✅ Hardcoded selectors (YAML configuration)
✅ Single-site limitation (multi-site support)

### New Features
✅ Pluggable authentication strategies
✅ Pluggable extraction strategies
✅ Site discovery (GET /sites)
✅ Per-site credentials
✅ Configuration validation
✅ Better logging and tracing

## Migration from Original

The refactored API is **100% backwards compatible**:

- `/query` endpoint still works for EMIS
- Environment variables work the same way
- Fallback credentials still available
- Existing skill scripts need no changes

## Extending the Framework

### Add New Auth Strategy

1. Create `auth/strategies/your_strategy.py`:
```python
from auth.base import AuthStrategy

class YourAuth(AuthStrategy):
    async def login(self, page, context):
        # Implement login
        pass
    
    async def validate_session(self, page):
        # Implement validation
        pass
```

2. Register in `core/scraper.py`:
```python
elif auth_type == 'your_type':
    self._auth_strategy = YourAuth(auth_config, credentials)
```

### Add New Extractor

1. Create `extractors/your_extractor.py`:
```python
from extractors.base import BaseExtractor
from extractors.registry import register_extractor

@register_extractor
class YourExtractor(BaseExtractor):
    def get_name(self):
        return "your_type"
    
    async def can_extract(self, page):
        # Check if can handle page
        pass
    
    async def extract(self, page):
        # Extract data
        pass
```

2. Import in `extractors/__init__.py` to auto-register

## Testing

### Test Site Configuration
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('sites/emis.yaml'))"

# List sites
curl http://localhost:38153/sites
```

### Test Query
```bash
# Start server
cd backend
python app.py

# Query in another terminal
curl -X POST http://localhost:38153/query/emis \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'
```

## Environment Variables

### Global
- `HEADLESS` - Browser visibility (true/false)
- `PLAYWRIGHT_SLOW_MO` - Delay between actions (ms)
- `PLAYWRIGHT_KEEP_OPEN` - Keep browser open (true/false)
- `SESSION_DIR` - Session file directory
- `SITES_CONFIG_DIR` - Site config directory
- `CORS_ORIGINS` - Allowed CORS origins

### Per-Site
- `{SITE_ID}_EMAIL` - Email/username
- `{SITE_ID}_PASSWORD` - Password
- `{SITE_ID}_API_KEY` - API key (if applicable)

## Security Considerations

⚠️ **Production Deployment:**
- Use secrets manager (AWS Secrets, Vault, etc.) instead of env vars
- Restrict CORS origins
- Add API key authentication
- Use HTTPS
- Rate limiting
- Monitor for abuse

## Future Enhancements

Potential additions:
- OAuth authentication strategy
- API token authentication
- Cookie-based authentication
- Pagination support
- Incremental scraping
- Result caching
- Browser pooling for performance
- Async task queue
- Webhook callbacks
- Monitoring/metrics

## Support

For issues or questions:
1. Check site configuration YAML syntax
2. Verify credentials are set correctly
3. Check backend logs for detailed errors
4. Review `sites/example.yaml` for reference
5. Test with `HEADLESS=false` to see browser
