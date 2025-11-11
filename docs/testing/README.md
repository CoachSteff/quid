# Testing Guide

Testing scenarios and best practices for the Generic Web Scraping Framework.

## Quick Test Workflow

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

**What to verify**:
- Browser opens and navigates to login page
- Credentials are entered correctly
- Login succeeds (URL changes or dashboard appears)
- Session is saved

### 3. Test Data Extraction

```bash
# Quick test query
./scrape query emis "test" --format table

# Verify data structure
./scrape query emis "test" --format raw | jq .
```

**What to verify**:
- Results are returned
- Data structure matches expectations
- All expected fields are present
- No errors in extraction

### 4. Test Session Reuse

```bash
# First query (will authenticate)
./scrape query emis "test1"

# Second query (should reuse session)
./scrape query emis "test2"
```

**What to verify**:
- First query takes ~28 seconds (authentication)
- Second query takes ~8 seconds (session reuse)
- No re-authentication occurs

## Testing Scenarios

### Test Site Configuration

**Validate YAML syntax**:
```bash
python3 -c "import yaml; yaml.safe_load(open('sites/emis.yaml'))"
```

**List sites**:
```bash
curl http://localhost:38153/sites
```

**Expected**: JSON response with all configured sites

### Test Query Endpoints

**Health check**:
```bash
curl http://localhost:38153/
```

**Expected**:
```json
{"status": "ok", "service": "Generic Web Scraping API", "version": "1.0.0"}
```

**Query default site**:
```bash
curl -X POST http://localhost:38153/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'
```

**Query specific site**:
```bash
curl -X POST http://localhost:38153/query/emis \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'
```

**Expected**: JSON response with results, citation, and summary

### Test Output Formats

**Summary format (default)**:
```bash
./scrape query emis "water treatment"
```
**Expected**: Summary + top 5 results

**JSON format**:
```bash
./scrape query emis "water treatment" --format json
```
**Expected**: Structured JSON with metadata

**Table format**:
```bash
./scrape query emis "water treatment" --format table
```
**Expected**: All results in table format

**Raw format**:
```bash
./scrape query emis "water treatment" --raw
```
**Expected**: Complete response with all data

### Test Error Handling

**Invalid site**:
```bash
curl -X POST http://localhost:38153/query/invalid_site \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```
**Expected**: 404 Not Found

**Missing credentials**:
```bash
# Unset credentials
unset EMIS_EMAIL EMIS_PASSWORD
./scrape query emis "test"
```
**Expected**: Error message about missing credentials

**Invalid query**:
```bash
curl -X POST http://localhost:38153/query/emis \
  -H "Content-Type: application/json" \
  -d '{}'
```
**Expected**: 400 Bad Request

## Debug Testing

### Verbose Mode

Enable detailed logging:
```bash
./scrape -v query emis "test"
```

**Shows**:
- Browser launch details
- Login process steps
- Search execution
- Data extraction progress
- All HTTP requests

### Visible Browser

Watch browser actions:
```bash
HEADLESS=false ./scrape query emis "test"
```

**Useful for**:
- Debugging authentication issues
- Verifying selectors
- Understanding page structure
- Identifying extraction problems

### Slow Motion

Slow down actions to observe:
```bash
PLAYWRIGHT_SLOW_MO=2000 ./scrape query emis "test"
```

**Useful for**:
- Understanding timing issues
- Debugging race conditions
- Learning how scraper works

### Keep Browser Open

Keep browser open after completion:
```bash
PLAYWRIGHT_KEEP_OPEN=true ./scrape query emis "test"
```

**Useful for**:
- Inspecting final page state
- Checking extracted elements
- Debugging extraction issues

## Integration Testing

### Test CLI Integration

```bash
# Test basic functionality
./scrape list
./scrape check emis
./scrape query emis "test" --format table

# Test error handling
./scrape query invalid_site "test"  # Should fail gracefully
```

### Test API Integration

