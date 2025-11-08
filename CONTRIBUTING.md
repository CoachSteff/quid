# Contributing to Generic Web Scraping Framework

Thank you for your interest in contributing! 🎉

## How to Contribute

### Adding a New Site Configuration

The easiest way to contribute is by adding configurations for new sites:

1. **Create a YAML configuration** in `backend/sites/your_site.yaml`
2. **Test thoroughly** with the CLI
3. **Document any quirks** or special requirements
4. **Submit a pull request**

Example:
```yaml
site_id: example
name: Example Website
base_url: https://example.com
auth:
  type: form_based
  selectors:
    email_field: 'input[name="email"]'
    password_field: 'input[name="password"]'
    submit_button: 'button[type="submit"]'
extraction:
  strategies:
    - type: table
```

### Adding New Features

1. **Open an issue** first to discuss the feature
2. **Fork the repository**
3. **Create a feature branch**: `git checkout -b feature/your-feature-name`
4. **Make your changes** with tests
5. **Update documentation**
6. **Submit a pull request**

### Bug Reports

Found a bug? Please open an issue with:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)
- Relevant logs (with credentials removed!)

## Development Setup

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd generic-web-scraper/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Set up credentials
cp .env.example .env
# Edit .env with test credentials

# Test your changes
./scrape list
./scrape query emis "test"
```

## Code Style

- **Python**: Follow PEP 8
- **Type hints**: Use them where it improves clarity
- **Docstrings**: Required for public functions
- **Comments**: Explain "why", not "what"

## Testing

Before submitting:
- [ ] Code passes syntax check: `python -m py_compile <files>`
- [ ] CLI works: `./scrape query <site> "test"`
- [ ] API works if modified: Test with curl
- [ ] Documentation updated
- [ ] No hardcoded credentials

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update docs/ if you changed functionality
3. Follow the PR template
4. Wait for review - be patient and responsive to feedback

## Adding Authentication Strategies

To add support for new auth types (OAuth, SAML, etc.):

1. Create `backend/auth/strategies/your_strategy.py`
2. Inherit from `AuthStrategy` base class
3. Implement `login()` and `validate_session()` methods
4. Register in `backend/core/scraper.py`
5. Add example YAML config
6. Document usage

## Adding Extraction Strategies

To add new data extraction patterns:

1. Create `backend/extractors/your_extractor.py`
2. Inherit from `BaseExtractor`
3. Use `@register_extractor` decorator
4. Implement `can_extract()` and `extract()` methods
5. Add example usage
6. Update documentation

## Community Guidelines

- Be respectful and constructive
- Help others in issues and discussions
- Share your site configurations
- Report security issues privately (see SECURITY.md)

## Questions?

- Open a Discussion for questions
- Check existing Issues and PRs
- Read the documentation in `docs/`

Thank you for making this project better! 🚀
