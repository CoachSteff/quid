#!/usr/bin/env python3
"""
Credential manager for per-site authentication.
Supports multiple credential sources with priority ordering.
"""

import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class CredentialManager:
    """
    Manages credentials for multiple sites.
    
    Priority order:
    1. Environment variables (per-site: {SITE_ID}_EMAIL, {SITE_ID}_PASSWORD)
    2. Environment variables (generic: EMIS_EMAIL, EMIS_PASSWORD for backwards compat)
    3. Hardcoded fallbacks (for development)
    
    Future: Could add secrets manager integration (AWS Secrets, Vault, etc.)
    """
    
    def __init__(self):
        self._fallbacks: Dict[str, Dict[str, str]] = {}
    
    def register_fallback(self, site_id: str, credentials: Dict[str, str]):
        """
        Register hardcoded fallback credentials for a site.
        
        Args:
            site_id: Site identifier
            credentials: Dict with credential keys (email, password, etc.)
        """
        self._fallbacks[site_id] = credentials
        logger.info(f"Registered fallback credentials for site: {site_id}")
    
    def get_credentials(self, site_id: str) -> Dict[str, str]:
        """
        Get credentials for a site.
        
        Args:
            site_id: Site identifier
            
        Returns:
            Dict with credentials (email, password, api_key, etc.)
        """
        credentials = {}
        
        # Try per-site environment variables first
        site_id_upper = site_id.upper()
        
        email_key = f"{site_id_upper}_EMAIL"
        password_key = f"{site_id_upper}_PASSWORD"
        username_key = f"{site_id_upper}_USERNAME"
        api_key_key = f"{site_id_upper}_API_KEY"
        
        email = os.getenv(email_key)
        password = os.getenv(password_key)
        username = os.getenv(username_key)
        api_key = os.getenv(api_key_key)
        
        # For backwards compatibility with EMIS, also check EMIS_* vars
        if not email and site_id == 'emis':
            email = os.getenv('EMIS_EMAIL')
        if not password and site_id == 'emis':
            password = os.getenv('EMIS_PASSWORD')
        
        # Use environment variables if available
        if email:
            credentials['email'] = email
            logger.info(f"Using {email_key} from environment")
        if password:
            credentials['password'] = password
        if username:
            credentials['username'] = username
            logger.info(f"Using {username_key} from environment")
        if api_key:
            credentials['api_key'] = api_key
            logger.info(f"Using {api_key_key} from environment")
        
        # If no credentials from environment, use fallback
        if not credentials and site_id in self._fallbacks:
            credentials = self._fallbacks[site_id].copy()
            logger.info(f"Using fallback credentials for site: {site_id}")
        
        return credentials
    
    def has_credentials(self, site_id: str) -> bool:
        """
        Check if credentials are available for a site.
        
        Args:
            site_id: Site identifier
            
        Returns:
            True if credentials are available
        """
        credentials = self.get_credentials(site_id)
        return bool(credentials)
    
    def validate_credentials(self, site_id: str, required_fields: list) -> bool:
        """
        Validate that all required credential fields are present.
        
        Args:
            site_id: Site identifier
            required_fields: List of required field names
            
        Returns:
            True if all required fields are present
        """
        credentials = self.get_credentials(site_id)
        
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                logger.warning(f"Missing required credential field '{field}' for site: {site_id}")
                return False
        
        return True


# Global credential manager instance
_global_manager = None


def get_credential_manager() -> CredentialManager:
    """Get the global credential manager instance."""
    global _global_manager
    if _global_manager is None:
        _global_manager = CredentialManager()
    return _global_manager
