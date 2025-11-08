# User Documentation

Welcome to the Generic Web Scraping Framework user documentation!

## Getting Started

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[../QUICK_REFERENCE.md](../../QUICK_REFERENCE.md)** - Cheat sheet for common commands

## Guides

- **[CLI_USAGE.md](CLI_USAGE.md)** - Complete CLI reference with examples
- **[GENERIC_FRAMEWORK.md](GENERIC_FRAMEWORK.md)** - Framework architecture and configuration

## Common Tasks

### Quick Test
```bash
cd backend
./scrape list
./scrape query emis "test"
```

### Add a New Site
1. Create `backend/sites/mysite.yaml`
2. Set credentials: `export MYSITE_EMAIL=... MYSITE_PASSWORD=...`
3. Test: `./scrape query mysite "test"`

See [GENERIC_FRAMEWORK.md](GENERIC_FRAMEWORK.md) for detailed instructions.

### Debug Issues
```bash
# Watch browser
HEADLESS=false ./scrape query emis "test"

# Verbose logging
./scrape -v query emis "test"

# Check credentials
./scrape check emis
```

## Need Help?

- Check the [QUICK_REFERENCE.md](../../QUICK_REFERENCE.md) for common commands
- See [../archived/](../archived/) for troubleshooting guides
- Open an issue on GitHub
