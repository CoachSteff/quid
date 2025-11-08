#!/usr/bin/env python3
"""
Generic content extractor for text-based content.
Extracts structured or unstructured text from pages.
"""

import logging
from typing import Dict, List, Any
from playwright.async_api import Page

from .base import BaseExtractor, ExtractionException
from .registry import register_extractor

logger = logging.getLogger(__name__)


@register_extractor
class ContentExtractor(BaseExtractor):
    """
    Extracts text content from pages.
    
    Config structure:
    {
        "type": "content",
        "selector": "main.content",  # Main content container
        "fields": {                  # Optional: Extract specific fields
            "title": "h1",
            "description": ".description",
            "items": ".item"         # Extracts multiple items
        },
        "max_length": 5000          # Limit text length
    }
    """
    
    def get_name(self) -> str:
        return "content"
    
    async def can_extract(self, page: Page) -> bool:
        """Check if page has content to extract."""
        selector = self.config.get('selector', 'main, article, .content, #content')
        
        try:
            element = await page.query_selector(selector)
            return element is not None
        except:
            return False
    
    async def extract(self, page: Page) -> List[Dict[str, Any]]:
        """
        Extract content from the page.
        
        Returns:
            List with extracted content (single item if no fields, multiple if using 'items' field)
        """
        selector = self.config.get('selector', 'main, article, .content, #content')
        fields = self.config.get('fields', {})
        max_length = self.config.get('max_length', 5000)
        
        try:
            # If fields are specified, extract structured data
            if fields:
                return await self._extract_structured(page, selector, fields, max_length)
            else:
                return await self._extract_text(page, selector, max_length)
                
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            raise ExtractionException(f"Failed to extract content: {str(e)}")
    
    async def _extract_text(self, page: Page, selector: str, max_length: int) -> List[Dict[str, Any]]:
        """Extract plain text content."""
        try:
            element = await page.query_selector(selector)
            
            if not element:
                logger.warning(f"No content found with selector: {selector}")
                return []
            
            text = await element.inner_text()
            text = text.strip()
            
            # Truncate if too long
            if len(text) > max_length:
                text = text[:max_length] + "..."
                logger.info(f"Content truncated to {max_length} characters")
            
            return [{"content": text}]
            
        except Exception as e:
            logger.warning(f"Failed to extract text content: {e}")
            return []
    
    async def _extract_structured(self, page: Page, selector: str, fields: Dict, max_length: int) -> List[Dict[str, Any]]:
        """Extract structured data based on field selectors."""
        results = []
        
        try:
            # Check if 'items' field exists (multiple items)
            if 'items' in fields:
                items_selector = fields['items']
                items = await page.query_selector_all(items_selector)
                
                logger.info(f"Found {len(items)} items with selector: {items_selector}")
                
                # Extract data from each item
                for item in items:
                    item_data = {}
                    
                    for field_name, field_selector in fields.items():
                        if field_name == 'items':
                            continue
                        
                        try:
                            # Find element within item
                            field_element = await item.query_selector(field_selector)
                            if field_element:
                                text = await field_element.inner_text()
                                item_data[field_name] = text.strip()
                        except:
                            item_data[field_name] = ""
                    
                    if item_data:
                        results.append(item_data)
                
            else:
                # Single item with multiple fields
                item_data = {}
                
                for field_name, field_selector in fields.items():
                    try:
                        field_element = await page.query_selector(field_selector)
                        if field_element:
                            text = await field_element.inner_text()
                            item_data[field_name] = text.strip()[:max_length]
                    except:
                        item_data[field_name] = ""
                
                if item_data:
                    results.append(item_data)
            
            logger.info(f"Extracted {len(results)} structured content items")
            return results
            
        except Exception as e:
            logger.warning(f"Failed to extract structured content: {e}")
            return []
