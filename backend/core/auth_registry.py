#!/usr/bin/env python3
"""
Authentication Strategy Registry for Quid MCP.
Manages registration and retrieval of authentication strategies.
"""

import logging
from typing import Dict, Type, Optional

try:
    from ..auth.base import AuthStrategy
except ImportError:
    # Fallback for when running as script or from tests
    from auth.base import AuthStrategy

logger = logging.getLogger(__name__)


class AuthRegistry:
    """
    Registry for authentication strategies.
    
    Maps authentication scenario names to strategy classes.
    Allows plugins to specify their auth needs declaratively.
    """
    
    _strategies: Dict[str, Type[AuthStrategy]] = {}
    
    @classmethod
    def register(cls, scenario: str, strategy_class: Type[AuthStrategy]):
        """
        Register an authentication strategy.
        
        Args:
            scenario: Scenario name (e.g., 'simple_form', 'api_key')
            strategy_class: AuthStrategy subclass
        """
        if scenario in cls._strategies:
            logger.warning(f"Overwriting existing auth strategy: {scenario}")
        
        cls._strategies[scenario] = strategy_class
        logger.debug(f"Registered auth strategy: {scenario} -> {strategy_class.__name__}")
    
    @classmethod
    def get(cls, scenario: str) -> Optional[Type[AuthStrategy]]:
        """
        Get an authentication strategy by scenario name.
        
        Args:
            scenario: Scenario name
            
        Returns:
            AuthStrategy class or None if not found
        """
        strategy = cls._strategies.get(scenario)
        if not strategy:
            logger.warning(f"Auth strategy not found: {scenario}")
        return strategy
    
    @classmethod
    def list_scenarios(cls) -> list:
        """
        List all registered authentication scenarios.
        
        Returns:
            List of scenario names
        """
        return list(cls._strategies.keys())
    
    @classmethod
    def is_registered(cls, scenario: str) -> bool:
        """Check if a scenario is registered."""
        return scenario in cls._strategies


def register_auth_strategy(scenario: str):
    """
    Decorator to register an authentication strategy.
    
    Usage:
        @register_auth_strategy('simple_form')
        class FormBasedAuth(AuthStrategy):
            ...
    """
    def decorator(strategy_class: Type[AuthStrategy]):
        AuthRegistry.register(scenario, strategy_class)
        return strategy_class
    return decorator


# Import and register built-in strategies
def _register_builtin_strategies():
    """Register all built-in authentication strategies."""
    try:
        from auth.strategies.form_based import FormBasedAuth
        AuthRegistry.register('simple_form', FormBasedAuth)
        AuthRegistry.register('form_based', FormBasedAuth)  # Legacy compatibility
        logger.info("Registered form-based authentication strategy")
    except ImportError as e:
        logger.warning(f"Failed to import form_based auth strategy: {e}")
    
    # API key strategy (to be implemented)
    try:
        from auth.strategies.api_key import APIKeyAuth
        AuthRegistry.register('api_key', APIKeyAuth)
        logger.info("Registered API key authentication strategy")
    except ImportError as e:
        logger.debug(f"API key auth strategy not available: {e}")
    
    # OAuth 2.0 strategy (to be implemented)
    try:
        from auth.strategies.oauth2 import OAuth2Auth
        AuthRegistry.register('oauth2', OAuth2Auth)
        logger.info("Registered OAuth 2.0 authentication strategy")
    except ImportError as e:
        logger.debug(f"OAuth 2.0 auth strategy not available: {e}")
    
    # CAPTCHA strategy (to be implemented)
    try:
        from auth.strategies.captcha import CaptchaAuth
        AuthRegistry.register('captcha', CaptchaAuth)
        logger.info("Registered CAPTCHA authentication strategy")
    except ImportError as e:
        logger.debug(f"CAPTCHA auth strategy not available: {e}")
    
    # MFA strategy (to be implemented)
    try:
        from auth.strategies.mfa import MFAAuth
        AuthRegistry.register('mfa', MFAAuth)
        logger.info("Registered MFA authentication strategy")
    except ImportError as e:
        logger.debug(f"MFA auth strategy not available: {e}")
    
    # None strategy (no auth required)
    try:
        from auth.strategies.none_auth import NoneAuth
        AuthRegistry.register('none', NoneAuth)
        logger.info("Registered 'none' authentication strategy")
    except ImportError as e:
        logger.debug(f"'None' auth strategy not available: {e}")


# Auto-register built-in strategies on module import
_register_builtin_strategies()
