#!/usr/bin/env python3
"""
API Key authentication strategy.
Handles authentication via API keys in headers, query parameters, or bearer tokens.
"""

import logging
from typing import Dict
from playwright.async_api import Page, BrowserContext, Route

from ..base import AuthStrategy, LoginFailedException

logger = logging.getLogger(__name__)


class APIKeyAuth(AuthStrategy):
    """
    Authentication via API key.
    
    Supports:
    - Header-based API keys (X-API-Key, Authorization, custom headers)
    - Query parameter API keys (?api_key=xxx)
    - Bearer token authentication (Authorization: Bearer xxx)
    
    Config structure:
    {
        "scenario": "api_key",
        "type": "api_key",
        "method": "header",  # header|query_param|bearer
        "key_name": "X-API-Key",  # Header name or query param name
        "key_location": "header",  # header|query
        "credential_env_var": "MY_SITE_API_KEY"  # Environment variable name
    }
    """
    
    def __init__(self, config: Dict, credentials: Dict, full_site_config: Dict = None):
        """
        Initialize API key auth strategy.
        
        Args:
            config: Authentication configuration from site YAML
            credentials: User credentials (should contain 'api_key')
            full_site_config: Full site configuration
        """
        super().__init__(config, credentials)
        self.full_site_config = full_site_config or config
        
        self.method = config.get('method', 'header')
        self.key_name = config.get('key_name', 'X-API-Key')
        self.key_location = config.get('key_location', 'header')
        
        # Get API key from credentials
        self.api_key = credentials.get('api_key')
        if not self.api_key:
            raise LoginFailedException("API key not found in credentials")
    
    async def login(self, page: Page, context: BrowserContext) -> bool:
        """
        Set up API key authentication.
        
        For browser-based access, this intercepts requests and adds the API key.
        For API-only access, the key is added to request headers.
        
        Args:
            page: Playwright Page
            context: Browser context
            
        Returns:
            True if setup successful
        """
        logger.info(f"Setting up API key authentication (method: {self.method})")
        
        # Set up request interception to add API key
        if self.method == 'bearer' or (self.method == 'header' and self.key_name.lower() == 'authorization'):
            # Bearer token authentication
            await self._setup_bearer_auth(context)
        elif self.method == 'header' or self.key_location == 'header':
            # Header-based API key
            await self._setup_header_auth(context)
        elif self.method == 'query_param' or self.key_location == 'query':
            # Query parameter API key
            await self._setup_query_param_auth(context)
        else:
            raise LoginFailedException(f"Unsupported API key method: {self.method}")
        
        logger.info("API key authentication configured")
        return True
    
    async def _setup_bearer_auth(self, context: BrowserContext):
        """Set up Bearer token authentication."""
        async def add_bearer_token(route: Route):
            headers = await route.request.headers
            headers['Authorization'] = f'Bearer {self.api_key}'
            await route.continue_(headers=headers)
        
        await context.route('**/*', add_bearer_token)
        logger.debug("Bearer token authentication configured")
    
    async def _setup_header_auth(self, context: BrowserContext):
        """Set up header-based API key authentication."""
        async def add_api_key_header(route: Route):
            headers = await route.request.headers
            headers[self.key_name] = self.api_key
            await route.continue_(headers=headers)
        
        await context.route('**/*', add_api_key_header)
        logger.debug(f"Header authentication configured: {self.key_name}")
    
    async def _setup_query_param_auth(self, context: BrowserContext):
        """Set up query parameter API key authentication."""
        async def add_api_key_param(route: Route):
            url = route.request.url
            separator = '&' if '?' in url else '?'
            new_url = f"{url}{separator}{self.key_name}={self.api_key}"
            await route.continue_(url=new_url)
        
        await context.route('**/*', add_api_key_param)
        logger.debug(f"Query parameter authentication configured: {self.key_name}")
    
    async def validate_session(self, page: Page) -> bool:
        """
        Validate API key session.
        
        For API key auth, the session is always valid as long as the key is present.
        Actual validation happens on each request.
        
        Args:
            page: Playwright Page
            
        Returns:
            True (API keys don't expire in the traditional sense)
        """
        logger.debug("API key session validation - always valid")
        return True
