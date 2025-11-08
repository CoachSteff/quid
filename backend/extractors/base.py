#!/usr/bin/env python3
"""
Base extractor interface for data extraction strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from playwright.async_api import Page


class ExtractionException(Exception):
    """Raised when data extraction fails."""
    pass


class BaseExtractor(ABC):
    """
    Abstract base class for data extraction strategies.
    
    Each extractor implements a specific extraction pattern
    (tables, articles, product listings, etc.)
    """
    
    def __init__(self, config: Dict):
        """
        Initialize extractor with configuration.
        
        Args:
            config: Extraction configuration from site YAML
        """
        self.config = config
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get extractor name/type.
        
        Returns:
            Extractor identifier (e.g., 'table', 'article')
        """
        pass
    
    @abstractmethod
    async def can_extract(self, page: Page) -> bool:
        """
        Check if this extractor can handle the current page.
        
        Args:
            page: Playwright Page object
            
        Returns:
            True if this extractor can extract data from this page
        """
        pass
    
    @abstractmethod
    async def extract(self, page: Page) -> List[Dict[str, Any]]:
        """
        Extract data from the page.
        
        Args:
            page: Playwright Page object
            
        Returns:
            List of extracted data records (each record is a dict)
            
        Raises:
            ExtractionException: If extraction fails
        """
        pass
