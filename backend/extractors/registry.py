#!/usr/bin/env python3
"""
Extractor registry for automatic discovery and selection of extractors.
"""

import logging
from typing import Dict, List, Type
from playwright.async_api import Page

from .base import BaseExtractor

logger = logging.getLogger(__name__)


class ExtractorRegistry:
    """
    Registry for managing and selecting extractors.
    
    Automatically discovers and selects appropriate extractor
    based on page content and configuration.
    """
    
    def __init__(self):
        self._extractors: Dict[str, Type[BaseExtractor]] = {}
    
    def register(self, extractor_class: Type[BaseExtractor]):
        """
        Register an extractor class.
        
        Args:
            extractor_class: Class that inherits from BaseExtractor
        """
        # Instantiate temporarily to get name
        temp_instance = extractor_class({})
        name = temp_instance.get_name()
        
        self._extractors[name] = extractor_class
        logger.info(f"Registered extractor: {name}")
    
    def get_extractor(self, extractor_type: str, config: Dict) -> BaseExtractor:
        """
        Get an extractor instance by type.
        
        Args:
            extractor_type: Type of extractor (e.g., 'table', 'article')
            config: Configuration for the extractor
            
        Returns:
            Extractor instance
            
        Raises:
            ValueError: If extractor type not found
        """
        extractor_class = self._extractors.get(extractor_type)
        
        if not extractor_class:
            available = ', '.join(self._extractors.keys())
            raise ValueError(f"Unknown extractor type '{extractor_type}'. Available: {available}")
        
        return extractor_class(config)
    
    async def select_extractor(self, page: Page, strategies: List[Dict]) -> BaseExtractor:
        """
        Automatically select best extractor for the page.
        
        Args:
            page: Playwright Page object
            strategies: List of extraction strategy configs to try
            
        Returns:
            First extractor that can handle the page
            
        Raises:
            ValueError: If no suitable extractor found
        """
        for strategy in strategies:
            extractor_type = strategy.get('type')
            if not extractor_type:
                continue
            
            try:
                extractor = self.get_extractor(extractor_type, strategy)
                
                if await extractor.can_extract(page):
                    logger.info(f"Selected extractor: {extractor_type}")
                    return extractor
                    
            except Exception as e:
                logger.warning(f"Error checking extractor '{extractor_type}': {e}")
                continue
        
        raise ValueError("No suitable extractor found for this page")
    
    def list_extractors(self) -> List[str]:
        """
        Get list of registered extractor names.
        
        Returns:
            List of extractor type names
        """
        return list(self._extractors.keys())


# Global registry instance
_global_registry = ExtractorRegistry()


def get_registry() -> ExtractorRegistry:
    """Get the global extractor registry."""
    return _global_registry


def register_extractor(extractor_class: Type[BaseExtractor]):
    """
    Decorator to register an extractor class.
    
    Usage:
        @register_extractor
        class MyExtractor(BaseExtractor):
            ...
    """
    _global_registry.register(extractor_class)
    return extractor_class
