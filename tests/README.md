# Quid MCP Test Suite

Comprehensive test suite for Quid MCP v2.0.0-alpha.

## Structure

```
tests/
├── unit/                      # Unit tests
│   ├── test_plugin_manager.py
│   ├── test_auth_registry.py
│   └── ...
├── integration/               # Integration tests
│   ├── test_emis_plugin.py
│   └── ...
├── e2e/                      # End-to-end tests
│   └── ...
├── fixtures/                 # Test data and mocks
│   └── ...
├── conftest.py              # Pytest configuration
└── README.md                # This file
```

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Install Playwright
playwright install chromium
```

### Basic Usage

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_plugin_manager.py

# Run specific test
pytest tests/unit/test_plugin_manager.py::TestPluginDiscovery::test_discover_plugins
```

### Coverage

```bash
# Run with coverage
pytest --cov=backend tests/

# Generate HTML coverage report
pytest --cov=backend --cov-report=html tests/

# View coverage report
open htmlcov/index.html  # macOS
```

### Test Markers

```bash
# Run only integration tests
pytest -m integration tests/

# Skip slow tests
pytest -m "not slow" tests/

# Run tests requiring credentials
pytest -m requires_credentials tests/

# Run end-to-end tests
pytest -m e2e tests/
```

### Useful Options

```bash
# Stop on first failure
pytest -x tests/

# Show local variables on failure
pytest -l tests/

# Run last failed tests
pytest --lf tests/

# Run tests in parallel (requires pytest-xdist)
pytest -n auto tests/

# Show print statements
pytest -s tests/

# Show slowest 10 tests
pytest --durations=10 tests/
```

## Test Categories

### Unit Tests (tests/unit/)

Test individual components in isolation.

**Current tests:**
- `test_plugin_manager.py` - Plugin system tests
- `test_auth_registry.py` - Auth registry tests

**To run:**
```bash
pytest tests/unit/ -v
```

### Integration Tests (tests/integration/)

Test components working together.

**Planned tests:**
- `test_emis_plugin.py` - EMIS plugin integration
- `test_template_plugin.py` - Template plugin validation
- `test_plugin_creation.py` - Plugin creation workflow

**To run:**
```bash
pytest tests/integration/ -m integration
```

### End-to-End Tests (tests/e2e/)

Test complete user workflows.

**Planned tests:**
- `test_fresh_install.py` - Fresh installation scenario
- `test_mcp_integration.py` - MCP server integration
- `test_workflows.py` - Complete query workflows

**To run:**
```bash
pytest tests/e2e/ -m e2e
```

## Writing Tests

### Test Structure

```python
#!/usr/bin/env python3
"""
Brief description of what this module tests.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from module_to_test import ClassToTest


class TestFeature:
    """Test specific feature."""
    
    def test_something(self):
        """TC-XX-001: Test description."""
        # Arrange
        obj = ClassToTest()
        
        # Act
        result = obj.do_something()
        
        # Assert
        assert result == expected_value


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

### Using Fixtures

```python
def test_with_fixture(mock_credentials):
    """Use fixtures from conftest.py"""
    assert mock_credentials['email'] == 'test@example.com'
```

### Markers

```python
@pytest.mark.integration
def test_integration_feature():
    """Mark as integration test"""
    pass

@pytest.mark.slow
def test_slow_feature():
    """Mark as slow test"""
    pass

@pytest.mark.requires_credentials
def test_with_real_credentials():
    """Mark as needing real credentials"""
    pass
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_feature():
    """Test async function"""
    result = await async_function()
    assert result is True
```

## Test Data

### Mock Plugins

Mock plugins for testing are located in `tests/fixtures/`.

### Mock Credentials

Use the `mock_credentials` fixture from `conftest.py`:

```python
def test_something(mock_credentials):
    email = mock_credentials['email']
    password = mock_credentials['password']
```

## Continuous Integration

Tests run automatically on GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r backend/requirements.txt
      - run: pip install pytest pytest-cov pytest-asyncio
      - run: playwright install chromium
      - run: pytest --cov=backend tests/
```

## Coverage Goals

- **Unit Tests**: 90%+ coverage
- **Integration Tests**: All major workflows
- **E2E Tests**: Key user scenarios

## Current Status

- ✅ Test structure created
- ✅ pytest configured
- ✅ Unit tests for PluginManager
- ✅ Unit tests for AuthRegistry
- 🔜 Integration tests (planned)
- 🔜 E2E tests (planned)
- 🔜 CI/CD integration (planned)

## Contributing Tests

When adding new features:

1. Write tests first (TDD)
2. Ensure tests pass locally
3. Run coverage check
4. Update test documentation
5. Submit PR with tests

## Troubleshooting

### Import Errors

If you get import errors:

```bash
# Make sure you're in the project root
cd /path/to/quid

# Run tests from project root
pytest tests/
```

### Playwright Issues

If Playwright tests fail:

```bash
# Reinstall browsers
playwright install chromium

# Check installation
playwright install --dry-run
```

### Async Test Issues

If async tests fail:

```bash
# Make sure pytest-asyncio is installed
pip install pytest-asyncio

# Run with asyncio mode
pytest --asyncio-mode=auto tests/
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Test Scenarios](../docs/testing/TEST_SCENARIOS.md)

---

**Need help?** Check the [troubleshooting guide](../docs/troubleshooting/) or open an issue.
