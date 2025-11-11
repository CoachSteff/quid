#!/usr/bin/env python3
"""
Site configuration loader.
Loads and validates site definitions from YAML files.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
import yaml

logger = logging.getLogger(__name__)


class ConfigurationException(Exception):
    """Raised when site configuration is invalid."""
    pass


class SiteConfigLoader:
    """
    Loads site configurations from YAML files.
    
    Config files are located in the 'sites/' directory.
    Each site has its own YAML file (e.g., sites/emis.yaml).
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize config loader.
        
        Args:
            config_dir: Directory containing site config files (default: sites/)
        """
        default_dir = os.getenv("SITES_CONFIG_DIR", "sites")
        self.config_dir = Path(config_dir or default_dir)
        
        if not self.config_dir.exists():
            logger.warning(f"Config directory does not exist: {self.config_dir}")
            self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Site config directory: {self.config_dir}")
        
        # Cache loaded configs
        self._configs: Dict[str, Dict] = {}
    
    def load_site(self, site_id: str) -> Dict:
        """
        Load site configuration by ID.
        
        Checks plugins first, then falls back to legacy site configs.
        
        Args:
            site_id: Site identifier (e.g., 'emis')
            
        Returns:
            Site configuration dict
            
        Raises:
            ConfigurationException: If config file not found or invalid
        """
        # Check cache first
        if site_id in self._configs:
            return self._configs[site_id]
        
        # Check plugin first (for backwards compatibility)
        try:
            from .plugin_manager import get_plugin_manager
            plugin_manager = get_plugin_manager()
            plugin = plugin_manager.get_plugin(site_id)
            if plugin and plugin.enabled:
                # Cache plugin config
                self._configs[site_id] = plugin.config
                logger.info(f"Loaded site config from plugin: {site_id}")
                return plugin.config
        except (ImportError, FileNotFoundError, Exception) as e:
            # Plugin not found or not available, continue to legacy config
            logger.debug(f"Plugin '{site_id}' not found, trying legacy config: {e}")
        
        # Fallback to legacy YAML file
        config_file = self.config_dir / f"{site_id}.yaml"
        
        if not config_file.exists():
            # Try .yml extension
            config_file = self.config_dir / f"{site_id}.yml"
        
        if not config_file.exists():
            available = self.list_sites()
            raise ConfigurationException(
                f"Site config not found: {site_id}. "
                f"Available sites: {', '.join(available) if available else 'none'}"
            )
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate config structure
            self._validate_config(site_id, config)
            
            # Cache it
            self._configs[site_id] = config
            
            logger.info(f"Loaded site config: {site_id}")
            return config
            
        except yaml.YAMLError as e:
            raise ConfigurationException(f"Failed to parse YAML for site '{site_id}': {str(e)}")
        except Exception as e:
            raise ConfigurationException(f"Failed to load config for site '{site_id}': {str(e)}")
    
    def _validate_config(self, site_id: str, config: Dict):
        """
        Validate site configuration structure.
        
        Args:
            site_id: Site identifier
            config: Configuration dict to validate
            
        Raises:
            ConfigurationException: If config is invalid
        """
        required_fields = ['site_id', 'name', 'base_url']
        
        for field in required_fields:
            if field not in config:
                raise ConfigurationException(
                    f"Site config '{site_id}' missing required field: {field}"
                )
        
        # Verify site_id matches filename
        if config['site_id'] != site_id:
            raise ConfigurationException(
                f"Site ID mismatch: filename '{site_id}' vs config '{config['site_id']}'"
            )
        
        # Validate auth section
        if 'auth' in config:
            auth_config = config['auth']
            
            if 'type' not in auth_config:
                raise ConfigurationException(
                    f"Site config '{site_id}' auth section missing 'type' field"
                )
            
            auth_type = auth_config['type']
            
            # Validate based on auth type
            if auth_type == 'form_based':
                if 'login_url' not in auth_config:
                    raise ConfigurationException(
                        f"Site config '{site_id}' form_based auth missing 'login_url'"
                    )
        
        # Validate extraction section
        if 'extraction' in config:
            extraction = config['extraction']
            
            if 'strategies' not in extraction:
                raise ConfigurationException(
                    f"Site config '{site_id}' extraction section missing 'strategies'"
                )
            
            if not isinstance(extraction['strategies'], list):
                raise ConfigurationException(
                    f"Site config '{site_id}' extraction strategies must be a list"
                )
            
            for idx, strategy in enumerate(extraction['strategies']):
                if 'type' not in strategy:
                    raise ConfigurationException(
                        f"Site config '{site_id}' extraction strategy {idx} missing 'type'"
                    )
    
    def list_sites(self) -> List[str]:
        """
        List all available site configurations.
        
        Returns:
            List of site IDs
        """
        if not self.config_dir.exists():
            return []
        
        sites = []
        
        for config_file in self.config_dir.glob("*.yaml"):
            site_id = config_file.stem
            sites.append(site_id)
        
        for config_file in self.config_dir.glob("*.yml"):
            site_id = config_file.stem
            if site_id not in sites:
                sites.append(site_id)
        
        return sorted(sites)
    
    def reload_site(self, site_id: str) -> Dict:
        """
        Reload a site configuration (clear cache and reload).
        
        Args:
            site_id: Site identifier
            
        Returns:
            Reloaded site configuration
        """
        if site_id in self._configs:
            del self._configs[site_id]
        
        return self.load_site(site_id)
    
    def get_site_info(self, site_id: str) -> Dict:
        """
        Get basic site information without full config.
        
        Args:
            site_id: Site identifier
            
        Returns:
            Dict with site_id, name, and description
        """
        config = self.load_site(site_id)
        
        return {
            'site_id': config.get('site_id'),
            'name': config.get('name'),
            'description': config.get('description', ''),
            'base_url': config.get('base_url')
        }


# Global config loader instance
_global_loader = None


def get_config_loader() -> SiteConfigLoader:
    """Get the global config loader instance."""
    global _global_loader
    if _global_loader is None:
        _global_loader = SiteConfigLoader()
    return _global_loader
