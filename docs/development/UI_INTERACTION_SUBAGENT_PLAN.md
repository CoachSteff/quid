# UI Interaction Subagent Development Plan

**Date:** November 6, 2025  
**Version:** 1.0  
**Status:** Planning Phase

---

## Executive Summary

### Problem Statement

Current web scraping implementation faces common UI interaction challenges:

1. **Cookie Consent Popups** - Block interactions (as seen with EMIS portal)
2. **Modal Dialogs** - Prevent access to underlying content
3. **Notification Toasts** - Can interfere with element detection
4. **Newsletter Signups** - Overlay forms that must be dismissed
5. **Form Filling Complexity** - Various field types and validation patterns

**Current State:** Popup/dialog handling is hardcoded in individual auth strategies, leading to:
- Code duplication across strategies
- Difficult to maintain and test
- Cannot be reused for non-auth interactions
- Site-specific logic mixed with generic logic

### Proposed Solution

Create a **UI Interaction Subagent** module that:
- Detects and handles common UI interaction patterns automatically
- Follows the existing framework's strategy pattern (like auth/extractors)
- Is configurable per-site via YAML
- Can be invoked at strategic points in the scraper lifecycle
- Provides reusable handlers for common patterns

### Benefits

**For Maintainability:**
- Centralized interaction logic
- Easy to add new interaction patterns
- Clear separation of concerns
- Follows existing architectural patterns

**For Reliability:**
- Consistent handling across all sites
- Better error handling and logging
- Priority-based handler selection
- Opt-in to prevent breaking existing flows

**For Extensibility:**
- Plugin architecture for new handlers
- Site-specific configuration overrides
- Easy to test in isolation
- Foundation for advanced features (AI-based field interpretation)

---

## Architecture Design

### Overview

The UI Interaction Subagent follows the same architectural patterns as existing framework components:

```
backend/interactions/
├── __init__.py
├── base.py              # Abstract base classes
├── registry.py          # Handler discovery and selection
└── handlers/
    ├── __init__.py
    ├── popup_handler.py # Phase 1: Popup/dialog handling
    └── form_filler.py   # Phase 2: Intelligent form filling
```

### Design Principles

1. **Strategy Pattern** - Like auth strategies and extractors
2. **Registry Pattern** - Auto-discovery of handlers
3. **Priority-Based Selection** - Handlers declare their priority
4. **Configuration-Driven** - Site-specific YAML configs
5. **Fail-Safe** - Never break scraping flow if handler fails
6. **Opt-In Initially** - Must be enabled in site config

### Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GenericScraper                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Navigation/Auth Flow                               │ │
│  │    ↓                                                │ │
│  │  _handle_interactions() ←──────────────────────────┼─┤
│  │    ↓                                                │ │
│  │  InteractionRegistry.get_handlers()                │ │
│  │    ↓                                                │ │
│  │  [PopupHandler, FormFiller, ...]                   │ │
│  │    ↓                                                │ │
│  │  handler.detect() → handler.handle()               │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 1: Popup Handler (MVP)

### Scope

**Included in Phase 1:**
- Cookie consent detection and handling
- Modal dialog dismissal
- Overlay/backdrop detection
- Common popup patterns (accept/dismiss/close)
- Site-specific selector configuration
- Logging of dismissed popups

**Excluded from Phase 1:**
- Form filling (Phase 2)
- AI-based content interpretation
- Multi-language detection (use selectors)
- Complex interaction flows

### File Structure

```
backend/interactions/
├── __init__.py
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

├── base.py
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

├── registry.py
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

└── handlers/popup_handler.py
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
        '.vito--cookie button',  # EMIS-specific
        'button:has-text("Aanvaarden")',  # Dutch "Accept"
        
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
```

### Configuration Schema

Site YAML configuration extension:

```yaml
# In sites/emis.yaml or any site config

interactions:
  # Popup handler configuration
  popups:
    enabled: true  # Enable popup handler
    auto_dismiss: true  # Automatically dismiss when detected
    wait_after_appearance: 1000  # ms to wait after popup appears
    wait_after_dismiss: 500      # ms to wait after dismissal
    
    # Site-specific selectors (optional)
    # If not specified, uses default patterns
    selectors:
      - '.vito--cookie button'
      - 'button:has-text("Aanvaarden")'
      - '.modal .close-button'
      - '[data-dismiss="modal"]'
    
    # Strategy (optional)
    strategy: first_match  # first_match | all | priority
    
    # Max retries (optional)
    max_retries: 3
    
    # Timeout per attempt (optional)
    timeout_ms: 5000
```

