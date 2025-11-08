"""
Popup and dialog handler.

Detects and dismisses common popup patterns:
- Cookie consent banners
- Modal dialogs
- Overlay notices
- Newsletter signups
"""

import logging
import asyncio
from typing import List, Dict, Any
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from ..base import InteractionHandler, HandlerResult
from ..registry import register_handler

logger = logging.getLogger(__name__)


@register_handler
class PopupHandler(InteractionHandler):
    """
    Handler for popup detection and dismissal.
    
    Supports:
    - Cookie consent banners
    - Modal overlays
    - Alert dialogs
    - Newsletter popups
    """
    
    # Default selectors for common popup patterns
    DEFAULT_POPUP_SELECTORS = [
        # Cookie consent
        '.cookie-banner button:has-text("Accept")',
        '.cookie-consent button:has-text("Accept")',
        '[class*="cookie"] button[class*="accept"]',
        '.vito--cookie button',
        'button:has-text("Aanvaarden")',
        
        # Generic modals
        '.modal .close',
        '[data-dismiss="modal"]',
        '.modal-close',
        
        # Overlays
        '.overlay .close',
        '.popup-close',
        
        # Newsletter/Subscription
        '.newsletter-popup .close',
        '[class*="newsletter"] button[class*="close"]',
    ]
    
    # Default backdrop/overlay selectors
    DEFAULT_BACKDROP_SELECTORS = [
        '.modal-backdrop',
        '.overlay',
        '[class*="backdrop"]',
    ]
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Get interaction config from site YAML
        self.interaction_config = config.get('interactions', {})
        self.popup_config = self.interaction_config.get('popups', {})
        
        # Enabled by default if config exists, otherwise opt-in
        self.enabled = self.popup_config.get('enabled', False)
        
        # Build selector list (site-specific + defaults)
        site_selectors = self.popup_config.get('selectors', [])
        self.selectors = site_selectors if site_selectors else self.DEFAULT_POPUP_SELECTORS
        
        # Auto-dismiss strategy
        self.auto_dismiss = self.popup_config.get('auto_dismiss', True)
        
        # Wait time after popup appears
        self.wait_after_appearance = self.popup_config.get('wait_after_appearance', 1000)
        
        # Wait time after dismissal
        self.wait_after_dismiss = self.popup_config.get('wait_after_dismiss', 500)
    
    def priority(self) -> int:
        """High priority - run before other interactions."""
        return 10
    
    async def detect(self, page: Page) -> bool:
        """
        Detect if any popups are present on the page.
        
        Returns:
            True if handler is enabled and popup detected
        """
        if not self.enabled:
            return False
        
        try:
            # Check if any popup selector matches
            for selector in self.selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        # Check if element is visible
                        is_visible = await element.is_visible()
                        if is_visible:
                            logger.debug(f"Detected popup with selector: {selector}")
                            return True
                except Exception as e:
                    logger.debug(f"Selector check failed for {selector}: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Popup detection error: {e}")
            return False
    
    async def handle(self, page: Page) -> HandlerResult:
        """
        Dismiss detected popups.
        
        Returns:
            HandlerResult with dismissal status
        """
        dismissed = []
        
        try:
            # Wait a bit for popup to fully appear
            await asyncio.sleep(self.wait_after_appearance / 1000)
            
            # Try each selector
            for selector in self.selectors:
                try:
                    # Wait for element to be visible
                    element = await page.wait_for_selector(
                        selector,
                        state="visible",
                        timeout=2000
                    )
                    
                    if element:
                        # Click to dismiss
                        await element.click(timeout=5000)
                        dismissed.append(selector)
                        logger.info(f"Dismissed popup: {selector}")
                        
                        # Wait after dismissal
                        await asyncio.sleep(self.wait_after_dismiss / 1000)
                        
                        # Only dismiss one popup at a time
                        break
                        
                except PlaywrightTimeoutError:
                    # Element not found or not clickable
                    continue
                except Exception as e:
                    logger.debug(f"Failed to dismiss with selector {selector}: {e}")
                    continue
            
            if dismissed:
                return HandlerResult(
                    success=True,
                    action_taken="dismissed_popup",
                    message=f"Dismissed popup using: {dismissed[0]}",
                    metadata={"selectors": dismissed}
                )
            else:
                return HandlerResult(
                    success=False,
                    message="No popup could be dismissed"
                )
                
        except Exception as e:
            return HandlerResult(
                success=False,
                message=f"Error dismissing popup: {str(e)}"
            )
