"""
Base classes for interaction handlers.

Defines the interface that all handlers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from playwright.async_api import Page


@dataclass
class HandlerResult:
    """Result of an interaction handler execution."""
    success: bool
    action_taken: Optional[str] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class InteractionHandler(ABC):
    """
    Base class for all UI interaction handlers.
    
    Handlers detect and respond to common UI patterns like
    popups, modals, cookie consents, etc.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize handler with configuration.
        
        Args:
            config: Site-specific configuration from YAML
        """
        self.config = config
    
    @abstractmethod
    async def detect(self, page: Page) -> bool:
        """
        Check if this handler can process the current page state.
        
        Args:
            page: Playwright page instance
            
        Returns:
            True if handler should be invoked
        """
        pass
    
    @abstractmethod
    async def handle(self, page: Page) -> HandlerResult:
        """
        Execute the interaction.
        
        Args:
            page: Playwright page instance
            
        Returns:
            HandlerResult with success status and details
        """
        pass
    
    @abstractmethod
    def priority(self) -> int:
        """
        Handler priority (lower number = higher priority).
        
        Returns:
            Priority value (0-100, default 50)
        """
        pass
    
    @property
    def name(self) -> str:
        """Handler name for logging."""
        return self.__class__.__name__
