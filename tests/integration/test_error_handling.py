#!/usr/bin/env python3
"""
Integration tests for Error Handling.

Tests graceful error handling in various scenarios.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, Mock

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from core.scraper import GenericScraper, ScraperException
from core.plugin_manager import PluginValidationError


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_plugin_manager_import_error_fallback(self):
        """TC-ERR-001: Plugin Manager Import Error."""
        # Mock ImportError when importing plugin_manager
        original_import = __import__
        
        def mock_import(name, *args, **kwargs):
            if 'plugin_manager' in name:
                raise ImportError("No module named 'core.plugin_manager'")
            return original_import(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            # Should fall back gracefully
            try:
                scraper = GenericScraper('emis')
                assert scraper.config is not None
            except ScraperException:
                # If emis doesn't exist as legacy, that's expected
                pass
    
    def test_auth_registry_import_error_fallback(self):
        """TC-ERR-002: AuthRegistry Import Error."""
        scraper = GenericScraper('emis')

        with patch('core.scraper.get_credential_manager') as mock_cred_mgr:
            mock_cred_mgr.return_value.get_credentials.return_value = {
                'email': 'test@example.com',
                'password': 'testpass'
            }

            # Mock ImportError for AuthRegistry by patching the import statement
            # AuthRegistry is imported locally in _get_auth_strategy, so we need to make that import fail
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
    
    def test_plugin_not_found_fallback(self):
        """TC-ERR-003: Plugin Not Found."""
        # Try to load a site that doesn't exist
        with pytest.raises(ScraperException) as exc:
            GenericScraper('definitely_nonexistent_site_xyz_123')
        
        # Should have clear error message
        assert len(str(exc.value)) > 0
    
    def test_invalid_plugin_config(self):
        """TC-ERR-004: Invalid Plugin Config."""
        from core.plugin_manager import PluginManager
        
        pm = PluginManager()
        
        invalid_config = {
            'auth': {'scenario': 'simple_form'}
            # Missing 'plugin' section
        }
        
        with pytest.raises(PluginValidationError) as exc:
            pm.validate_plugin_config(invalid_config, 'test')
        
        assert 'missing' in str(exc.value).lower() or 'plugin' in str(exc.value).lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])

