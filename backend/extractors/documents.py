#!/usr/bin/env python3
"""
Document links extractor - extracts downloadable document links and metadata.
Designed for EMIS portal to capture detail pages, PDFs, and other documents.
"""

import logging
from typing import Dict, List, Any
from playwright.async_api import Page

from .base import BaseExtractor, ExtractionException
from .registry import register_extractor

logger = logging.getLogger(__name__)


@register_extractor
class DocumentLinksExtractor(BaseExtractor):
    """
    Extracts document links and metadata from search results pages.
    
    Specifically designed for EMIS which uses:
    - Detail links: /detail?woId=XXX&woVersion=YYYY-MM-DD
    - PDF links: links containing .pdf
    - Download links: links with 'download' keyword
    
    Config structure:
    {
        "type": "documents",
        "link_selectors": [         # CSS selectors for document links
            "a[href*='detail']",
            "a[href*='.pdf']",
            "a[href*='download']"
        ],
        "extract_metadata": true,   # Extract link text, href, attributes
        "base_url": "https://..."   # Base URL for relative links
    }
    """
    
    def get_name(self) -> str:
        return "documents"
    
    async def can_extract(self, page: Page) -> bool:
        """Check if page contains document links."""
        link_selectors = self.config.get('link_selectors', [
            "a[href*='detail']",
            "a[href*='.pdf']",
            "a[href*='download']"
        ])
        
        try:
            # Check if any of the selectors match
            for selector in link_selectors:
                await page.wait_for_selector(selector, timeout=2000)
                elements = await page.query_selector_all(selector)
                if len(elements) > 0:
                    return True
            return False
        except:
            # Timeout or not found
            return False
    
    async def extract(self, page: Page) -> List[Dict[str, Any]]:
        """
        Extract document links and metadata from the page.
        
        Returns:
            List of document dictionaries with title, url, type, and metadata
        """
        link_selectors = self.config.get('link_selectors', [
            "a[href*='detail']",
            "a[href*='.pdf']",
            "a[href*='download']"
        ])
        base_url = self.config.get('base_url', page.url.split('?')[0].rsplit('/', 1)[0])
        
        try:
            documents = []
            seen_urls = set()  # Avoid duplicates
            
            for selector in link_selectors:
                try:
                    links = await page.query_selector_all(selector)
                    
                    for link in links:
                        try:
                            href = await link.get_attribute('href')
                            text = await link.inner_text()
                            text = text.strip()
                            
                            if not href or not text:
                                continue
                            
                            # Make absolute URL
                            if href.startswith('/'):
                                full_url = base_url.split('/')[0] + '//' + base_url.split('/')[2] + href
                            elif not href.startswith('http'):
                                full_url = base_url + '/' + href
                            else:
                                full_url = href
                            
                            # Skip if already seen
                            if full_url in seen_urls:
                                continue
                            seen_urls.add(full_url)
                            
                            # Determine document type
                            doc_type = 'unknown'
                            if 'detail' in href:
                                doc_type = 'detail_page'
                            elif '.pdf' in href:
                                doc_type = 'pdf'
                            elif 'download' in href:
                                doc_type = 'download'
                            
                            # Extract woId and version if present (EMIS-specific)
                            metadata = {}
                            if '?woId=' in href:
                                parts = href.split('?')[1].split('&')
                                for part in parts:
                                    if '=' in part:
                                        key, value = part.split('=', 1)
                                        metadata[key] = value
                            
                            documents.append({
                                'title': text,
                                'url': full_url,
                                'type': doc_type,
                                'metadata': metadata if metadata else None
                            })
                            
                        except Exception as e:
                            logger.debug(f"Failed to extract link: {e}")
                            continue
                    
                except Exception as e:
                    logger.debug(f"Failed to process selector '{selector}': {e}")
                    continue
            
            logger.info(f"Extracted {len(documents)} document links")
            return documents
            
        except Exception as e:
            logger.error(f"Document link extraction failed: {e}")
            raise ExtractionException(f"Failed to extract document links: {str(e)}")
