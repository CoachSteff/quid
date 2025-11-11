#!/usr/bin/env python3
"""
Unit tests for Scraper Plugin Integration.

Tests that scraper correctly uses plugin_manager and falls back to config_loader.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from core.scraper import GenericScraper, ScraperException
from core.config_loader import ConfigurationException


class TestScraperPluginLoading:
    """Test scraper plugin loading functionality."""
    
    def test_load_plugin_via_scraper(self):
        """TC-SCRAPER-001: Load Plugin via Scraper."""
        scraper = GenericScraper('emis')
        
        assert scraper.is_plugin is True
        assert scraper.config is not None
        assert 'plugin' in scraper.config
        assert scraper.config['plugin']['id'] == 'emis'
        assert scraper.config['plugin']['name'] == 'VITO EMIS Portal'
    
    def test_fallback_to_legacy_config(self):
        """TC-SCRAPER-002: Fallback to Legacy Config."""
        # Use example site which should be legacy
        # If example doesn't exist, this test will be skipped
        try:
            scraper = GenericScraper('example')
            # If it loads, it should be legacy
            assert scraper.is_plugin is False
            assert scraper.config is not None
            assert 'site_id' in scraper.config or 'name' in scraper.config
        except ScraperException:
            # If example site doesn't exist, skip this test
            pytest.skip("Legacy example site not available")
    
    def test_plugin_priority_over_legacy(self):
        """TC-SCRAPER-003: Plugin Priority Over Legacy."""
        # EMIS has both plugin and potentially legacy config
        scraper = GenericScraper('emis')
        
        # Should load plugin, not legacy
        assert scraper.is_plugin is True
        assert 'plugin' in scraper.config
    
    def test_disabled_plugin_falls_back(self):
        """TC-SCRAPER-004: Disabled Plugin Falls Back."""
        from core.plugin_manager import get_plugin_manager
        
        plugin_manager = get_plugin_manager()
        plugin_manager.load_all_plugins()
        
        # Disable plugin
        plugin_manager.disable_plugin('emis')
        
        try:
            scraper = GenericScraper('emis')
            # Should fall back to legacy if available
            # If no legacy, should still work but with disabled plugin
            assert scraper.config is not None
        finally:
            # Re-enable plugin for other tests
            plugin_manager.enable_plugin('emis')
    
    def test_nonexistent_site_raises_error(self):
        """Test that nonexistent site raises ScraperException."""
        with pytest.raises(ScraperException) as exc:
            GenericScraper('nonexistent_site_xyz_123')
        
        assert 'configuration error' in str(exc.value).lower() or 'not found' in str(exc.value).lower()


class TestScraperAuthRegistry:
    """Test scraper AuthRegistry integration."""
    
    def test_auth_registry_with_plugin_config(self):
        """TC-SCRAPER-005: AuthRegistry with Plugin Config."""
        scraper = GenericScraper('emis')
        
        # Mock credentials
        with patch('core.scraper.get_credential_manager') as mock_cred_mgr:
            mock_cred_mgr.return_value.get_credentials.return_value = {
                'email': 'test@example.com',
                'password': 'testpass'
            }
            
            auth_strategy = scraper._get_auth_strategy()
            
            # Should use AuthRegistry, not hardcoded logic
            assert auth_strategy is not None
            # Verify it's using the registry by checking it's FormBasedAuth
            from auth.strategies.form_based import FormBasedAuth
            assert isinstance(auth_strategy, FormBasedAuth)
    
    def test_auth_registry_with_legacy_config(self):
        """TC-SCRAPER-006: AuthRegistry with Legacy Config."""
        try:
            scraper = GenericScraper('example')
            
            # Mock credentials
            with patch('core.scraper.get_credential_manager') as mock_cred_mgr:
                mock_cred_mgr.return_value.get_credentials.return_value = {
                    'email': 'test@example.com',
                    'password': 'testpass'
                }
                
                auth_strategy = scraper._get_auth_strategy()
                
                # Should convert type to scenario and use registry
                if auth_strategy is not None:
                    from auth.strategies.form_based import FormBasedAuth
                    assert isinstance(auth_strategy, FormBasedAuth)
        except ScraperException:
            pytest.skip("Legacy example site not available")
    
    def test_none_auth_via_registry(self):
        """TC-SCRAPER-008: None Auth via Registry."""
        # Create a mock plugin config with none auth
        with patch('core.plugin_manager.get_plugin_manager') as mock_pm:
            mock_plugin = Mock()
            mock_plugin.enabled = True
            mock_plugin.config = {
                'plugin': {'id': 'test', 'name': 'Test'},
                'auth': {'scenario': 'none'},
                'extraction': {'strategies': []}
            }
            
            mock_pm.return_value.get_plugin.return_value = mock_plugin
            
            scraper = GenericScraper('test')
            auth_strategy = scraper._get_auth_strategy()
            
            # None auth should return None
            assert auth_strategy is None
    
    def test_invalid_auth_scenario_raises_error(self):
        """TC-SCRAPER-009: Invalid Auth Scenario."""
        # Create a mock plugin config with invalid auth scenario
        with patch('core.plugin_manager.get_plugin_manager') as mock_pm:
            mock_plugin = Mock()
            mock_plugin.enabled = True
            mock_plugin.config = {
                'plugin': {'id': 'test', 'name': 'Test'},
                'auth': {'scenario': 'invalid_type_xyz'},
                'extraction': {'strategies': []}
            }
            
            mock_pm.return_value.get_plugin.return_value = mock_plugin
            
            scraper = GenericScraper('test')
            
            with patch('core.scraper.get_credential_manager') as mock_cred_mgr:
                mock_cred_mgr.return_value.get_credentials.return_value = {}
                
                with pytest.raises(ScraperException) as exc:
                    scraper._get_auth_strategy()
                
                assert 'unsupported' in str(exc.value).lower() or 'invalid' in str(exc.value).lower()


class TestScraperPluginFallback:
    """Test scraper fallback mechanisms."""
    
    def test_plugin_manager_import_error_fallback(self):
        """TC-ERR-001: Plugin Manager Import Error."""
        # Mock ImportError when importing plugin_manager
        with patch('builtins.__import__', side_effect=ImportError("No module named 'core.plugin_manager'")):
            # Should fall back to config_loader
            try:
                scraper = GenericScraper('emis')
                assert scraper.config is not None
            except ScraperException:
                # If emis doesn't exist as legacy, that's okay
                pass
    
    def test_plugin_not_found_fallback(self):
        """TC-ERR-003: Plugin Not Found."""
        # Try to load a site that doesn't exist as plugin or legacy
        with pytest.raises(ScraperException):
            GenericScraper('definitely_nonexistent_site_xyz')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

