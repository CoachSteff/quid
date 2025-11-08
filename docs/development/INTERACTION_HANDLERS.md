# UI Interaction Handlers

## Overview

The UI Interaction Subagent is a modular system for handling common web UI patterns like popups, cookie consents, modals, and dialogs. It follows the same architectural patterns as authentication strategies and extractors.

## Architecture

```
backend/interactions/
├── __init__.py           # Module exports
├── base.py               # Abstract base classes
├── registry.py           # Handler discovery and selection
└── handlers/
    ├── __init__.py       # Handler imports
    └── popup_handler.py  # Popup/cookie consent handler
```

## Usage

### 1. Enable in Site Configuration

Add an `interactions` section to your site YAML configuration:

```yaml
# sites/mysite.yaml
site_id: mysite
name: My Website
base_url: https://example.com

# UI Interactions
interactions:
  popups:
    enabled: true
    auto_dismiss: true
    wait_after_appearance: 1000  # ms
    wait_after_dismiss: 500       # ms
    selectors:
      - '.cookie-banner button:has-text("Accept")'
      - '.modal .close'
      - 'button:has-text("OK")'

# ... rest of config
```

### 2. Configuration Options

#### Popup Handler

- **`enabled`** (boolean): Enable popup detection and dismissal
- **`auto_dismiss`** (boolean): Automatically dismiss detected popups (default: true)
- **`wait_after_appearance`** (int): Milliseconds to wait after popup appears (default: 1000)
- **`wait_after_dismiss`** (int): Milliseconds to wait after dismissal (default: 500)
- **`selectors`** (list): Site-specific selectors to try (optional, uses defaults if not specified)

#### Default Selectors

If no selectors are specified, the popup handler uses these defaults:

```python
# Cookie consent
'.cookie-banner button:has-text("Accept")'
'.cookie-consent button:has-text("Accept")'
'[class*="cookie"] button[class*="accept"]'
'button:has-text("Aanvaarden")'  # Dutch

# Generic modals
'.modal .close'
'[data-dismiss="modal"]'
'.modal-close'

# Overlays
'.overlay .close'
'.popup-close'

# Newsletter/Subscription
'.newsletter-popup .close'
'[class*="newsletter"] button[class*="close"]'
```

### 3. Example: EMIS Portal

```yaml
# sites/emis.yaml
interactions:
  popups:
    enabled: true
    auto_dismiss: true
    wait_after_appearance: 1000
    wait_after_dismiss: 500
    selectors:
      - '.vito--cookie button'
      - 'button:has-text("Aanvaarden")'
      - '.cookie-consent button:has-text("Accept")'
```

This configuration successfully dismisses the VITO cookie consent popup before authentication.

## How It Works

### 1. Handler Registration

Handlers are automatically registered using the `@register_handler` decorator:

```python
from ..base import InteractionHandler, HandlerResult
from ..registry import register_handler

@register_handler
class PopupHandler(InteractionHandler):
    def priority(self) -> int:
        return 10  # Higher priority (lower number)
    
    async def detect(self, page: Page) -> bool:
        # Detection logic
        pass
    
    async def handle(self, page: Page) -> HandlerResult:
        # Handling logic
        pass
```

### 2. Invocation Points

Handlers are invoked at strategic points in the scraping flow:

- **After page navigation** (in `_perform_search`)
- **Before authentication** (in `_login`)
- **After login page load** (in `FormBasedAuth.login`)

### 3. Execution Flow

1. **Detection Phase**: Each registered handler's `detect()` method checks if it should run
2. **Priority Sorting**: Handlers are sorted by priority (lower = higher priority)
3. **Execution**: Each handler that detects a match runs its `handle()` method
4. **Logging**: Results are logged for debugging and monitoring
5. **Fail-Safe**: Errors never break the scraping flow

### 4. Example Output

```
2025-11-06 10:42:47 - interactions.registry - INFO - Executing handler: PopupHandler
2025-11-06 10:42:48 - interactions.handlers.popup_handler - INFO - Dismissed popup: .vito--cookie button
2025-11-06 10:42:49 - interactions.registry - INFO - PopupHandler: Dismissed popup using: .vito--cookie button
```

## Creating Custom Handlers

### Step 1: Create Handler File

