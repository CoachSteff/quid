# Quid MCP Test Scenarios

**Version**: 2.0.0-alpha  
**Last Updated**: November 8, 2025  
**Status**: Test suite specification

## Overview

Comprehensive test scenarios for Quid MCP covering the new plugin system, authentication strategies, backwards compatibility, and end-to-end workflows.

## Test Suite Structure

```
tests/
├── unit/                      # Unit tests for core components
│   ├── test_plugin_manager.py
│   ├── test_auth_registry.py
│   ├── test_api_key_auth.py
│   ├── test_none_auth.py
│   └── test_config_validation.py
├── integration/               # Integration tests
│   ├── test_emis_plugin.py
│   ├── test_template_plugin.py
│   ├── test_plugin_creation.py
│   └── test_multi_plugin.py
├── e2e/                      # End-to-end scenarios
│   ├── test_fresh_install.py
│   ├── test_mcp_integration.py
│   └── test_workflows.py
├── fixtures/                 # Test data and mocks
│   ├── mock_plugin/
│   ├── credentials.py
│   └── mock_responses.py
└── conftest.py              # Pytest configuration
```

---

## 1. Unit Tests

### 1.1 Plugin Manager Tests

**File**: `tests/unit/test_plugin_manager.py`

#### Test Cases

**TC-PM-001: Discover Plugins**
- **Description**: Test plugin discovery in directory
- **Setup**: Ensure plugins/ directory exists with EMIS and template
- **Action**: Call `discover_plugins()`
- **Expected**: Returns list with 'emis' and 'template'
- **Priority**: P0 (Critical)

**TC-PM-002: Load Valid Plugin**
- **Description**: Load EMIS plugin successfully
- **Setup**: EMIS plugin config exists
- **Action**: Call `load_plugin('emis')`
- **Expected**: Returns Plugin object with all fields populated
- **Assertions**:
  - plugin.id == 'emis'
  - plugin.name == 'VITO EMIS Portal'
  - plugin.version == '1.0.0'
  - plugin.category == 'environmental'
- **Priority**: P0 (Critical)

**TC-PM-003: Load Non-Existent Plugin**
- **Description**: Attempt to load missing plugin
- **Action**: Call `load_plugin('nonexistent')`
- **Expected**: Raises `FileNotFoundError`
- **Priority**: P1 (High)

**TC-PM-004: Validate Plugin Config**
- **Description**: Test config validation with valid EMIS config
- **Setup**: Valid plugin config dictionary
- **Action**: Call `validate_plugin_config()`
- **Expected**: Returns True, no exceptions
- **Priority**: P0 (Critical)

**TC-PM-005: Reject Invalid Config - Missing Fields**
- **Description**: Test validation rejects config missing required fields
- **Setup**: Config missing 'name' field
- **Action**: Call `validate_plugin_config()`
- **Expected**: Raises `PluginValidationError` with field name
- **Priority**: P1 (High)

**TC-PM-006: Reject Invalid Config - Bad Auth Scenario**
- **Description**: Test validation rejects invalid auth scenario
- **Setup**: Config with auth.scenario = 'invalid_scenario'
- **Action**: Call `validate_plugin_config()`
- **Expected**: Raises `PluginValidationError` listing valid scenarios
- **Priority**: P1 (High)

**TC-PM-007: Enable/Disable Plugin**
- **Description**: Test plugin enable/disable functionality
- **Setup**: Load EMIS plugin
- **Actions**:
  1. Call `disable_plugin('emis')`
  2. Check `get_enabled_plugins()`
  3. Call `enable_plugin('emis')`
  4. Check `get_enabled_plugins()` again
- **Expected**: Plugin status changes correctly
- **Priority**: P2 (Medium)

**TC-PM-008: Get Plugin Info**
- **Description**: Test plugin info extraction
- **Setup**: Load EMIS plugin
- **Action**: Call `get_plugin_info('emis')`
- **Expected**: Returns dictionary with all metadata
- **Assertions**:
  - Contains id, name, version, author, category
  - Contains auth_scenario
  - Contains human_intervention flags
- **Priority**: P1 (High)

**TC-PM-009: Handle Missing Plugins Directory**
- **Description**: Test graceful handling of missing directory
- **Setup**: Point to non-existent directory
- **Action**: Call `discover_plugins()`
- **Expected**: Returns empty list, logs warning, no exception
- **Priority**: P2 (Medium)