### Integration into GenericScraper

Modify `backend/core/scraper.py`:

```python
from interactions.registry import InteractionRegistry

class GenericScraper:
    # ... existing code ...
    
    async def _handle_interactions(self, page: Page) -> None:
        """
        Handle common UI interactions (popups, modals, etc.).
        
        Called at strategic points in the scraping flow:
        - After page navigation
        - Before authentication
        - Before form interactions
        """
        try:
            results = await InteractionRegistry.handle_interactions(
                page,
                self.config
            )
            
            # Log results
            for result in results:
                if result.success:
                    self.logger.debug(f"Interaction handled: {result.message}")
                else:
                    self.logger.warning(f"Interaction failed: {result.message}")
                    
        except Exception as e:
            self.logger.error(f"Interaction handling error: {e}")
            # Never fail the scraping flow due to interaction handling
    
    async def _authenticate(self):
        """Authenticate with the site (with interaction handling)."""
        # ... existing auth code ...
        
        # After navigation, handle popups
        await self._handle_interactions(page)
        
        # Then proceed with authentication
        # ... rest of auth code ...
    
    async def _perform_search(self, query: str):
        """Perform search (with interaction handling)."""
        # ... navigate to search page ...
        
        # Handle any popups before search
        await self._handle_interactions(page)
        
        # ... rest of search code ...
```

### Testing Strategy

**Test Cases:**

1. **Cookie Consent**
   - Test with EMIS portal
   - Verify cookie banner is detected
   - Verify click action succeeds
   - Verify page is interactable after dismissal

2. **Modal Dialogs**
   - Create test page with modal
   - Verify detection
   - Verify dismissal

3. **Multiple Popups**
   - Test priority-based handling
   - Verify only highest priority runs

4. **Non-Interference**
   - Test sites without popups
   - Verify no false positives
   - Verify scraping flow continues normally

5. **Error Handling**
   - Test with invalid selectors
   - Verify graceful failure
   - Verify scraping continues

**Test Implementation:**

```bash
# Manual testing with EMIS
cd backend
set -a && source .env && set +a
./scrape query emis "water" --format summary

# With verbose logging
export LOG_LEVEL=DEBUG
./scrape query emis "water"

# With visible browser
export HEADLESS=false
./scrape query emis "water"
```

---

## Phase 2: Form Filler (Future)

### Scope

**Included in Phase 2:**
- Detect form fields and types
- Interpret field labels/placeholders
- Fill forms based on user intent
- Handle complex fields (select, date, checkbox)
- Multi-step form support
- Field validation detection

**Excluded:**
- AI-based interpretation (future enhancement)
- Form submission (use existing logic)
- Complex JavaScript form libraries (unless common)

### Design Considerations

```python
@register_handler
class FormFiller(InteractionHandler):
    """
    Intelligent form filling handler.
    
    Detects form fields and fills them based on:
    - User-provided data
    - Field labels/placeholders
    - Context clues
    """
    
    def priority(self) -> int:
        return 30  # Lower priority than popups
    
    async def detect(self, page: Page) -> bool:
        """Detect if forms need filling."""
        # Check for unfilled required fields
        pass
    
    async def handle(self, page: Page) -> HandlerResult:
        """Fill detected forms."""
        # Detect fields
        # Interpret field purpose
        # Fill with appropriate data
        pass
```

### Configuration Schema

```yaml
interactions:
  forms:
    enabled: true
    auto_fill: false  # Require explicit trigger
    
    # Field mappings (optional)
    field_mappings:
      search_query: 'input[name="search"]'
      date_from: 'input[name="start_date"]'
      date_to: 'input[name="end_date"]'
    
    # Default values
    defaults:
      date_range: last_30_days
      results_per_page: 50
```

---

## Implementation Plan

### Phase 1: Popup Handler (Week 1)

**Day 1-2: Foundation**
- [ ] Create `backend/interactions/` module structure
- [ ] Implement `base.py` with abstract classes
- [ ] Implement `registry.py` with handler discovery
- [ ] Add comprehensive docstrings and type hints

**Day 3-4: Popup Handler**
- [ ] Implement `handlers/popup_handler.py`
- [ ] Add default selector patterns
- [ ] Add configuration loading
- [ ] Add error handling and logging

**Day 5: Integration**
- [ ] Modify `core/scraper.py` to call interaction handlers
- [ ] Add strategic invocation points
- [ ] Update EMIS config with popup configuration
- [ ] Remove hardcoded cookie handling from `form_based.py`

