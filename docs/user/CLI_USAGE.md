# CLI Usage Guide

The scraping framework includes a powerful command-line interface for testing, debugging, and scripting.

## Quick Start

```bash
# From the backend directory
cd backend

# List available sites
./scrape list

# Query a site
./scrape query emis "BBT water treatment"
```

## Installation

The CLI uses the same dependencies as the backend:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## Commands

### 1. List Sites

List all configured sites:

```bash
./scrape list
```

**Output:**
```
Available Sites (2):
------------------------------------------------------------

  emis
    Name: VITO EMIS Portal
    URL:  https://emis.vito.be
    Info: Energie- en milieu-informatiesysteem

  example
    Name: Example Website
    URL:  https://example.com
```

### 2. Show Configuration

Display full configuration for a site:

```bash
./scrape config emis
```

**Output:**
```json
{
  "site_id": "emis",
  "name": "VITO EMIS Portal",
  "base_url": "https://emis.vito.be",
  "auth": {
    "type": "form_based",
    "login_url": "https://navigator.emis.vito.be",
    ...
  },
  "extraction": {
    "strategies": [...]
  }
}
```

**Use Cases:**
- Verify site configuration is valid
- Debug selector issues
- Document site setup

### 3. Check Credentials

Verify credentials are configured:

```bash
./scrape check emis
```

**Output:**
```
Credential Check for 'emis':
------------------------------------------------------------
Auth Type: form_based
Status: ✅ Credentials found

Available fields:
  email: tim***@gmail.com
  password: ******
```

**Missing Credentials:**
```
Status: ❌ No credentials found

Set credentials with environment variables:
  export EMIS_EMAIL=your_email
  export EMIS_PASSWORD=your_password
```

### 4. Query Site

Execute a search query:

```bash
./scrape query <site_id> "<query>" [options]
```

**Basic Query:**
```bash
./scrape query emis "BBT water treatment"
```

**Output Formats:**

#### Summary Format (default)
```bash
./scrape query emis "water treatment"
```
Shows summary, result count, and top 5 results.

#### JSON Format
```bash
./scrape query emis "water treatment" --format json
```
Returns structured JSON with metadata.

#### Table Format
```bash
./scrape query emis "water treatment" --format table
```
Shows all results in table format.

#### Raw Format
```bash
./scrape query emis "water treatment" --format raw
# or
./scrape query emis "water treatment" --raw
```
Complete raw response with all data.

## Advanced Usage

### Verbose Mode

Enable detailed logging for debugging:

```bash
./scrape -v query emis "search term"
```

Shows:
- Browser launch details
- Login process steps
- Search execution
- Data extraction progress
- All HTTP requests

### Environment Variables

Control scraper behavior:

```bash
# Show browser window (for debugging)
HEADLESS=false ./scrape query emis "test"

# Slow down actions to observe
PLAYWRIGHT_SLOW_MO=2000 ./scrape query emis "test"

# Keep browser open after completion
PLAYWRIGHT_KEEP_OPEN=true ./scrape query emis "test"
```

### Piping and Scripting

Extract specific data:

```bash
# Get just the raw data
./scrape query emis "water" --format raw | jq '.raw_data'

# Count results
./scrape query emis "water" --format json | jq '.results_count'

# Extract source URL
./scrape query emis "water" --format raw | jq '.citation.source_url'
```

**Example Script:**
```bash
#!/bin/bash
# Query multiple topics and save results

TOPICS=("water treatment" "waste management" "air quality")

for topic in "${TOPICS[@]}"; do
    echo "Querying: $topic"
    ./scrape query emis "$topic" --format raw > "results_${topic// /_}.json"
    sleep 5  # Rate limiting
done
```

### Batch Queries

```bash
# Read queries from file
while IFS= read -r query; do
    echo "Processing: $query"
    ./scrape query emis "$query" >> results.txt
done < queries.txt
```

## Testing Workflow

### 1. Verify Setup
```bash
# Check site is configured
./scrape list

# Verify credentials
./scrape check emis

# Check configuration
./scrape config emis
```

### 2. Test Authentication
```bash
# Run with browser visible to watch login
HEADLESS=false ./scrape -v query emis "test"
```

### 3. Test Data Extraction
```bash
# Quick test query
./scrape query emis "test" --format table

# Verify data structure
./scrape query emis "test" --format raw | jq .
```

### 4. Debug Issues
```bash
# Full verbose logging with visible browser
HEADLESS=false PLAYWRIGHT_SLOW_MO=1000 ./scrape -v query emis "test"

# Check what selectors match
./scrape config emis | jq '.extraction.strategies'
```

## Troubleshooting

### "Site ID mismatch" Error

**Problem:** Configuration file site_id doesn't match filename

```bash
# Error message:
ERROR: Failed to load config for site 'example': Site ID mismatch
```

**Cause:** The `site_id` in the YAML file must match the filename (without .yaml)

**Solution:**
```bash
# If file is example.yaml, ensure:
site_id: example  # NOT example_site

# Or rename file to match site_id:
mv example.yaml example_site.yaml  # If site_id is example_site
```

**Rule:** `sites/[FILENAME].yaml` must have `site_id: [FILENAME]`

### Command Not Found

```bash
# Make sure script is executable
chmod +x backend/scrape

# Or call Python directly
python3 backend/cli.py list
```

### Import Errors

**Problem:** `ModuleNotFoundError` or import failures

**Solution 1:** Use the wrapper script (recommended)
```bash
cd backend
./scrape list  # This handles Python path correctly
```

