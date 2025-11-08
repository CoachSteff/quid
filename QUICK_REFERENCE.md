# Quick Reference Card

## Setup (One-time)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

cp .env.example .env
# Edit .env with your credentials
```

## CLI Commands

```bash
# Discovery
./scrape list                    # List all sites
./scrape config <site>           # Show site config
./scrape check <site>            # Check credentials

# Query
./scrape query <site> "<query>"  # Basic query
./scrape query <site> "<query>" --format json    # JSON output
./scrape query <site> "<query>" --format table   # Table format
./scrape query <site> "<query>" --raw           # Raw data
./scrape -v query <site> "<query>"              # Verbose

# Debug
HEADLESS=false ./scrape query <site> "<query>"          # Watch browser
PLAYWRIGHT_SLOW_MO=2000 ./scrape query <site> "<query>" # Slow motion
```

## API Endpoints

```bash
# Start server
python app.py                    # Port 38153

# Endpoints
GET  /                          # Health check
GET  /sites                     # List sites
POST /query                     # Query default (EMIS)
POST /query/{site_id}          # Query specific site

# Examples
curl http://localhost:38153/sites

curl -X POST http://localhost:38153/query/emis \
  -H "Content-Type: application/json" \
  -d '{"query": "search term"}'
```

## Add New Site

1. **Create** `sites/mysite.yaml`:
```yaml
site_id: mysite
name: My Site
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
    - type: content
      selector: 'main'
```

2. **Set credentials**:
```bash
export MYSITE_EMAIL=user@example.com
export MYSITE_PASSWORD=password
```

3. **Test**:
```bash
./scrape check mysite
./scrape query mysite "test"
```

## Environment Variables

### Global
```bash
HEADLESS=false              # Show browser
PLAYWRIGHT_SLOW_MO=500      # Delay between actions (ms)
PLAYWRIGHT_KEEP_OPEN=true   # Keep browser open
SESSION_DIR=data/sessions   # Session storage
SITES_CONFIG_DIR=sites      # Config directory
```

### Per-Site Credentials
```bash
{SITE_ID}_EMAIL=email
{SITE_ID}_PASSWORD=password
{SITE_ID}_API_KEY=key
```

## Common Issues

### CLI not found
```bash
chmod +x backend/scrape
# OR
python3 backend/cli.py list
```

### Import errors
```bash
source venv/bin/activate
```

### Browser issues
```bash
playwright install chromium
```

### Auth failures
```bash
./scrape check emis
export EMIS_EMAIL=your@email.com
export EMIS_PASSWORD=yourpass
```

### Debug login
```bash
HEADLESS=false PLAYWRIGHT_SLOW_MO=1000 ./scrape -v query emis "test"
```

## File Locations

```
backend/
├── sites/          # Site configs (YAML)
├── data/
│   └── sessions/  # Session files
├── cli.py         # CLI script
├── scrape         # CLI wrapper
└── app.py         # API server
```

## Output Formats

### Summary (default)
Shows summary + top 5 results

### JSON
```bash
--format json
```
Returns structured metadata

### Table
```bash
--format table
```
Shows all results with labels

### Raw
```bash
--format raw
# OR
--raw
```
Complete response with all data

## Piping Examples

```bash
# Extract field with jq
./scrape query emis "water" --raw | jq '.citation.source_url'

# Count results
./scrape query emis "water" --format json | jq '.results_count'

# Save to file
./scrape query emis "water" --raw > results.json

# Process in loop
for topic in "water" "waste" "air"; do
  ./scrape query emis "$topic" >> all_results.txt
done
```

## Quick Test

```bash
# Verify everything works
./scrape list
./scrape check emis
./scrape query emis "test" --format table

# With visible browser
HEADLESS=false ./scrape query emis "test"
```

## Documentation

- **README.md** - Project overview
- **GENERIC_FRAMEWORK.md** - Complete framework docs
- **CLI_USAGE.md** - CLI guide with examples
- **QUICKSTART.md** - Setup guide
- **REFACTORING_SUMMARY.md** - What changed

## Help

```bash
./scrape --help
./scrape query --help
```

## Support

1. Check credentials: `./scrape check <site>`
2. Verify config: `./scrape config <site>`
3. Verbose mode: `./scrape -v query ...`
4. Watch browser: `HEADLESS=false ./scrape query ...`
5. Check logs in verbose mode