```bash
# Start backend
python app.py

# Test endpoints
curl http://localhost:38153/
curl http://localhost:38153/sites
curl -X POST http://localhost:38153/query/emis \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

### Test MCP Server Integration

1. Start backend
2. Configure MCP server in Claude Desktop
3. Test with Claude: "Search EMIS for water treatment"
4. Verify Claude uses `query_emis` tool
5. Check results are returned correctly

## Performance Testing

### Measure Query Times

```bash
# First query (authentication)
time ./scrape query emis "test"

# Subsequent queries (session reuse)
time ./scrape query emis "test2"
```

**Expected**:
- First query: ~28 seconds
- Subsequent queries: ~8 seconds

### Test Concurrent Queries

```bash
# Run multiple queries in parallel
./scrape query emis "test1" &
./scrape query emis "test2" &
./scrape query emis "test3" &
wait
```

**Verify**:
- No race conditions
- Session file locking works
- All queries complete successfully

### Test Session Expiration

1. Make a query (creates session)
2. Wait for session to expire (check session file timestamp)
3. Make another query
4. Verify re-authentication occurs

## Testing New Sites

### Test Site Configuration

1. Create site YAML file
2. Validate syntax: `python3 -c "import yaml; yaml.safe_load(open('sites/newsite.yaml'))"`
3. Check credentials: `./scrape check newsite`
4. View configuration: `./scrape config newsite`

### Test Authentication

```bash
# Test with visible browser
HEADLESS=false ./scrape -v query newsite "test"
```

**Verify**:
- Login page loads
- Credentials are entered
- Login succeeds
- Success indicators match

### Test Data Extraction

```bash
# Test extraction strategies
./scrape query newsite "test" --format raw | jq '.raw_data'
```

**Verify**:
- Data is extracted correctly
- Structure matches expectations
- All expected fields present

## Best Practices

### Before Testing

1. ✅ Verify backend is running
2. ✅ Check credentials are set
3. ✅ Ensure virtual environment is activated
4. ✅ Verify site configuration is valid

### During Testing

1. ✅ Start with simple queries
2. ✅ Use verbose mode for debugging
3. ✅ Test with visible browser first
4. ✅ Verify each step before proceeding

### After Testing

1. ✅ Check logs for errors
2. ✅ Verify session files are created
3. ✅ Test session reuse
4. ✅ Clean up test data if needed

## Automated Testing

### Basic Test Script

```bash
#!/bin/bash
# test_basic.sh

set -e

echo "Testing basic functionality..."

# Test list
./scrape list || exit 1

# Test check
./scrape check emis || exit 1

# Test query
./scrape query emis "test" --format json || exit 1

echo "All tests passed!"
```

### API Test Script

```bash
#!/bin/bash
# test_api.sh

set -e

BACKEND_URL="http://localhost:38153"

echo "Testing API endpoints..."

# Health check
curl -f "$BACKEND_URL/" || exit 1

# List sites
curl -f "$BACKEND_URL/sites" || exit 1

# Query
curl -f -X POST "$BACKEND_URL/query/emis" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}' || exit 1

echo "All API tests passed!"
```

## Common Test Issues

### Tests Fail Intermittently

**Cause**: Race conditions or timing issues

**Solution**: Add delays or use file locking verification

### Tests Pass Locally But Fail in CI

**Cause**: Missing dependencies or environment differences

**Solution**: 
- Verify all dependencies in CI
- Check environment variables
- Ensure Playwright browsers are installed

### Tests Are Too Slow

**Cause**: Real browser automation is slow

**Solution**:
- Use headless mode (default)
- Reduce `PLAYWRIGHT_SLOW_MO`
- Test session reuse separately

## Test Data Management

### Using Test Credentials

**Development**:
- Use test accounts if available
- Don't use production credentials in tests
- Clean up test data after tests

### Session File Management

**Testing**:
- Clear session files between test runs if needed
- Verify session files are created correctly
- Test session expiration scenarios

## Additional Resources

- [CLI Usage Guide](docs/user/CLI_USAGE.md) - Detailed CLI examples
- [Troubleshooting Guide](docs/troubleshooting/README.md) - Common issues
- [Advanced Configuration](docs/advanced/GENERIC_FRAMEWORK.md) - Framework details