**Solution 2:** Activate virtual environment
```bash
cd backend
source venv/bin/activate
python3 cli.py list
```

**Solution 3:** Check dependencies are installed
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
```

### Authentication Failures

```bash
# Check credentials are set
./scrape check emis

# Set credentials
export EMIS_EMAIL=your_email@example.com
export EMIS_PASSWORD=your_password

# Test again
./scrape query emis "test"
```

### Playwright-Stealth Compatibility Issues

**Problem:** Import errors related to `playwright-stealth`

**Symptoms:**
```
ImportError: cannot import name 'stealth_async'
AttributeError: module 'playwright_stealth' has no attribute 'stealth_async'
```

**Cause:** Version incompatibility between v1.0.6 and v2.0+

**Solution:** The code includes automatic fallback handling. If you still see errors:

```bash
# Ensure correct version is installed
pip install playwright-stealth==1.0.6

# Or if you prefer v2.0+, the code supports both
pip install playwright-stealth>=2.0.0

# Verify installation
python3 -c "import playwright_stealth; print(playwright_stealth.__version__)"
```

**Note:** Code in `core/scraper.py` automatically detects and handles both v1.x and v2.x APIs

### Browser Issues

```bash
# Reinstall Playwright browsers
playwright install chromium

# Test with visible browser
HEADLESS=false ./scrape query emis "test"
```

### Timeout Errors

```bash
# Site might be slow - check with visible browser
HEADLESS=false ./scrape query emis "test"

# Check network connectivity
ping emis.vito.be
```

### "Site config not found" Error

**Problem:** Site configuration file doesn't exist

```bash
# List available sites
./scrape list

# Use exact site_id from the list
./scrape query emis "test"  # NOT EMIS or emis.yaml
```

### Selector Not Found Errors

**Problem:** Page elements can't be located

**Debug Steps:**
```bash
# 1. View current selectors
./scrape config emis | jq '.extraction.strategies'

# 2. Watch browser with slow motion
HEADLESS=false PLAYWRIGHT_SLOW_MO=2000 ./scrape -v query emis "test"

# 3. Check if site structure changed
# Update selectors in sites/emis.yaml if needed
```

## Examples

### Example 1: Quick Test
```bash
# Test that everything works
./scrape list
./scrape check emis
./scrape query emis "test" --format table
```

### Example 2: Extract to CSV
```bash
# Get data and convert to CSV with jq
./scrape query emis "water" --format raw | \
  jq -r '.raw_data[] | [.column1, .column2] | @csv' > results.csv
```

### Example 3: Monitor for Changes
```bash
# Script to check for new content
#!/bin/bash
QUERY="recent updates"
CURRENT=$(./scrape query emis "$QUERY" --format raw | jq -r '.raw_data | length')
PREVIOUS=$(cat count.txt)

if [ "$CURRENT" -gt "$PREVIOUS" ]; then
    echo "New results found!"
    ./scrape query emis "$QUERY" --format raw > latest.json
fi

echo $CURRENT > count.txt
```

### Example 4: Compare Sites
```bash
# Query multiple sites with same term
for site in emis other_site; do
    echo "=== $site ==="
    ./scrape query $site "search term" --format json
    echo
done
```

## Integration with Other Tools

### With jq (JSON processing)
```bash
# Extract specific fields
./scrape query emis "water" --raw | jq '.raw_data[0]'

# Filter results
./scrape query emis "water" --raw | jq '.raw_data[] | select(.title | contains("treatment"))'
```

### With curl (API comparison)
```bash
# Compare CLI vs API results
./scrape query emis "test" --raw > cli_result.json
curl -X POST http://localhost:38153/query/emis \
  -d '{"query":"test"}' -H 'Content-Type: application/json' > api_result.json
diff cli_result.json api_result.json
```

### With watch (Live monitoring)
```bash
# Auto-refresh query results
watch -n 60 './scrape query emis "latest" --format table'
```

## Best Practices

1. **Always test with `--format table` first** - Quick visual inspection
2. **Use `-v` when debugging** - See what's happening
3. **Set `HEADLESS=false` for first-time setup** - Watch authentication
4. **Check credentials before querying** - Use `./scrape check`
5. **Add rate limiting in scripts** - `sleep` between queries
6. **Validate configuration** - Use `./scrape config` before production
7. **Save raw data** - Easier to reprocess later
8. **Use environment files** - Manage credentials safely

## Security Notes

⚠️ **Credentials:**
- Never commit credentials to version control
- Use environment variables or secure vaults
- Don't log passwords in scripts

⚠️ **Rate Limiting:**
- Add delays between queries to avoid bans
- Respect robots.txt and terms of service
- Monitor for rate limit responses

⚠️ **Data Privacy:**
- Be careful with scraped data storage
- Follow GDPR and data protection laws
- Don't expose sensitive data in logs

## Performance Tips

- **Headless mode** - Faster (default)
- **Reduce slow_mo** - Set `PLAYWRIGHT_SLOW_MO=0`
- **Session reuse** - Automatic, no action needed
- **Parallel queries** - Use background jobs (`&`)

```bash
# Parallel execution (be careful with rate limits!)
./scrape query emis "topic1" &
./scrape query emis "topic2" &
wait
```

## Help

Get help anytime:
```bash
./scrape --help
./scrape query --help
```

For issues, check:
1. `./scrape -v query ...` - Verbose logging
2. Configuration: `./scrape config <site>`
3. Credentials: `./scrape check <site>`
4. Backend logs if API is running
