#!/usr/bin/env python3
"""
No authentication strategy.
For public websites that don't require any authentication.
"""

import logging
from typing import Dict
from playwright.async_api import Page, BrowserContext

from ..base import AuthStrategy

logger = logging.getLogger(__name__)


class NoneAuth(AuthStrategy):
    """
    No authentication required.
    
    Used for public websites that don't require login or API keys.
    
    Config structure:
    {
        "scenario": "none",
        "type": "none"
    }
    """
    
    def __init__(self, config: Dict, credentials: Dict, full_site_config: Dict = None):
        """
        Initialize none auth strategy.
        
        Args:
            config: Authentication configuration from site YAML
            credentials: User credentials (not used)
            full_site_config: Full site configuration
        """
        super().__init__(config, credentials)
        self.full_site_config = full_site_config or config
    
    async def login(self, page: Page, context: BrowserContext) -> bool:
        """
        No-op login for public sites.
        
        Args:
            page: Playwright Page
            context: Browser context
            
        Returns:
            True (always successful)
        """
        logger.info("No authentication required - public website")
        return True
    
    async def validate_session(self, page: Page) -> bool:
        """
        Validate session for public sites.
        
        Args:
            page: Playwright Page
            
        Returns:
            True (always valid for public sites)
        """
        logger.debug("No authentication validation needed - public website")
        return True
