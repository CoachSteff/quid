#!/usr/bin/env python3
"""
Raw text extractor - fallback extractor that always succeeds.
Extracts plain text from the entire page body.
"""

import logging
from typing import Dict, List, Any
from playwright.async_api import Page

from .base import BaseExtractor, ExtractionException
from .registry import register_extractor

logger = logging.getLogger(__name__)


@register_extractor
class RawExtractor(BaseExtractor):
    """
    Raw text extractor - always available as fallback.
    
    Extracts the entire page body text when structured extraction fails.
    This ensures queries never fail with "no suitable extractor found".
    
    Config structure:
    {
        "type": "raw",
        "selector": "body",       # Element to extract (default: body)
        "max_length": 10000       # Limit text length (optional)
    }
    """
    
    def get_name(self) -> str:
        return "raw"
    
    async def can_extract(self, page: Page) -> bool:
        """
        Always returns True - this is a fallback extractor.
        
        Returns:
            True (always available)
        """
        return True
    
    async def extract(self, page: Page) -> List[Dict[str, Any]]:
        """
        Extract raw text from the page.
        
        Args:
            page: Playwright Page object
            
        Returns:
            List with single item containing raw page text
        """
        selector = self.config.get('selector', 'body')
        max_length = self.config.get('max_length', 10000)
        
        try:
            element = await page.query_selector(selector)
            
            if not element:
                logger.warning(f"Raw extractor: selector '{selector}' not found, using body")
                element = await page.query_selector('body')
            
            text = await element.inner_text()
            text = text.strip()
            
            # Truncate if too long
            if len(text) > max_length:
                logger.info(f"Raw text truncated from {len(text)} to {max_length} characters")
                text = text[:max_length] + "..."
            
            logger.info(f"Raw extractor: extracted {len(text)} characters")
            
            return [{
                "raw_text": text,
                "url": page.url,
                "title": await page.title(),
                "note": "Raw text extraction used (structured extraction unavailable)"
            }]
            
        except Exception as e:
            logger.error(f"Raw extraction failed: {e}")
            raise ExtractionException(f"Failed to extract raw text: {str(e)}")
