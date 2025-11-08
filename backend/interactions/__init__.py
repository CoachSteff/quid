"""
UI Interaction Subagent Module

Provides handlers for common web UI interaction patterns:
- Popup/dialog dismissal
- Cookie consent handling
- Modal overlays
- Form filling (future)
"""

from .base import InteractionHandler, HandlerResult
from .registry import InteractionRegistry

__all__ = ['InteractionHandler', 'HandlerResult', 'InteractionRegistry']
