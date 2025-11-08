# Developer Documentation

Documentation for contributors and developers extending the framework.

## Contents

- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - Complete refactoring overview
- **[../../CONTRIBUTING.md](../../CONTRIBUTING.md)** - Contribution guidelines
- **[../../SECURITY.md](../../SECURITY.md)** - Security policy

## Architecture Overview

The framework uses a modular design with pluggable strategies:

```
core/
  ├── scraper.py          # Main scraper (uses strategies)
  ├── session_manager.py  # Session persistence
  └── config_loader.py    # YAML config loading

auth/strategies/          # Authentication plugins
extractors/              # Data extraction plugins
credentials/             # Credential management
sites/                   # Site configurations (YAML)
```

## Extending the Framework

### Add Authentication Strategy

1. Create `auth/strategies/your_auth.py`
2. Inherit from `AuthStrategy`
3. Implement `login()` and `validate_session()`
4. Register in `core/scraper.py`

### Add Extraction Strategy

1. Create `extractors/your_extractor.py`
2. Inherit from `BaseExtractor`
3. Use `@register_extractor` decorator
4. Implement `can_extract()` and `extract()`

### Add Site Configuration

1. Create `sites/your_site.yaml`
2. Define auth and extraction strategies
3. Test with CLI
4. Submit PR

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings for public APIs
- Comment "why", not "what"

## Testing

```bash
# Syntax check
python -m py_compile backend/**/*.py

# Manual testing
./scrape list
./scrape query <site> "test"

# With visible browser
HEADLESS=false ./scrape query <site> "test"
```

## Release Process

1. Update `CHANGELOG.md`
2. Tag version: `git tag v1.x.x`
3. Push: `git push origin v1.x.x`
4. Create GitHub release with notes

## Questions?

Open a Discussion on GitHub or check existing Issues.
