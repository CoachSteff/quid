# UI Interaction Handlers - Quick Start Guide

## Overview

The UI Interaction Subagent handles common web UI patterns like cookie consents, popups, and modals automatically.

## 5-Minute Setup

### 1. Enable in Your Site Config

Add to `sites/yoursite.yaml`:

```yaml
interactions:
  popups:
    enabled: true
    selectors:
      - '.cookie-banner button:has-text("Accept")'
      - '.modal .close'
```

### 2. That's It!

The handler will automatically:
- Detect popups on page load
- Dismiss them before authentication
- Log actions for debugging

## Common Configurations

### Cookie Consent Only

```yaml
interactions:
  popups:
    enabled: true
    selectors:
      - '.cookie-consent button:has-text("Accept")'
```

### Multiple Languages

```yaml
interactions:
  popups:
    enabled: true
    selectors:
      - 'button:has-text("Accept")'      # English
      - 'button:has-text("Accepter")'    # French
      - 'button:has-text("Akzeptieren")' # German
      - 'button:has-text("Aanvaarden")'  # Dutch
```

### Use Defaults

If you don't specify selectors, the handler uses sensible defaults:

```yaml
interactions:
  popups:
    enabled: true
    # Uses built-in selectors for common cookie/popup patterns
```

### Custom Timing

```yaml
interactions:
  popups:
    enabled: true
    wait_after_appearance: 2000  # Wait 2s for popup to fully appear
    wait_after_dismiss: 1000     # Wait 1s after clicking dismiss
    selectors:
      - '.slow-loading-popup button'
```

## Testing Your Configuration

### View in Browser

```bash
export HEADLESS=false
export LOG_LEVEL=DEBUG
cd backend
./scrape query yoursite "test"
```

### Check Logs

Look for these log lines:

```
interactions.registry - INFO - Executing handler: PopupHandler
interactions.handlers.popup_handler - INFO - Dismissed popup: .cookie-consent button
interactions.registry - INFO - PopupHandler: Dismissed popup using: ...
```

### Debug Selector

If your selector doesn't work:

1. Open site in browser
2. Open browser console (F12)
3. Test selector: `document.querySelector('your-selector')`
4. If null, adjust selector
5. Update config and test again

## Troubleshooting

### Handler Not Running

**Problem**: No log lines about PopupHandler

**Solutions**:
- Set `enabled: true` in config
- Check selector is correct
- Increase LOG_LEVEL to DEBUG

### Wrong Element Selected

**Problem**: Handler clicks wrong button

**Solutions**:
- Make selector more specific: `.cookie-banner button.accept`
- Add text match: `button:has-text("Accept All")`
- Use multiple fallback selectors

### Timing Issues

**Problem**: Handler runs too early/late

**Solutions**:
- Increase `wait_after_appearance` (popup loads slowly)
- Increase `wait_after_dismiss` (page reacts slowly)
- Check browser console for JavaScript errors

## Migration from Old Cookie Handling

### Before

```yaml
auth:
  cookie_consent:
    selector: '.cookie button'
    wait_after_click: 1000
```

### After

```yaml
interactions:
  popups:
    enabled: true
    selectors:
      - '.cookie button'
```

Then remove the `cookie_consent` section from `auth:`.

## When to Use

### ✅ Good Use Cases

- Cookie consent banners
- Newsletter signup popups
- Modal dialogs that block content
- Notification toasts
- Survey popups

### ❌ Not Suitable For

- Complex multi-step flows (use custom handler)
- Forms that need specific data (use Phase 2 Form Filler)
- Site-specific authentication flows (keep in auth strategy)

## Full Documentation

- **Usage Guide**: See `INTERACTION_HANDLERS.md`
- **Implementation Details**: See `UI_INTERACTION_IMPLEMENTATION_SUMMARY.md`
- **Original Plan**: See `UI_INTERACTION_SUBAGENT_PLAN.md`

## Support

If you encounter issues:

1. Set `LOG_LEVEL=DEBUG` and check logs
2. Test selector in browser console
3. Review configuration syntax
4. Check documentation above

---

**Quick Reference**: [Configuration Options](#common-configurations) | [Testing](#testing-your-configuration) | [Troubleshooting](#troubleshooting)