```python
# backend/interactions/handlers/my_handler.py

from ..base import InteractionHandler, HandlerResult
from ..registry import register_handler
from playwright.async_api import Page

@register_handler
class MyCustomHandler(InteractionHandler):
    """Handler for custom UI pattern."""
    
    def __init__(self, config):
        super().__init__(config)
        # Extract handler-specific config
        self.handler_config = config.get('interactions', {}).get('my_handler', {})
        self.enabled = self.handler_config.get('enabled', False)
    
    def priority(self) -> int:
        """Priority (0-100, lower = higher priority)."""
        return 50  # Medium priority
    
    async def detect(self, page: Page) -> bool:
        """Detect if handler should run."""
        if not self.enabled:
            return False
        
        # Your detection logic
        element = await page.query_selector('.my-pattern')
        return element is not None
    
    async def handle(self, page: Page) -> HandlerResult:
        """Handle the interaction."""
        try:
            await page.click('.my-pattern .close')
            return HandlerResult(
                success=True,
                action_taken="custom_action",
                message="Successfully handled custom pattern"
            )
        except Exception as e:
            return HandlerResult(
                success=False,
                message=f"Failed: {str(e)}"
            )
```

### Step 2: Import Handler

```python
# backend/interactions/handlers/__init__.py

from .popup_handler import PopupHandler
from .my_handler import MyCustomHandler  # Add import

__all__ = ['PopupHandler', 'MyCustomHandler']
```

### Step 3: Configure in Site YAML

```yaml
interactions:
  my_handler:
    enabled: true
    # Your custom options
```

## Best Practices

### 1. Detection

- Keep detection fast (< 2 seconds)
- Use `query_selector` instead of `wait_for_selector` for detection
- Check element visibility before returning true
- Return false if handler is not enabled

### 2. Handling

- Use reasonable timeouts (2-5 seconds)
- Wait for elements to be visible and stable
- Add appropriate delays after actions
- Log actions for debugging
- Never throw exceptions that break the scraping flow

### 3. Configuration

- Make handlers opt-in (enabled: false by default)
- Provide sensible defaults
- Support site-specific overrides
- Document all configuration options

### 4. Priority

- **0-20**: Critical handlers (cookie consent, blocking modals)
- **21-50**: Standard handlers (popups, notifications)
- **51-100**: Low-priority handlers (optional interactions)

## Testing

### Unit Test Example

```python
import pytest
from playwright.async_api import async_playwright
from interactions.handlers.popup_handler import PopupHandler

@pytest.mark.asyncio
async def test_popup_detection():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Create handler
        config = {'interactions': {'popups': {'enabled': True}}}
        handler = PopupHandler(config)
        
        # Load test page
        await page.set_content('<div class="cookie-banner"><button>Accept</button></div>')
        
        # Test detection
        assert await handler.detect(page) is True
        
        # Test handling
        result = await handler.handle(page)
        assert result.success is True
        
        await browser.close()
```

### Manual Testing

```bash
# Test with visible browser
export HEADLESS=false
export LOG_LEVEL=DEBUG
./scrape query mysite "test query"

# Check logs for handler execution
grep "PopupHandler" logs/scraper.log
```

## Troubleshooting

### Handler Not Running

1. Check if enabled in config: `interactions.popups.enabled: true`
2. Verify handler is imported in `handlers/__init__.py`
3. Check detection logic returns true
4. Review logs for errors

### Selector Not Working

1. Test selector in browser console: `document.querySelector('...')`
2. Check if element is in shadow DOM (may need different approach)
3. Try multiple fallback selectors
4. Add debug logging in detect() method

### Timing Issues

1. Increase `wait_after_appearance` if popup loads slowly
2. Increase `wait_after_dismiss` if page reacts slowly
3. Check if handler runs before popup appears
4. Consider adding retry logic

## Future Enhancements

### Phase 2: Form Filler

Coming soon: Intelligent form filling handler that:
- Detects form fields automatically
- Interprets field purpose from labels/placeholders
- Fills forms based on user intent
- Handles complex field types

### Possible Extensions

- Multi-language support (auto-detect button text)
- AI-based pattern detection
- Computer vision for popup detection
- Performance metrics and monitoring
- Retry logic with exponential backoff

## Migration from Hardcoded Handlers

If you have hardcoded popup/cookie handling in auth strategies:

### Before (Hardcoded)

```python
# In auth strategy
cookie_consent = self.config.get('cookie_consent')
if cookie_consent:
    selector = cookie_consent.get('selector')
    await page.click(selector)
```

### After (Using Interaction Handler)

1. Remove hardcoded logic from auth strategy
2. Add to site config:

```yaml
interactions:
  popups:
    enabled: true
    selectors:
      - '.cookie-consent button'
```

3. Handler runs automatically before authentication

## Support

For issues or questions:
1. Check logs for handler execution
2. Review site configuration
3. Test selectors in browser console
4. Create a GitHub issue with logs and config

---

**Last Updated**: November 6, 2025  
**Version**: 1.0  
**Status**: Phase 1 Complete (Popup Handler)
