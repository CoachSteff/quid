# Plugin Template

This is a starter template for creating new Quid MCP plugins.

## Creating a New Plugin

### 1. Copy the Template

```bash
cd plugins
cp -r template my_new_plugin
cd my_new_plugin
```

### 2. Edit config.yaml

Update the plugin metadata:

```yaml
plugin:
  id: my_new_plugin
  name: My New Website
  version: 1.0.0
  author: Your Name
  description: What this plugin provides
  homepage: https://example.com
  category: medical  # Choose appropriate category
  tags: [relevant, keywords]
```

### 3. Configure Authentication

Choose an authentication scenario:

#### Simple Form Login

```yaml
auth:
  scenario: simple_form
  type: form_based
  login_url: https://example.com/login
  selectors:
    email_field: 'input[name="email"]'
    password_field: 'input[name="password"]'
    submit_button: 'button[type="submit"]'
```

#### API Key

```yaml
auth:
  scenario: api_key
  type: api_key
  method: header  # header|query_param|bearer
  key_name: X-API-Key
  key_location: header
```

#### No Authentication (Public)

```yaml
auth:
  scenario: none
  type: none
```

### 4. Configure Search

```yaml
search:
  url: https://example.com/search
  method: GET
  selectors:
    search_input: 'input[name="q"]'
    search_button: 'button[type="submit"]'
```

### 5. Configure Extraction

Choose which extraction strategies to use:

```yaml
extraction:
  strategies:
    - type: table       # For tabular data
    - type: content     # For article/page content
    - type: documents   # For PDFs/downloads
    - type: raw         # Fallback for any text
```

### 6. Set Up Credentials

Create environment variables for your credentials:

```bash
export MY_NEW_PLUGIN_EMAIL=user@example.com
export MY_NEW_PLUGIN_PASSWORD=password
```

The naming convention is: `{PLUGIN_ID}_EMAIL` and `{PLUGIN_ID}_PASSWORD`

### 7. Test Your Plugin

```bash
# Validate configuration
quid config validate my_new_plugin

# Test authentication
quid auth test my_new_plugin

# Try a query
quid query my_new_plugin "test search"
```

### 8. Create README.md

Document your plugin:

```markdown
# My New Plugin

Brief description of the website and what content it provides.

## Category

Choose emoji: 🏥 Medical | ⚖️ Legal | 🔬 Research | 🌍 Environmental | 💼 Business | 📚 Technical

## Authentication

Describe auth requirements and setup.

## Usage

Provide examples of how to use the plugin.

## Extracted Content

Describe what types of content can be extracted.

## Known Issues

List any known limitations or issues.
```

## Plugin Structure

```
my_new_plugin/
├── config.yaml       # Required: Plugin configuration
├── README.md         # Required: Plugin documentation
└── custom.py         # Optional: Custom logic (advanced)
```

## Testing Checklist

- [ ] config.yaml is valid YAML
- [ ] All required fields are filled
- [ ] Authentication works (`quid auth test`)
- [ ] Search returns results
- [ ] Extraction captures relevant data
- [ ] Rate limiting is respectful
- [ ] README is complete

## Validation

Quid validates plugins automatically:

```bash
quid config validate my_new_plugin
```

This checks:
- Required fields are present
- Authentication scenario is valid
- Extraction strategies are configured
- YAML syntax is correct

## Advanced: Custom Logic

For complex scenarios, create `custom.py`:

```python
# custom.py
async def pre_search_hook(page, query):
    """Called before executing search"""
    pass

async def post_extraction_hook(data):
    """Called after extracting data"""
    return data
```

## Authentication Scenarios

### Simple Form (`simple_form`)
Username/password login forms.

### API Key (`api_key`)
API key in header, query param, or bearer token.

### OAuth 2.0 (`oauth2`)
OAuth 2.0 authorization flow.

### CAPTCHA (`captcha`)
Form login with CAPTCHA (requires human intervention).

### MFA (`mfa`)
Multi-factor authentication (requires human intervention).

### None (`none`)
Public websites with no authentication.

## Extraction Strategies

### Table (`table`)
Extracts HTML tables with headers and rows.

### Content (`content`)
Extracts structured HTML content (articles, divs).

### Documents (`documents`)
Finds and extracts PDFs, downloads, detail pages.

### API JSON (`api_json`)
Parses JSON API responses.

### Raw (`raw`)
Fallback: extracts plain text from any selector.

## Best Practices

1. **Respect robots.txt**: Check if scraping is allowed
2. **Rate limiting**: Be conservative with requests_per_minute
3. **Test thoroughly**: Test on multiple queries before releasing
4. **Document well**: Clear README helps others use your plugin
5. **Ethical use**: Follow terms of service and ethical guidelines
6. **Error handling**: Provide helpful error messages

## Example Plugins

Look at existing plugins for examples:
- `emis/` - Complex Ionic Framework site with form auth
- More coming soon!

## Contributing

Once your plugin is working:

1. Test it thoroughly
2. Document it well
3. Submit a pull request to the main Quid repository
4. Share it with the community!

## Support

- [Plugin Development Guide](../../docs/developer/creating_plugins.md)
- [Authentication Strategies](../../docs/developer/authentication_strategies.md)
- [Extraction Patterns](../../docs/developer/extraction_patterns.md)
