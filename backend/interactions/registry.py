"""
Handler registry for discovery and selection.

Manages available interaction handlers and selects
appropriate ones based on page state and priority.
"""

import logging
from typing import List, Type, Dict, Any
from playwright.async_api import Page

from .base import InteractionHandler, HandlerResult

logger = logging.getLogger(__name__)


class InteractionRegistry:
    """
    Registry for interaction handlers.
    
    Discovers handlers, manages their lifecycle, and selects
    appropriate handlers for current page state.
    """
    
    _handlers: List[Type[InteractionHandler]] = []
    
    @classmethod
    def register(cls, handler_class: Type[InteractionHandler]):
        """
        Register a handler class.
        
        Args:
            handler_class: Handler class to register
        """
        if handler_class not in cls._handlers:
            cls._handlers.append(handler_class)
            logger.debug(f"Registered handler: {handler_class.__name__}")
    
    @classmethod
    def get_handlers(cls, config: Dict[str, Any]) -> List[InteractionHandler]:
        """
        Get instantiated handlers for configuration.
        
        Args:
            config: Site configuration
            
        Returns:
            List of handler instances, sorted by priority
        """
        handlers = [handler_cls(config) for handler_cls in cls._handlers]
        handlers.sort(key=lambda h: h.priority())
        return handlers
    
    @classmethod
    async def handle_interactions(cls, page: Page, config: Dict[str, Any]) -> List[HandlerResult]:
        """
        Run all applicable handlers on the page.
        
        Args:
            page: Playwright page instance
            config: Site configuration
            
        Returns:
            List of results from handlers that were executed
        """
        results = []
        handlers = cls.get_handlers(config)
        
        for handler in handlers:
            try:
                if await handler.detect(page):
                    logger.info(f"Executing handler: {handler.name}")
                    result = await handler.handle(page)
                    results.append(result)
                    
                    if result.success:
                        logger.info(f"{handler.name}: {result.message}")
                    else:
                        logger.warning(f"{handler.name} failed: {result.message}")
            except Exception as e:
                logger.error(f"Handler {handler.name} error: {e}")
                results.append(HandlerResult(
                    success=False,
                    message=f"Exception: {str(e)}"
                ))
        
        return results


def register_handler(handler_class: Type[InteractionHandler]):
    """
    Decorator to register a handler class.
    
    Usage:
        @register_handler
        class MyHandler(InteractionHandler):
            ...
    """
    InteractionRegistry.register(handler_class)
    return handler_class
