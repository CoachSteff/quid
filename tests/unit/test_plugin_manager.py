#!/usr/bin/env python3
"""
Unit tests for Plugin Manager.

Tests plugin discovery, loading, validation, and lifecycle management.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from core.plugin_manager import (
    PluginManager,
    Plugin,
    PluginValidationError,
    get_plugin_manager
)


class TestPluginDiscovery:
    """Test plugin discovery functionality."""
    
    def test_discover_plugins(self):
        """TC-PM-001: Test plugin discovery finds EMIS and template."""
        pm = PluginManager()
        plugins = pm.discover_plugins()
        
        assert isinstance(plugins, list)
        assert 'emis' in plugins
        assert 'template' in plugins
        assert len(plugins) >= 2
    
    def test_discover_plugins_handles_missing_directory(self, tmp_path):
        """TC-PM-009: Test graceful handling of missing plugins directory."""
        pm = PluginManager(plugins_dir=str(tmp_path / "nonexistent"))
        plugins = pm.discover_plugins()
        
        assert isinstance(plugins, list)
        assert len(plugins) == 0
        # Should not raise exception


class TestPluginLoading:
    """Test plugin loading functionality."""
    
    def test_load_emis_plugin(self):
        """TC-PM-002: Load EMIS plugin successfully."""
        pm = PluginManager()
        plugin = pm.load_plugin('emis')
        
        assert isinstance(plugin, Plugin)
        assert plugin.id == 'emis'
        assert plugin.name == 'VITO EMIS Portal'
        assert plugin.version == '1.0.0'
        assert plugin.author == 'Quid Contributors'
        assert plugin.category == 'environmental'
        assert 'belgium' in plugin.tags
        assert plugin.enabled is True
        assert plugin.loaded_at is not None
    
    def test_load_nonexistent_plugin(self):
        """TC-PM-003: Attempt to load missing plugin raises error."""
        pm = PluginManager()
        
        with pytest.raises(FileNotFoundError) as exc:
            pm.load_plugin('nonexistent_plugin_xyz')
        
        assert 'not found' in str(exc.value).lower()
    
    def test_load_all_plugins(self):
        """TC-PM-010: Test bulk loading of all plugins."""
        pm = PluginManager()
        plugins = pm.load_all_plugins()
        
        assert isinstance(plugins, dict)
        assert 'emis' in plugins
        assert 'template' in plugins
        assert all(isinstance(p, Plugin) for p in plugins.values())


class TestPluginValidation:
    """Test plugin configuration validation."""
    
    def test_validate_valid_config(self):
        """TC-PM-004: Test validation with valid EMIS config."""
        pm = PluginManager()
        
        valid_config = {
            'plugin': {
                'id': 'test',
                'name': 'Test Plugin',
                'version': '1.0.0',
                'description': 'Test description'
            },
            'auth': {
                'scenario': 'simple_form'
            },
            'extraction': {
                'strategies': [
                    {'type': 'table'}
                ]
            }
        }
        
        result = pm.validate_plugin_config(valid_config, 'test')
        assert result is True
    
    def test_validate_missing_plugin_section(self):
        """TC-PM-005: Reject config missing 'plugin' section."""
        pm = PluginManager()
        
        invalid_config = {
            'auth': {'scenario': 'simple_form'}
        }
        
        with pytest.raises(PluginValidationError) as exc:
            pm.validate_plugin_config(invalid_config, 'test')
        
        assert 'missing' in str(exc.value).lower()
        assert 'plugin' in str(exc.value).lower()
    
    def test_validate_missing_required_field(self):
        """TC-PM-005: Reject config missing required fields."""
        pm = PluginManager()
        
        invalid_config = {
            'plugin': {
                'id': 'test'
                # Missing 'name', 'version', 'description'
            }
        }
        
        with pytest.raises(PluginValidationError) as exc:
            pm.validate_plugin_config(invalid_config, 'test')
        
        assert 'missing required field' in str(exc.value).lower()
    
    def test_validate_invalid_auth_scenario(self):
        """TC-PM-006: Reject invalid auth scenario."""
        pm = PluginManager()
        
        invalid_config = {
            'plugin': {
                'id': 'test',
                'name': 'Test',
                'version': '1.0.0',
                'description': 'Test'
            },
            'auth': {
                'scenario': 'invalid_scenario_xyz'
            }
        }
        
        with pytest.raises(PluginValidationError) as exc:
            pm.validate_plugin_config(invalid_config, 'test')
        
        error_msg = str(exc.value).lower()
        assert 'invalid' in error_msg or 'scenario' in error_msg


class TestPluginLifecycle:
    """Test plugin lifecycle management."""
    
    def test_enable_disable_plugin(self):
        """TC-PM-007: Test plugin enable/disable functionality."""
        pm = PluginManager()
        pm.load_all_plugins()
        
        # Plugin should be enabled by default
        plugin = pm.get_plugin('emis')
        assert plugin.enabled is True
        
        # Disable it
        result = pm.disable_plugin('emis')
        assert result is True
        
        # Check it's disabled
        enabled_plugins = pm.get_enabled_plugins()
        assert 'emis' not in enabled_plugins
        
        # Re-enable it
        result = pm.enable_plugin('emis')
        assert result is True
        
        # Check it's enabled
        enabled_plugins = pm.get_enabled_plugins()
        assert 'emis' in enabled_plugins
    
    def test_get_plugin_by_id(self):
        """Test getting plugin by ID."""
        pm = PluginManager()
        plugin = pm.get_plugin('emis')
        
        assert plugin is not None
        assert plugin.id == 'emis'
    
    def test_get_nonexistent_plugin(self):
        """Test getting non-existent plugin returns None."""
        pm = PluginManager()
        pm.load_all_plugins()
        
        plugin = pm.get_plugin('nonexistent')
        assert plugin is None
    
    def test_get_plugin_info(self):
        """TC-PM-008: Test plugin info extraction."""
        pm = PluginManager()
        info = pm.get_plugin_info('emis')
        
        assert info is not None
        assert isinstance(info, dict)
        
        # Check required fields
        assert info['id'] == 'emis'
        assert info['name'] == 'VITO EMIS Portal'
        assert info['version'] == '1.0.0'
        assert info['author'] == 'Quid Contributors'
        assert info['category'] == 'environmental'
        
        # Check auth info
        assert 'auth_scenario' in info
        assert info['auth_scenario'] == 'simple_form'
        
        # Check human intervention flags
        assert 'human_intervention' in info
        assert info['human_intervention']['captcha'] is False
        assert info['human_intervention']['mfa'] is False


class TestPluginManager:
    """Test PluginManager utility functions."""
    
    def test_list_plugins_by_category(self):
        """Test grouping plugins by category."""
        pm = PluginManager()
        pm.load_all_plugins()
        
        categories = pm.list_plugins_by_category()
        
        assert isinstance(categories, dict)
        assert 'environmental' in categories
        assert 'emis' in categories['environmental']
    
    def test_get_all_plugins(self):
        """Test getting all plugins."""
        pm = PluginManager()
        all_plugins = pm.get_all_plugins()
        
        assert isinstance(all_plugins, dict)
        assert len(all_plugins) >= 2
        assert 'emis' in all_plugins
    
    def test_singleton_plugin_manager(self):
        """Test global plugin manager singleton."""
        pm1 = get_plugin_manager()
        pm2 = get_plugin_manager()
        
        assert pm1 is pm2


class TestPluginConfiguration:
    """Test plugin configuration details."""
    
    def test_emis_has_auth_config(self):
        """Test EMIS plugin has authentication configured."""
        pm = PluginManager()
        plugin = pm.load_plugin('emis')
        
        assert 'auth' in plugin.config
        auth = plugin.config['auth']
        assert auth['scenario'] == 'simple_form'
        assert 'login_url' in auth
        assert 'selectors' in auth
    
    def test_emis_has_extraction_config(self):
        """Test EMIS plugin has extraction strategies configured."""
        pm = PluginManager()
        plugin = pm.load_plugin('emis')
        
        assert 'extraction' in plugin.config
        extraction = plugin.config['extraction']
        assert 'strategies' in extraction
        assert isinstance(extraction['strategies'], list)
        assert len(extraction['strategies']) > 0
    
    def test_emis_has_rate_limiting(self):
        """Test EMIS plugin has rate limiting configured."""
        pm = PluginManager()
        plugin = pm.load_plugin('emis')
        
        assert 'rate_limit' in plugin.config
        rate_limit = plugin.config['rate_limit']
        assert rate_limit['requests_per_minute'] == 10
        assert rate_limit['concurrent_sessions'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
