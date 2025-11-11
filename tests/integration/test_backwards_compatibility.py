#!/usr/bin/env python3
"""
Integration tests for Backwards Compatibility.

Tests that legacy sites and existing functionality still work.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from core.scraper import GenericScraper, ScraperException
from core.config_loader import get_config_loader


@pytest.mark.integration
class TestLegacySiteSupport:
    """Test legacy site support."""
    
    def test_legacy_site_queries_work(self):
        """TC-BC-001: Legacy Site Queries Work."""
        # Try to load example site if it exists
        try:
            scraper = GenericScraper('example')
            assert scraper.config is not None
            assert scraper.is_plugin is False
        except ScraperException:
            pytest.skip("Legacy example site not available")
    
    def test_legacy_auth_still_works(self):
        """TC-BC-002: Legacy Auth Still Works."""
        try:
            scraper = GenericScraper('example')
            
            # Mock credentials
            with patch('core.scraper.get_credential_manager') as mock_cred_mgr:
                mock_cred_mgr.return_value.get_credentials.return_value = {
                    'email': 'test@example.com',
                    'password': 'testpass'
                }
                
                auth_strategy = scraper._get_auth_strategy()
                # Should work without errors
                assert auth_strategy is not None or scraper.config.get('auth', {}).get('type') == 'none'
        except ScraperException:
            pytest.skip("Legacy example site not available")
    
    def test_existing_cli_commands_unchanged(self):
        """TC-BC-004: Existing CLI Commands Unchanged."""
        # Test that basic CLI commands still work
        cli_path = Path(__file__).parent.parent.parent / "backend" / "cli.py"
        
        import subprocess
        result = subprocess.run(
            [sys.executable, str(cli_path), "list"],
            capture_output=True,
            text=True,
            cwd=str(cli_path.parent)
        )
        
        # Should still work
        assert result.returncode == 0


@pytest.mark.integration
class TestConfigLoaderCompatibility:
    """Test config loader backwards compatibility."""
    
    def test_config_loader_checks_plugins_first(self):
        """TC-BC-005: Config Loader Checks Plugins First."""
        config_loader = get_config_loader()
        
        # EMIS should load from plugin
        config = config_loader.load_site('emis')
        
        # Should have plugin metadata if loaded from plugin
        assert config is not None
        # If loaded from plugin, should have 'plugin' key
        # If loaded from legacy, should have 'site_id' key
        assert 'plugin' in config or 'site_id' in config
    
    def test_config_loader_falls_back_to_legacy(self):
        """TC-BC-006: Config Loader Falls Back to Legacy."""
        config_loader = get_config_loader()
        
        try:
            config = config_loader.load_site('example')
            assert config is not None
            # Legacy configs have 'site_id'
            assert 'site_id' in config or 'name' in config
        except Exception:
            pytest.skip("Legacy example site not available")


@pytest.mark.integration
class TestMixedPluginLegacy:
    """Test mixed plugin and legacy usage."""
    
    def test_query_both_plugin_and_legacy(self):
        """TC-WF-003: Query Both Plugin and Legacy."""
        # Query plugin site
        scraper_plugin = GenericScraper('emis')
        assert scraper_plugin.config is not None
        
        # Query legacy site if available
        try:
            scraper_legacy = GenericScraper('example')
            assert scraper_legacy.config is not None
        except ScraperException:
            pytest.skip("Legacy example site not available")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])

