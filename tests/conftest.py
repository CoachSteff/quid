#!/usr/bin/env python3
"""
Pytest configuration for Quid MCP tests.

Defines fixtures, markers, and test configuration.
"""

import pytest
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


# Test markers
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires full setup)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_credentials: mark test as requiring real credentials"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )


@pytest.fixture
def mock_credentials():
    """Provide mock credentials for testing."""
    return {
        'email': 'test@example.com',
        'password': 'test_password',
        'api_key': 'test_api_key_12345'
    }


@pytest.fixture
def mock_plugin_config():
    """Provide a valid mock plugin configuration."""
    return {
        'plugin': {
            'id': 'mock_plugin',
            'name': 'Mock Plugin',
            'version': '1.0.0',
            'author': 'Test Author',
            'description': 'A mock plugin for testing',
            'homepage': 'https://example.com',
            'category': 'test',
            'tags': ['test', 'mock'],
            'license': 'MIT'
        },
        'auth': {
            'scenario': 'none',
            'type': 'none'
        },
        'extraction': {
            'strategies': [
                {'type': 'raw'}
            ]
        },
        'rate_limit': {
            'requests_per_minute': 10,
            'concurrent_sessions': 1
        }
    }


@pytest.fixture
def plugins_directory():
    """Provide path to plugins directory."""
    return Path(__file__).parent.parent / "plugins"


@pytest.fixture
def temp_plugin_dir(tmp_path):
    """Create a temporary plugins directory for testing."""
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    return plugins_dir
