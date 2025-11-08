"""Authentication strategies for web scraping."""

from .base import (
    AuthStrategy,
    AuthenticationException,
    LoginFailedException,
    SessionExpiredException
)

__all__ = [
    'AuthStrategy',
    'AuthenticationException',
    'LoginFailedException',
    'SessionExpiredException'
]
