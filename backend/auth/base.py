#!/usr/bin/env python3
"""
Base authentication strategy interface.
Defines the contract for all authentication implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from playwright.async_api import Page, BrowserContext


class AuthenticationException(Exception):
    """Raised when authentication fails."""
    pass


class LoginFailedException(AuthenticationException):
    """Raised when login explicitly fails (wrong credentials, captcha, etc.)."""
    pass


class SessionExpiredException(AuthenticationException):
    """Raised when an existing session has expired."""
    pass


class AuthStrategy(ABC):
    """
    Abstract base class for authentication strategies.
    
    Each strategy implements a specific authentication pattern
    (form-based, OAuth, API tokens, cookies, etc.)
    """
    
    def __init__(self, config: Dict, credentials: Dict):
        """
        Initialize auth strategy with configuration and credentials.
        
        Args:
            config: Authentication configuration from site YAML
            credentials: User credentials (email, password, tokens, etc.)
        """
        self.config = config
        self.credentials = credentials
    
    @abstractmethod
    async def login(self, page: Page, context: BrowserContext) -> bool:
        """
        Perform authentication and establish session.
        
        Args:
            page: Playwright Page object
            context: Playwright BrowserContext for session persistence
            
        Returns:
            True if login successful
            
        Raises:
            LoginFailedException: If login fails
            AuthenticationException: For other auth errors
        """
        pass
    
    @abstractmethod
    async def validate_session(self, page: Page) -> bool:
        """
        Check if current session is valid (user is logged in).
        
        Args:
            page: Playwright Page object
            
        Returns:
            True if session is valid and user is authenticated
        """
        pass
    
    async def logout(self, page: Page) -> bool:
        """
        Optional: Perform logout (if supported by the site).
        
        Args:
            page: Playwright Page object
            
        Returns:
            True if logout successful
        """
        # Default implementation: no-op
        return True
    
    def requires_credentials(self) -> bool:
        """
        Check if this auth strategy requires user credentials.
        
        Returns:
            True if credentials are required (default)
        """
        return True
