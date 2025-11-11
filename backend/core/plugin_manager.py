#!/usr/bin/env python3
"""
Plugin Manager for Quid MCP.
Handles plugin discovery, loading, validation, and lifecycle management.
"""

import logging
import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Plugin:
    """Represents a loaded plugin."""
    id: str
    name: str
    version: str
    author: str
    description: str
    homepage: str
    category: str
    tags: List[str]
    license: Optional[str]
    config: Dict[str, Any]
    path: Path
    enabled: bool = True
    loaded_at: Optional[datetime] = None


class PluginValidationError(Exception):
    """Raised when plugin validation fails."""
    pass


class PluginManager:
    """
    Manages plugin discovery, loading, and validation.
    
    Plugins are self-contained directories with a config.yaml file.
    Each plugin can have custom authentication, extraction, and search logic.
    """
    
    def __init__(self, plugins_dir: Optional[str] = None):
        """
        Initialize plugin manager.
        
        Args:
            plugins_dir: Path to plugins directory (defaults to project root/plugins)
        """
        if plugins_dir is None:
            # Default to project root/plugins
            backend_dir = Path(__file__).parent.parent
            self.plugins_dir = backend_dir.parent / "plugins"
        else:
            self.plugins_dir = Path(plugins_dir)
        
        self._plugins: Dict[str, Plugin] = {}
        self._loaded = False
        
        logger.info(f"Plugin manager initialized with directory: {self.plugins_dir}")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover all available plugins in the plugins directory.
        
        Returns:
            List of plugin IDs found
        """
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory does not exist: {self.plugins_dir}")
            return []
        
        plugin_ids = []
        
        for item in self.plugins_dir.iterdir():
            if not item.is_dir():
                continue
            
            # Check if it has a config.yaml
            config_file = item / "config.yaml"
            if not config_file.exists():
                logger.debug(f"Skipping {item.name} - no config.yaml found")
                continue
            
            plugin_ids.append(item.name)
            logger.debug(f"Discovered plugin: {item.name}")
        
        logger.info(f"Discovered {len(plugin_ids)} plugins: {plugin_ids}")
        return plugin_ids
    
    def load_plugin(self, plugin_id: str) -> Plugin:
        """
        Load a specific plugin by ID.
        
        Args:
            plugin_id: Plugin identifier (directory name)
            
        Returns:
            Loaded Plugin object
            
        Raises:
            PluginValidationError: If plugin is invalid
            FileNotFoundError: If plugin not found
        """
        plugin_path = self.plugins_dir / plugin_id
        config_file = plugin_path / "config.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Plugin '{plugin_id}' not found at {plugin_path}")
        
        # Load configuration
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            raise PluginValidationError(f"Failed to parse config.yaml: {e}")
        
        # Validate plugin configuration
        self.validate_plugin_config(config, plugin_id)
        
        # Extract plugin metadata
        plugin_meta = config.get('plugin', {})
        
        plugin = Plugin(
            id=plugin_meta.get('id', plugin_id),
            name=plugin_meta.get('name', plugin_id),
            version=plugin_meta.get('version', '1.0.0'),
            author=plugin_meta.get('author', 'Unknown'),
            description=plugin_meta.get('description', ''),
            homepage=plugin_meta.get('homepage', ''),
            category=plugin_meta.get('category', 'other'),
            tags=plugin_meta.get('tags', []),
            license=plugin_meta.get('license'),
            config=config,
            path=plugin_path,
            enabled=True,
            loaded_at=datetime.now()
        )
        
        logger.info(f"Loaded plugin: {plugin.name} v{plugin.version} ({plugin.id})")
        return plugin
    
    def validate_plugin_config(self, config: Dict[str, Any], plugin_id: str) -> bool:
        """
        Validate plugin configuration against schema.
        
        Args:
            config: Plugin configuration dictionary
            plugin_id: Plugin identifier for error messages
            
        Returns:
            True if valid
            
        Raises:
            PluginValidationError: If validation fails
        """
        # Required top-level keys
        if 'plugin' not in config:
            raise PluginValidationError(f"Plugin '{plugin_id}' missing 'plugin' section")
        
        plugin_meta = config['plugin']
        
        # Required plugin metadata
        required_fields = ['id', 'name', 'version', 'description']
        for field in required_fields:
            if field not in plugin_meta:
                raise PluginValidationError(f"Plugin '{plugin_id}' missing required field: plugin.{field}")
        
        # Validate auth section
        if 'auth' in config:
            auth = config['auth']
            if 'scenario' not in auth:
                raise PluginValidationError(f"Plugin '{plugin_id}' missing auth.scenario")
            
            valid_scenarios = ['simple_form', 'api_key', 'oauth2', 'captcha', 'mfa', 'none']
            if auth['scenario'] not in valid_scenarios:
                raise PluginValidationError(
                    f"Plugin '{plugin_id}' has invalid auth scenario: {auth['scenario']}. "
                    f"Valid options: {valid_scenarios}"
                )
        
        # Validate extraction section
        if 'extraction' in config:
            extraction = config['extraction']
            if 'strategies' not in extraction:
                raise PluginValidationError(f"Plugin '{plugin_id}' missing extraction.strategies")
            
            if not isinstance(extraction['strategies'], list):
                raise PluginValidationError(f"Plugin '{plugin_id}' extraction.strategies must be a list")
        
        logger.debug(f"Plugin '{plugin_id}' configuration validated successfully")
        return True
    
    def load_all_plugins(self, auto_enable: bool = True) -> Dict[str, Plugin]:
        """
        Load all discovered plugins.
        
        Args:
            auto_enable: Whether to auto-enable all plugins
            
        Returns:
            Dictionary of plugin_id -> Plugin
        """
        plugin_ids = self.discover_plugins()
        
        loaded = {}
        failed = []
        
        for plugin_id in plugin_ids:
            try:
                plugin = self.load_plugin(plugin_id)
                if auto_enable:
                    plugin.enabled = True
                loaded[plugin_id] = plugin
            except Exception as e:
                logger.error(f"Failed to load plugin '{plugin_id}': {e}")
                failed.append((plugin_id, str(e)))
        
        self._plugins = loaded
        self._loaded = True
        
        logger.info(f"Loaded {len(loaded)} plugins successfully")
        if failed:
            logger.warning(f"Failed to load {len(failed)} plugins: {[p[0] for p in failed]}")
        
        return loaded
    
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """
        Get a loaded plugin by ID.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin object or None if not found
        """
        if not self._loaded:
            self.load_all_plugins()
        
        return self._plugins.get(plugin_id)
    
    def get_all_plugins(self) -> Dict[str, Plugin]:
        """
        Get all loaded plugins.
        
        Returns:
            Dictionary of plugin_id -> Plugin
        """
        if not self._loaded:
            self.load_all_plugins()
        
        return self._plugins
    
    def get_enabled_plugins(self) -> Dict[str, Plugin]:
        """
        Get only enabled plugins.
        
        Returns:
            Dictionary of enabled plugins
        """
        return {
            plugin_id: plugin 
            for plugin_id, plugin in self.get_all_plugins().items() 
            if plugin.enabled
        }
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin."""
        plugin = self.get_plugin(plugin_id)
        if plugin:
            plugin.enabled = True
            logger.info(f"Enabled plugin: {plugin_id}")
            return True
        return False
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin."""
        plugin = self.get_plugin(plugin_id)
        if plugin:
            plugin.enabled = False
            logger.info(f"Disabled plugin: {plugin_id}")
            return True
        return False
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get plugin information as dictionary.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin info dictionary or None
        """
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return None
        
        # Get auth scenario info
        auth_config = plugin.config.get('auth', {})
        auth_scenario = auth_config.get('scenario', 'unknown')
        
        # Check for human intervention requirements
        human_intervention = plugin.config.get('human_intervention', {})
        
        return {
            'id': plugin.id,
            'name': plugin.name,
            'version': plugin.version,
            'author': plugin.author,
            'description': plugin.description,
            'homepage': plugin.homepage,
            'category': plugin.category,
            'tags': plugin.tags,
            'license': plugin.license,
            'auth_scenario': auth_scenario,
            'enabled': plugin.enabled,
            'loaded_at': plugin.loaded_at.isoformat() if plugin.loaded_at else None,
            'human_intervention': {
                'captcha': human_intervention.get('captcha', False),
                'mfa': human_intervention.get('mfa', False),
                'initial_setup': human_intervention.get('initial_setup', False)
            }
        }
    
    def list_plugins_by_category(self) -> Dict[str, List[str]]:
        """
        Group plugins by category.
        
        Returns:
            Dictionary of category -> list of plugin IDs
        """
        categories: Dict[str, List[str]] = {}
        
        for plugin_id, plugin in self.get_all_plugins().items():
            category = plugin.category
            if category not in categories:
                categories[category] = []
            categories[category].append(plugin_id)
        
        return categories


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
