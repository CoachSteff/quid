#!/usr/bin/env python3
"""
Integration tests for API Plugin Endpoints.

Tests API plugin management endpoints work correctly.
"""

import pytest
import sys
import requests
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))


@pytest.mark.integration
class TestAPIPluginEndpoints:
    """Test API plugin management endpoints."""
    
    @pytest.fixture
    def api_url(self):
        """Base API URL."""
        return "http://localhost:38153"
    
    @pytest.fixture
    def api_available(self, api_url):
        """Check if API is available."""
        try:
            response = requests.get(f"{api_url}/", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def test_list_plugins(self, api_url, api_available):
        """TC-API-001: List Plugins."""
        if not api_available:
            pytest.skip("API server not available")
        
        response = requests.get(f"{api_url}/plugins", timeout=5)
        
        assert response.status_code == 200
        data = response.json()
        assert "plugins" in data
        assert "count" in data
        assert isinstance(data["plugins"], list)
    
    def test_get_plugin_details(self, api_url, api_available):
        """TC-API-002: Get Plugin Details."""
        if not api_available:
            pytest.skip("API server not available")
        
        response = requests.get(f"{api_url}/plugins/emis", timeout=5)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "emis"
        assert "name" in data
        assert "version" in data
        assert "auth_scenario" in data
    
    def test_enable_plugin_via_api(self, api_url, api_available):
        """TC-API-003: Enable Plugin via API."""
        if not api_available:
            pytest.skip("API server not available")
        
        response = requests.post(f"{api_url}/plugins/emis/enable", timeout=5)
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
    
    def test_disable_plugin_via_api(self, api_url, api_available):
        """TC-API-004: Disable Plugin via API."""
        if not api_available:
            pytest.skip("API server not available")
        
        response = requests.post(f"{api_url}/plugins/emis/disable", timeout=5)
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        
        # Re-enable for other tests
        requests.post(f"{api_url}/plugins/emis/enable", timeout=5)
    
    def test_plugin_not_found(self, api_url, api_available):
        """TC-API-005: Plugin Not Found."""
        if not api_available:
            pytest.skip("API server not available")
        
        response = requests.get(f"{api_url}/plugins/nonexistent_plugin_xyz", timeout=5)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data.get("detail", "").lower()


@pytest.mark.integration
class TestAPIUpdatedEndpoints:
    """Test updated API endpoints."""
    
    @pytest.fixture
    def api_url(self):
        """Base API URL."""
        return "http://localhost:38153"
    
    @pytest.fixture
    def api_available(self, api_url):
        """Check if API is available."""
        try:
            response = requests.get(f"{api_url}/", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def test_sites_endpoint_still_works(self, api_url, api_available):
        """TC-API-007: Sites Endpoint Still Works."""
        if not api_available:
            pytest.skip("API server not available")
        
        response = requests.get(f"{api_url}/sites", timeout=5)
        
        assert response.status_code == 200
        data = response.json()
        assert "sites" in data
        assert "count" in data
    
    def test_query_plugin_via_api(self, api_url, api_available):
        """TC-API-008: Query Plugin via API."""
        if not api_available:
            pytest.skip("API server not available")
        
        response = requests.post(
            f"{api_url}/query/emis",
            json={"query": "test"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        # May succeed or fail depending on credentials, but should not be 404
        assert response.status_code != 404
        if response.status_code == 200:
            data = response.json()
            assert "status" in data or "raw_data" in data


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])

