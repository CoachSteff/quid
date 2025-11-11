# Manual Testing Checklist

**Date**: 2025-01-XX  
**Version**: 2.0.0-alpha  
**Phase**: Phase 2 Integration Testing

## Prerequisites

- [ ] Backend dependencies installed (`pip install -r backend/requirements.txt`)
- [ ] Playwright browsers installed (`playwright install chromium`)
- [ ] EMIS plugin exists in `plugins/emis/`
- [ ] Legacy site exists in `backend/sites/example.yaml` (if available)
- [ ] Credentials configured for EMIS (EMIS_EMAIL, EMIS_PASSWORD)

## Quick Smoke Test

### 1. Plugin CLI Commands

- [ ] `cd backend && python3 cli.py plugin list`
  - **Expected**: Lists all plugins with status
  - **Result**: ________________

- [ ] `python3 cli.py plugin info emis`
  - **Expected**: Shows detailed plugin information as JSON
  - **Result**: ________________

- [ ] `python3 cli.py plugin enable emis`
  - **Expected**: Plugin enabled successfully
  - **Result**: ________________

- [ ] `python3 cli.py plugin disable emis`
  - **Expected**: Plugin disabled successfully
  - **Result**: ________________

- [ ] `python3 cli.py plugin enable emis` (re-enable)
  - **Expected**: Plugin enabled again
  - **Result**: ________________

### 2. Updated CLI Commands

- [ ] `python3 cli.py list`
  - **Expected**: Shows plugins section and legacy sites section
  - **Result**: ________________

- [ ] `python3 cli.py config emis`
  - **Expected**: Shows "Plugin Configuration" header
  - **Result**: ________________

- [ ] `python3 cli.py check emis`
  - **Expected**: Shows "(plugin)" in header, uses auth.scenario
  - **Result**: ________________

- [ ] `python3 cli.py query emis "test"`
  - **Expected**: Query executes successfully using plugin config
  - **Result**: ________________

### 3. API Endpoints

**Note**: Start API server first: `cd backend && python3 app.py`

- [ ] `curl http://localhost:38153/plugins`
  - **Expected**: Returns PluginListResponse with plugins
  - **Result**: ________________

- [ ] `curl http://localhost:38153/plugins/emis`
  - **Expected**: Returns PluginInfo for EMIS
  - **Result**: ________________

- [ ] `curl -X POST http://localhost:38153/plugins/emis/enable`
  - **Expected**: Returns success message
  - **Result**: ________________

- [ ] `curl -X POST http://localhost:38153/plugins/emis/disable`
  - **Expected**: Returns success message
  - **Result**: ________________

- [ ] `curl -X POST http://localhost:38153/plugins/emis/enable` (re-enable)
  - **Expected**: Plugin enabled again
  - **Result**: ________________

- [ ] `curl http://localhost:38153/sites`
  - **Expected**: Returns legacy sites only
  - **Result**: ________________

- [ ] `curl -X POST http://localhost:38153/query/emis -H "Content-Type: application/json" -d '{"query":"test"}'`
  - **Expected**: Query executes using plugin config
  - **Result**: ________________

### 4. Backwards Compatibility

- [ ] Legacy site queries still work (if example site exists)
  - **Command**: `python3 cli.py query example "test"`
  - **Expected**: Works as before Phase 2
  - **Result**: ________________

- [ ] Existing API endpoints unchanged
  - **Endpoints**: `/query`, `/query/{site_id}`, `/sites`
  - **Expected**: All work as before
  - **Result**: ________________

### 5. Error Handling

- [ ] `python3 cli.py plugin info nonexistent`
  - **Expected**: Error message, exit code 1
  - **Result**: ________________

- [ ] `curl http://localhost:38153/plugins/nonexistent`
  - **Expected**: 404 Not Found
  - **Result**: ________________

## Test Results Summary

**Total Tests**: XX  
**Passed**: XX  
**Failed**: XX  
**Skipped**: XX

### Critical Issues Found
- None / List issues here

### High Priority Issues Found
- None / List issues here

### Notes
- Add any additional observations here