**TC-PM-010: Load All Plugins**
- **Description**: Test bulk loading of all plugins
- **Setup**: Multiple plugins exist
- **Action**: Call `load_all_plugins()`
- **Expected**: Returns dictionary of all valid plugins
- **Priority**: P1 (High)

### 1.2 Auth Registry Tests

**File**: `tests/unit/test_auth_registry.py`

#### Test Cases

**TC-AR-001: Register Strategy**
- **Description**: Test registering a new auth strategy
- **Setup**: Mock strategy class
- **Action**: Call `AuthRegistry.register('test_scenario', MockStrategy)`
- **Expected**: Strategy registered successfully
- **Priority**: P1 (High)

**TC-AR-002: Get Registered Strategy**
- **Description**: Test retrieving registered strategy
- **Setup**: Register test strategy
- **Action**: Call `AuthRegistry.get('test_scenario')`
- **Expected**: Returns correct strategy class
- **Priority**: P1 (High)

**TC-AR-003: Get Non-Existent Strategy**
- **Description**: Test getting unregistered strategy
- **Action**: Call `AuthRegistry.get('nonexistent')`
- **Expected**: Returns None, logs warning
- **Priority**: P1 (High)

**TC-AR-004: List All Scenarios**
- **Description**: Test listing all registered scenarios
- **Action**: Call `AuthRegistry.list_scenarios()`
- **Expected**: Returns list including 'simple_form', 'api_key', 'none'
- **Priority**: P2 (Medium)

**TC-AR-005: Built-in Strategies Registered**
- **Description**: Verify all built-in strategies are auto-registered
- **Action**: Check registry after module import
- **Expected**: 
  - 'simple_form' registered
  - 'form_based' registered (legacy)
  - 'api_key' registered
  - 'none' registered
- **Priority**: P0 (Critical)

**TC-AR-006: Overwrite Warning**
- **Description**: Test that overwriting strategy logs warning
- **Setup**: Register 'test' strategy
- **Action**: Register 'test' again with different class
- **Expected**: Logs warning, overwrites successfully
- **Priority**: P2 (Medium)

### 1.3 API Key Auth Tests

**File**: `tests/unit/test_api_key_auth.py`

#### Test Cases

**TC-AK-001: Bearer Token Auth**
- **Description**: Test bearer token setup
- **Setup**: Config with method='bearer'
- **Action**: Call `login()` with mock page/context
- **Expected**: Route handler adds 'Authorization: Bearer {key}'
- **Priority**: P1 (High)

**TC-AK-002: Header API Key**
- **Description**: Test custom header API key
- **Setup**: Config with method='header', key_name='X-API-Key'
- **Action**: Call `login()`
- **Expected**: Route handler adds custom header with key
- **Priority**: P1 (High)

**TC-AK-003: Query Parameter API Key**
- **Description**: Test query parameter API key
- **Setup**: Config with method='query_param', key_name='api_key'
- **Action**: Call `login()`
- **Expected**: Route handler appends ?api_key={key} to URLs
- **Priority**: P1 (High)

**TC-AK-004: Missing API Key**
- **Description**: Test error when API key not in credentials
- **Setup**: Empty credentials dict
- **Action**: Initialize APIKeyAuth
- **Expected**: Raises `LoginFailedException`
- **Priority**: P1 (High)

**TC-AK-005: Session Always Valid**
- **Description**: Test that API key sessions don't expire
- **Action**: Call `validate_session()`
- **Expected**: Always returns True
- **Priority**: P2 (Medium)

### 1.4 None Auth Tests

**File**: `tests/unit/test_none_auth.py`

#### Test Cases

**TC-NA-001: Login Success**
- **Description**: Test no-op login for public sites
- **Action**: Call `login()`
- **Expected**: Returns True immediately, no side effects
- **Priority**: P1 (High)

**TC-NA-002: Session Always Valid**
- **Description**: Test session validation for public sites
- **Action**: Call `validate_session()`
- **Expected**: Returns True always
- **Priority**: P2 (Medium)

**TC-NA-003: No Credentials Required**
- **Description**: Test that None auth works without credentials
- **Setup**: Empty credentials dict
- **Action**: Initialize and call login()
- **Expected**: Success, no errors
- **Priority**: P1 (High)

---

## 2. Integration Tests

### 2.1 EMIS Plugin Tests

**File**: `tests/integration/test_emis_plugin.py`

#### Test Cases