**Day 6: Testing**
- [ ] Test with EMIS portal (cookie consent)
- [ ] Test with sites without popups (no false positives)
- [ ] Test error scenarios
- [ ] Verify non-interference with existing flows

**Day 7: Documentation**
- [ ] Update development docs
- [ ] Add configuration examples
- [ ] Update user documentation
- [ ] Create migration guide

### Phase 2: Form Filler (Week 2)

**Planning only** - Implementation deferred based on Phase 1 learnings

- [ ] Design field detection logic
- [ ] Design interpretation rules
- [ ] Design configuration schema
- [ ] Plan integration points

### Success Criteria

**Phase 1 Complete When:**
- ✅ EMIS cookie consent handled automatically
- ✅ No code duplication in auth strategies
- ✅ All existing tests pass
- ✅ New popup handler tests pass
- ✅ Documentation updated
- ✅ Can add new sites with popup config easily

---

## Migration Path

### Step 1: Opt-In (Week 1)

Enable for EMIS only:

```yaml
# sites/emis.yaml
interactions:
  popups:
    enabled: true
    selectors:
      - '.vito--cookie button'
      - 'button:has-text("Aanvaarden")'
```

### Step 2: Cleanup (Week 2)

Remove hardcoded popup handling from `form_based.py`:

```python
# BEFORE: Hardcoded in form_based.py
cookie_consent = self.config.get('cookie_consent')
if cookie_consent:
    # ... hardcoded handling ...

# AFTER: Handled by PopupHandler
# No cookie-specific code in auth strategy
```

### Step 3: Expand (Week 3)

Enable for other sites as needed:

```yaml
# sites/other_site.yaml
interactions:
  popups:
    enabled: true
    # Uses default selectors automatically
```

### Step 4: Default (Week 4)

Make enabled by default for all sites:

```python
# registry.py
self.enabled = self.popup_config.get('enabled', True)  # Default True
```

---

## Risk Mitigation

### Risk 1: Breaking Existing Flows

**Mitigation:**
- Opt-in initially with `enabled: false` default
- Comprehensive testing before enabling
- Fail-safe design (never throw exceptions that break scraping)
- Extensive logging for debugging

### Risk 2: False Positives

