#!/usr/bin/env python3
"""
Unit tests for Scraper AuthRegistry Integration.

Tests that scraper correctly uses AuthRegistry instead of hardcoded auth logic.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from core.scraper import GenericScraper, ScraperException
from core.auth_registry import AuthRegistry


class TestAuthRegistryIntegration:
    """Test AuthRegistry integration in scraper."""
    
    def test_uses_auth_registry_not_hardcoded(self):
        """Verify scraper uses AuthRegistry, not hardcoded logic."""
        scraper = GenericScraper('emis')

        # Mock credentials
        with patch('core.scraper.get_credential_manager') as mock_cred_mgr:
            mock_cred_mgr.return_value.get_credentials.return_value = {
                'email': 'test@example.com',
                'password': 'testpass'
            }

            # Mock AuthRegistry to verify it's called
            # AuthRegistry is imported locally in the method, so we patch the import
            with patch('core.auth_registry.AuthRegistry') as mock_registry:
                mock_strategy_class = Mock()
                mock_registry.get.return_value = mock_strategy_class
                mock_strategy_class.return_value = Mock()
                
                scraper._get_auth_strategy()
                
                # Verify AuthRegistry.get was called
                assert mock_registry.get.called
    
    def test_auth_registry_with_simple_form(self):
        """Test AuthRegistry returns FormBasedAuth for simple_form."""
        scraper = GenericScraper('emis')
        
        with patch('core.scraper.get_credential_manager') as mock_cred_mgr:
            mock_cred_mgr.return_value.get_credentials.return_value = {
                'email': 'test@example.com',
                'password': 'testpass'
            }
            
            auth_strategy = scraper._get_auth_strategy()
            
            # Should return FormBasedAuth instance
            assert auth_strategy is not None
            from auth.strategies.form_based import FormBasedAuth
            assert isinstance(auth_strategy, FormBasedAuth)
    
    def test_auth_registry_fallback_on_import_error(self):
        """TC-ERR-002: AuthRegistry Import Error Fallback."""
        scraper = GenericScraper('emis')

        with patch('core.scraper.get_credential_manager') as mock_cred_mgr:
            mock_cred_mgr.return_value.get_credentials.return_value = {
                'email': 'test@example.com',
                'password': 'testpass'
            }

            # Mock ImportError for AuthRegistry by patching the import
            original_import = __import__

            def mock_import(name, *args, **kwargs):
                if 'auth_registry' in name:
                    raise ImportError("No module named 'core.auth_registry'")
                return original_import(name, *args, **kwargs)

            with patch('builtins.__import__', side_effect=mock_import):
                # Should fall back to legacy hardcoded logic
                auth_strategy = scraper._get_auth_strategy()

                # Should still work with fallback
                assert auth_strategy is not None
    
    def test_supports_both_scenario_and_type(self):
        """Test scraper supports both plugin format (scenario) and legacy (type)."""
        # Test plugin format
        scraper_plugin = GenericScraper('emis')
        assert scraper_plugin.config.get('auth', {}).get('scenario') == 'simple_form'
        
        # Test legacy format (if example exists)
        try:
            scraper_legacy = GenericScraper('example')
            # Legacy might use 'type' instead of 'scenario'
            auth_config = scraper_legacy.config.get('auth', {})
            # Should handle both
            assert 'scenario' in auth_config or 'type' in auth_config
        except ScraperException:
            pytest.skip("Legacy example site not available")
    
    def test_none_auth_returns_none(self):
        """Test that 'none' auth scenario returns None."""
        # Create mock plugin with none auth
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
            
            assert auth_strategy is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