**TC-EP-001: Load EMIS Config**
- **Description**: Test loading EMIS plugin configuration
- **Action**: Load EMIS plugin
- **Expected**: All fields populated correctly
- **Priority**: P0 (Critical)

**TC-EP-002: Validate EMIS Config**
- **Description**: Test EMIS config passes validation
- **Action**: Run validation on EMIS config
- **Expected**: No validation errors
- **Priority**: P0 (Critical)

**TC-EP-003: EMIS Auth Config**
- **Description**: Verify EMIS auth configuration
- **Expected**:
  - scenario == 'simple_form'
  - login_url present
  - selectors defined
  - success_indicators defined
- **Priority**: P0 (Critical)

**TC-EP-004: EMIS Extraction Config**
- **Description**: Verify extraction strategies configured
- **Expected**:
  - Table extraction configured
  - Content extraction configured
  - Raw extraction configured
- **Priority**: P1 (High)

**TC-EP-005: EMIS Rate Limiting**
- **Description**: Verify rate limiting configured
- **Expected**:
  - requests_per_minute == 10
  - concurrent_sessions == 1
- **Priority**: P2 (Medium)

### 2.2 Template Plugin Tests

**File**: `tests/integration/test_template_plugin.py`

#### Test Cases

**TC-TP-001: Template Config Valid**
- **Description**: Verify template config is valid
- **Action**: Load and validate template plugin
- **Expected**: Passes validation
- **Priority**: P1 (High)

**TC-TP-002: Template Has All Scenarios**
- **Description**: Verify template shows all auth scenarios
- **Action**: Check template config comments/examples
- **Expected**: Documents simple_form, api_key, oauth2, etc.
- **Priority**: P2 (Medium)

**TC-TP-003: Template README Complete**
- **Description**: Verify template README has all sections
- **Expected**: Contains:
  - Creating a Plugin section
  - Authentication scenarios
  - Testing checklist
  - Examples
- **Priority**: P2 (Medium)

### 2.3 Plugin Creation Tests

**File**: `tests/integration/test_plugin_creation.py`

#### Test Cases

**TC-PC-001: Create Plugin from Template**
- **Description**: Test creating new plugin from template
- **Actions**:
  1. Copy template to new directory
  2. Modify config.yaml
  3. Load new plugin
- **Expected**: New plugin loads successfully
- **Priority**: P1 (High)

**TC-PC-002: Multiple Plugins Coexist**
- **Description**: Test loading multiple plugins simultaneously
- **Actions**:
  1. Load EMIS plugin
  2. Load template plugin
  3. Create and load test plugin
- **Expected**: All 3 plugins loaded, no conflicts
- **Priority**: P1 (High)

---

## 3. End-to-End Scenarios

### 3.1 Fresh Install Scenario

**File**: `tests/e2e/test_fresh_install.py`

**TC-E2E-001: Complete Setup Flow**
- **Description**: Simulate fresh installation
- **Steps**:
  1. Start with clean environment
  2. Install dependencies
  3. Set up credentials
  4. Start backend
  5. Execute first query
- **Expected**: Success in < 5 minutes
- **Priority**: P0 (Critical)

### 3.2 Plugin Workflows

**File**: `tests/e2e/test_workflows.py`

**TC-E2E-002: Query Workflow**
- **Description**: Complete query execution flow
- **Steps**:
  1. Load plugin
  2. Authenticate
  3. Execute search
  4. Extract results
  5. Return formatted data
- **Expected**: Results returned correctly
- **Priority**: P0 (Critical)

**TC-E2E-003: Session Persistence**
- **Description**: Test session reuse across queries
- **Steps**:
  1. Execute first query (authenticates)
  2. Execute second query (reuses session)
  3. Wait for TTL expiry
  4. Execute third query (re-authenticates)
- **Expected**: Sessions managed correctly
- **Priority**: P1 (High)

---

## 4. Backwards Compatibility Tests

### 4.1 Legacy Configuration

**TC-BC-001: Legacy EMIS Config Works**
- **Description**: Test old sites/emis.yaml still works
- **Setup**: Use backend/sites/emis.yaml
- **Action**: Execute query
- **Expected**: Works as before
- **Priority**: P0 (Critical)

**TC-BC-002: Legacy Environment Variables**
- **Description**: Test old env var names work
- **Setup**: Set EMIS_EMAIL and EMIS_PASSWORD
- **Action**: Authenticate
- **Expected**: Credentials loaded correctly
- **Priority**: P0 (Critical)

