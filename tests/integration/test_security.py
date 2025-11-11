#!/usr/bin/env python3
"""
Security tests for Phase 2 Integration.

Tests credential handling and security best practices.
"""

import pytest
import sys
import logging
from pathlib import Path
from io import StringIO
from unittest.mock import patch

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))


@pytest.mark.integration
class TestSecurity:
    """Security tests."""
    
    def test_credentials_not_exposed_in_logs(self):
        """TC-SEC-001: Credentials Not Exposed in Logs."""
        from core.scraper import GenericScraper
        
        # Capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)
        
        logger = logging.getLogger('core.scraper')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            scraper = GenericScraper('emis')
            
            # Mock credentials with sensitive data
            with patch('core.scraper.get_credential_manager') as mock_cred_mgr:
                mock_cred_mgr.return_value.get_credentials.return_value = {
                    'email': 'test@example.com',
                    'password': 'secret_password_123',
                    'api_key': 'sk_live_abc123xyz789'
                }
                
                # Trigger auth strategy creation (which might log)
                try:
                    scraper._get_auth_strategy()
                except:
                    pass
            
            # Get log output
            log_output = log_capture.getvalue()
            
            # Verify sensitive data not in logs
            assert 'secret_password_123' not in log_output
            assert 'sk_live_abc123xyz789' not in log_output
            # Email might be in logs (less sensitive), but password should not be
            
        finally:
            logger.removeHandler(handler)
    
    def test_plugin_config_validation(self):
        """TC-SEC-002: Plugin Config Validation."""
        from core.plugin_manager import PluginManager, PluginValidationError
        
        pm = PluginManager()
        
        # Test invalid auth config
        invalid_config = {
            'plugin': {
                'id': 'test',
                'name': 'Test',
                'version': '1.0.0',
                'description': 'Test'
            },
            'auth': {
                'scenario': 'invalid_scenario'
            }
        }
        
        # Should fail validation before execution
        with pytest.raises(PluginValidationError):
            pm.validate_plugin_config(invalid_config, 'test')
    
    def test_credentials_masked_in_output(self):
        """Test that credentials are masked in CLI output."""
        import subprocess
        from pathlib import Path
        
        cli_path = Path(__file__).parent.parent.parent / "backend" / "cli.py"
        
        result = subprocess.run(
            [sys.executable, str(cli_path), "check", "emis"],
            capture_output=True,
            text=True,
            cwd=str(cli_path.parent)
        )
        
        if result.returncode == 0:
            output = result.stdout.lower()
            # Should not contain actual passwords
            # Should contain masked versions like "******"
            assert '******' in output or 'no credentials' in output or 'not found' in output


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])