**Mitigation:**
- Conservative default selectors
- Site-specific configuration overrides
- Detection timeout (don't wait forever)
- Log all dismissals for review

### Risk 3: Timing Issues

**Mitigation:**
- Configurable wait times
- Retry logic with exponential backoff
- Detect element visibility before interaction
- Integration at multiple lifecycle points

### Risk 4: Performance Impact

**Mitigation:**
- Short detection timeouts (2-5 seconds)
- Fail fast on detection
- Only run when enabled
- Log timing metrics

---

## Future Enhancements

### AI-Based Field Interpretation

Use LLM to interpret form fields:

```python
async def interpret_field(self, field_element) -> str:
    """Use LLM to determine field purpose."""
    label = await field_element.get_attribute('label')
    placeholder = await field_element.get_attribute('placeholder')
    
    prompt = f"What data should go in a field with label '{label}' and placeholder '{placeholder}'?"
    # Call LLM API
    # Return interpretation
```

### Multi-Language Support

```yaml
interactions:
  popups:
    language: auto  # or 'en', 'nl', 'fr', 'de'
    accept_terms:
      en: ["Accept", "OK", "Agree"]
      nl: ["Aanvaarden", "OK", "Akkoord"]
      fr: ["Accepter", "OK", "D'accord"]
```

### Advanced Pattern Detection

```python
class AIPopupHandler(InteractionHandler):
    """Use computer vision to detect popups."""
    
    async def detect(self, page: Page) -> bool:
        # Take screenshot
        # Use CV model to detect popup patterns
        # Return confidence score
        pass
```

### Performance Monitoring

```python
@dataclass
class HandlerMetrics:
    handler_name: str
    detection_time_ms: float
    handling_time_ms: float
    success_rate: float
    
# Track and expose metrics
GET /metrics/interactions
```

---

## Dependencies

### Required
- `playwright` - Already installed
- Python 3.8+ - Already required

### Optional (Future)
- `openai` or `anthropic` - For AI-based interpretation
- `opencv-python` - For vision-based detection
- `prometheus-client` - For metrics

---

## Rollout Plan

### Week 1: Development
- Implement Phase 1
- Internal testing

### Week 2: Alpha Testing
- Enable for EMIS only
- Monitor logs
- Fix issues

### Week 3: Beta Testing
- Enable for 2-3 more sites
- Gather feedback
- Refine selectors

### Week 4: General Availability
- Enable by default
- Update documentation
- Announce feature

---

## Success Metrics

### Technical Metrics
- **Detection Accuracy**: >95% for enabled sites
- **False Positive Rate**: <5%
- **Performance Impact**: <500ms per page
- **Error Rate**: <1%

### User Experience Metrics
- **Sites Successfully Scraped**: Should not decrease
- **Authentication Success Rate**: Should not decrease
- **User Complaints**: Should not increase

### Code Quality Metrics
- **Code Duplication**: Reduced by removing hardcoded handlers
- **Test Coverage**: >80% for interaction module
- **Documentation**: 100% of public APIs documented

---

## Questions & Decisions

### Open Questions

1. **When to invoke handlers?**
   - After every navigation? (safest but slower)
   - Only when configured? (faster but might miss cases)
   - **Decision**: Opt-in via config initially, strategic invocation points

2. **How many popups to dismiss per page?**
   - All detected popups? (thorough but risky)
   - Only first match? (safer but incomplete)
   - **Decision**: First match only, with retry option in config

3. **Should handlers be stateful?**
   - Remember dismissed popups? (avoid redundant work)
   - Always check fresh? (simpler but redundant)
   - **Decision**: Stateless for Phase 1, consider state for Phase 2

### Decisions Made

1. ✅ **Phase 1 only**: Popup handler first, form filler later
2. ✅ **Opt-in initially**: Requires `enabled: true` in config
3. ✅ **Fail-safe design**: Never break scraping flow
4. ✅ **Strategic invocation**: After navigation and before auth
5. ✅ **Priority-based**: Handlers declare priority, run in order

---

## Appendix

### Example: Adding a New Handler

```python
# backend/interactions/handlers/my_handler.py

from ..base import InteractionHandler, HandlerResult
from ..registry import register_handler

@register_handler
class MyHandler(InteractionHandler):
    """Custom handler for specific site pattern."""
    
    def priority(self) -> int:
        return 50  # Medium priority
    
    async def detect(self, page: Page) -> bool:
        # Detection logic
        return await page.query_selector('.my-pattern') is not None
    
    async def handle(self, page: Page) -> HandlerResult:
        # Handling logic
        await page.click('.my-pattern .close')
        return HandlerResult(success=True, message="Pattern handled")
```

### Example: Site Configuration

```yaml
# sites/mysite.yaml
site_id: mysite
name: My Website
base_url: https://example.com

auth:
  type: form_based
  login_url: https://example.com/login
  # ... auth config ...

interactions:
  popups:
    enabled: true
    selectors:
      - '.cookie-notice button.accept'
      - '.modal .btn-close'
    wait_after_appearance: 1500
    wait_after_dismiss: 500

# ... rest of config ...
```

### Example: Testing

```python
# tests/test_popup_handler.py

import pytest
from playwright.async_api import async_playwright
from interactions.handlers.popup_handler import PopupHandler

@pytest.mark.asyncio
async def test_cookie_consent_detection():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Create handler
        config = {'interactions': {'popups': {'enabled': True}}}
        handler = PopupHandler(config)
        
        # Load test page with cookie consent
        await page.set_content('''
            <div class="cookie-banner">
                <button class="accept">Accept</button>
            </div>
        ''')
        
        # Test detection
        detected = await handler.detect(page)
        assert detected is True
        
        # Test handling
        result = await handler.handle(page)
        assert result.success is True
        
        await browser.close()
```

---

## Conclusion

This plan provides a comprehensive roadmap for implementing a UI Interaction Subagent that:

1. **Solves immediate problems** (EMIS cookie consent)
2. **Follows framework patterns** (strategy, registry, configuration)
3. **Is extensible** (easy to add new handlers)
4. **Is safe** (opt-in, fail-safe, well-tested)
5. **Has clear phases** (popup handler first, form filler later)

The phased approach allows us to:
- Deliver value quickly (Phase 1: ~1 week)
- Learn from real usage before expanding (Phase 2)
- Maintain backwards compatibility
- Minimize risk to existing functionality

**Next Steps:**
1. Review and approve this plan
2. Create feature branch: `feature/ui-interaction-subagent`
3. Begin Phase 1 implementation
4. Test with EMIS portal
5. Iterate based on feedback

---

**Document History:**
- v1.0 (2025-11-06): Initial plan created