**TC-BC-003: Legacy CLI Commands**
- **Description**: Test all old CLI commands work
- **Actions**: Run each command from v1.x
- **Expected**: All commands produce expected output
- **Priority**: P0 (Critical)

**TC-BC-004: Legacy API Endpoints**
- **Description**: Test all old API endpoints work
- **Actions**: Test GET /, GET /sites, POST /query
- **Expected**: All return correct responses
- **Priority**: P0 (Critical)

---

## 5. Error Handling Tests

### 5.1 Graceful Failures

**TC-EH-001: Missing Credentials**
- **Description**: Test helpful error for missing credentials
- **Setup**: No credentials set
- **Action**: Attempt authentication
- **Expected**: Clear error message about setting env vars
- **Priority**: P1 (High)

**TC-EH-002: Invalid Plugin Config**
- **Description**: Test error message for invalid config
- **Setup**: Config missing required field
- **Action**: Load plugin
- **Expected**: ValidationError with field name and fix suggestion
- **Priority**: P1 (High)

**TC-EH-003: Network Timeout**
- **Description**: Test timeout handling
- **Setup**: Mock slow network
- **Action**: Execute query
- **Expected**: Timeout error with retry suggestion
- **Priority**: P2 (Medium)

---

## 6. Performance Tests

### 6.1 Benchmarks

**TC-PERF-001: Plugin Loading Speed**
- **Metric**: Time to load plugin
- **Target**: < 100ms per plugin
- **Priority**: P2 (Medium)

**TC-PERF-002: Query Response Time**
- **Metric**: End-to-end query time
- **Target**: < 3s for simple query
- **Priority**: P1 (High)

**TC-PERF-003: Concurrent Queries**
- **Metric**: Handle 5 concurrent queries
- **Target**: All complete within 10s
- **Priority**: P2 (Medium)

---

## 7. Security Tests

### 7.1 Credential Protection

**TC-SEC-001: Credentials Not Logged**
- **Description**: Verify credentials don't appear in logs
- **Action**: Enable debug logging, execute query
- **Expected**: No passwords or API keys in logs
- **Priority**: P0 (Critical)

**TC-SEC-002: Safe Error Messages**
- **Description**: Verify errors don't leak credentials
- **Action**: Trigger various errors
- **Expected**: No credentials in error messages
- **Priority**: P0 (Critical)

---

## Test Execution

### Prerequisites

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock
playwright install chromium
```

### Running Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/ -v

# Integration tests (requires setup)
pytest tests/integration/ -m integration

# With coverage
pytest --cov=backend tests/

# Generate HTML coverage report
pytest --cov=backend --cov-report=html tests/

# Specific test
pytest tests/unit/test_plugin_manager.py::test_discover_plugins

# Verbose with output
pytest -v -s tests/
```

### Test Markers

```python
# Mark integration tests
@pytest.mark.integration

# Mark slow tests
@pytest.mark.slow

# Mark tests requiring credentials
@pytest.mark.requires_credentials
```

---

## Success Criteria

### Coverage Goals
- **Unit Tests**: 90%+ coverage of core modules
- **Integration Tests**: All major workflows covered
- **E2E Tests**: Key user scenarios validated

### Quality Metrics
- ✅ All P0 tests pass
- ✅ 95%+ of P1 tests pass
- ✅ 80%+ of P2 tests pass
- ✅ No security test failures
- ✅ Performance targets met

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Test Quid MCP
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov pytest-asyncio
          playwright install chromium
      - name: Run tests
        run: pytest --cov=backend tests/
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Test Maintenance

### Regular Updates
- Update tests when adding new features
- Review and update test scenarios quarterly
- Keep mock data current
- Update documentation

### Test Reviews
- Code review includes test review
- Maintain test quality standards
- Keep tests DRY (Don't Repeat Yourself)
- Ensure tests are readable and maintainable

---

## Appendix

### Test Data Locations
- Mock plugins: `tests/fixtures/mock_plugin/`
- Mock credentials: `tests/fixtures/credentials.py`
- Mock responses: `tests/fixtures/mock_responses.py`

### Useful Commands

```bash
# Run only failed tests
pytest --lf

# Run tests in parallel
pytest -n auto

# Stop on first failure
pytest -x

# Show slowest tests
pytest --durations=10

# Debug mode
pytest --pdb
```

---

**Version History**:
- v1.0 (2025-11-08): Initial test scenarios for Quid MCP v2.0.0-alpha
