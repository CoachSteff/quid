#!/usr/bin/env python3
"""
Form-based authentication strategy.
Handles traditional username/password login forms.
"""

import logging
import asyncio
import random
from typing import Dict
from playwright.async_api import Page, BrowserContext, TimeoutError as PlaywrightTimeoutError

from ..base import AuthStrategy, LoginFailedException, SessionExpiredException

try:
    from ...interactions.registry import InteractionRegistry
    from ...interactions import handlers
except ImportError:
    from interactions.registry import InteractionRegistry
    import interactions.handlers

logger = logging.getLogger(__name__)


class FormBasedAuth(AuthStrategy):
    """
    Authentication via HTML form submission.
    
    Supports:
    - Email/username + password forms
    - Multiple success/failure indicators
    - Configurable selectors
    - Human-like delays
    - Ionic Framework web components (ion-input, ion-button)
    """
    
    def __init__(self, config: Dict, credentials: Dict, full_site_config: Dict = None):
        """
        Initialize form-based auth strategy.
        
        Args:
            config: Authentication configuration from site YAML
            credentials: User credentials
            full_site_config: Full site configuration (for interaction handlers)
        """
        super().__init__(config, credentials)
        self.full_site_config = full_site_config or config
    
    async def _human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """Add randomized human-like delay."""
        delay = random.uniform(min_ms / 1000, max_ms / 1000)
        await asyncio.sleep(delay)
    
    async def _is_ionic_page(self, page: Page) -> bool:
        """Check if the page uses Ionic Framework."""
        try:
            is_ionic = await page.evaluate("""() => {
                return document.querySelector('html.hydrated, ion-app, ion-input, ion-button') !== null;
            }""")
            return is_ionic
        except:
            return False
    
    async def _wait_for_ionic_hydration(self, page: Page, timeout: int = 10000):
        """Wait for Ionic components to be hydrated (interactive)."""
        try:
            await page.wait_for_selector('html.hydrated', timeout=timeout)
            logger.info("Ionic hydration complete")
            await asyncio.sleep(1)  # Extra buffer for component initialization
        except PlaywrightTimeoutError:
            logger.warning("Ionic hydration timeout - proceeding anyway")
    
    async def _wait_for_ionic_modal(self, page: Page, timeout: int = 10000):
        """
        Wait for Ionic modal or custom dialog to appear and be interactive.
        
        Args:
            page: Playwright page instance
            timeout: Maximum wait time in milliseconds
            
        Returns:
            True if modal detected, False otherwise
        """
        modal_selectors = [
            '[role="dialog"]',  # Most common, including custom dialogs
            '.vito-dialog',     # EMIS-specific custom dialog
            'ion-modal',
            'ion-popover', 
            '.modal'
        ]
        
        for selector in modal_selectors:
            try:
                await page.wait_for_selector(selector, state="attached", timeout=min(timeout, 3000))
                logger.info(f"Modal detected: {selector}")
                # Wait for modal animation to complete
                await asyncio.sleep(1)
                # Wait for ion-input or input elements to be ready
                try:
                    # Try ion-input first
                    await page.wait_for_selector('ion-input', state="visible", timeout=2000)
                    logger.info("Modal ion-input elements ready")
                except PlaywrightTimeoutError:
                    try:
                        # Fallback to regular input
                        await page.wait_for_selector('input', state="visible", timeout=2000)
                        logger.info("Modal input elements ready")
                    except PlaywrightTimeoutError:
                        logger.debug("Input elements not immediately available in modal")
                return True
            except PlaywrightTimeoutError:
                continue
        
        logger.warning("No modal detected with standard selectors - proceeding anyway")
        return False
    
    async def _fill_ionic_input(self, page: Page, input_type: str, value: str, selectors: list) -> bool:
        """
        Fill an Ionic ion-input component using JavaScript.
        
        IMPORTANT: For Ionic modals, we must search within the modal context first
        before falling back to document-wide search.
        
        Args:
            page: Playwright page
            input_type: 'email' or 'password'
            value: Value to fill
            selectors: List of selectors to try
            
        Returns:
            True if successful, False otherwise
        """
        for selector in selectors:
            try:
                # Try to find ion-input component
                result = await page.evaluate("""
                    ({selector, value, inputType}) => {
                        // First, try to find modal context to scope search
                        let modalSelectors = ['[role="dialog"]', '.vito-dialog', 'ion-modal', 'ion-popover', '.modal'];
                        let searchContext = document;
                        
                        for (let modalSel of modalSelectors) {
                            let modal = document.querySelector(modalSel);
                            if (modal) {
                                searchContext = modal;
                                console.log('Found modal context:', modalSel);
                                break;
                            }
                        }
                        
                        // Try multiple approaches to find the input within modal
                        let ionInput = searchContext.querySelector(selector);
                        
                        if (!ionInput) {
                            // Try finding by type attribute in modal
                            ionInput = searchContext.querySelector(`ion-input[type="${inputType}"]`);
                        }
                        
                        if (!ionInput) {
                            // Last resort: search in document (for non-modal forms)
                            ionInput = document.querySelector(selector);
                        }
                        
                        if (!ionInput) {
                            return {success: false, reason: 'ion-input not found'};
                        }
                        
                        // Get the actual input element (can be in shadow DOM or regular DOM)
                        let input = ionInput.querySelector('input');
                        
                        // If not found, try shadow root
                        if (!input && ionInput.shadowRoot) {
                            input = ionInput.shadowRoot.querySelector('input');
                        }
                        
                        // Last resort: check if ion-input itself has input properties
                        if (!input && ionInput.value !== undefined) {
                            ionInput.value = value;
                            ionInput.dispatchEvent(new Event('ionChange', { bubbles: true }));
                            return {success: true, method: 'ion-input.value'};
                        }
                        
                        if (!input) {
                            return {success: false, reason: 'input element not found'};
                        }
                        
                        // Fill the input
                        input.value = value;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        
                        return {success: true, method: 'input.value'};
                    }
                """, {"selector": selector, "value": value, "inputType": input_type})
                
                if result.get('success'):
                    logger.info(f"Successfully filled {input_type} using {result.get('method')}")
                    return True
                else:
                    logger.debug(f"Selector {selector} failed: {result.get('reason')}")
                    
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        return False
    
    async def _click_ionic_button(self, page: Page, selectors: list) -> bool:
        """
        Click an Ionic ion-button component.
        
        IMPORTANT: For Ionic modals, we must search within the modal context first.
        
        Args:
            page: Playwright page
            selectors: List of selectors to try
            
        Returns:
            True if successful, False otherwise
        """
        for selector in selectors:
            try:
                result = await page.evaluate("""
                    (selector) => {
                        // Try to find button within modal first
                        let modalSelectors = ['[role="dialog"]', '.vito-dialog', 'ion-modal', 'ion-popover', '.modal'];
                        let searchContext = document;
                        
                        for (let modalSel of modalSelectors) {
                            let modal = document.querySelector(modalSel);
                            if (modal) {
                                searchContext = modal;
                                console.log('Found modal context for button:', modalSel);
                                break;
                            }
                        }
                        
                        let button = searchContext.querySelector(selector);
                        
                        if (!button) {
                            // Try finding by text content within modal
                            const buttons = searchContext.querySelectorAll('ion-button, button');
                            for (const btn of buttons) {
                                if (btn.textContent.toLowerCase().includes('login') || 
                                    btn.textContent.toLowerCase().includes('sign in') ||
                                    btn.textContent.toLowerCase().includes('inloggen')) {
                                    button = btn;
                                    break;
                                }
                            }
                        }
                        
                        if (!button) {
                            // Last resort: search in document
                            button = document.querySelector(selector);
                        }
                        
                        if (!button) {
                            return {success: false, reason: 'button not found'};
                        }
                        
                        button.click();
                        return {success: true};
                    }
                """, selector)
                
                if result.get('success'):
                    logger.info(f"Successfully clicked button")
                    return True
                    
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        return False
    
    async def login(self, page: Page, context: BrowserContext) -> bool:
        """
        Perform form-based login.
        
        Config structure:
        {
            "login_url": "https://...",
            "selectors": {
                "email_field": "input[name='email']",
                "password_field": "input[name='password']",
                "submit_button": "button[type='submit']"
            },
            "success_indicators": [
                {"type": "url_change", "pattern": "!login"},
                {"type": "element_present", "selector": ".dashboard"}
            ],
            "failure_indicators": [
                {"type": "element_present", "selector": ".error-message", "extract_error": true}
            ]
        }
        """
        login_url = self.config.get('login_url')
        selectors = self.config.get('selectors', {})
        
        if not login_url:
            raise LoginFailedException("No login_url configured")
        
        # Get credentials
        email = self.credentials.get('email') or self.credentials.get('username')
        password = self.credentials.get('password')
        
        if not email or not password:
            raise LoginFailedException("Missing email/username or password in credentials")
        
        logger.info(f"Navigating to login page: {login_url}")
        
        try:
            # Navigate to login page
            await page.goto(login_url, wait_until="networkidle", timeout=30000)
            await self._human_delay(2000, 3000)
            
            logger.info(f"Login page loaded: {page.url}")
            
            # Wait for page to be fully interactive
            await page.wait_for_load_state("domcontentloaded")
            
            # Check if this is an Ionic page and wait for hydration
            is_ionic = await self._is_ionic_page(page)
            if is_ionic:
                logger.info("Detected Ionic Framework - waiting for hydration")
                await self._wait_for_ionic_hydration(page)
            else:
                await asyncio.sleep(2)  # Standard wait for dynamic content
            
            # Handle any UI interactions (popups, cookie consent, etc.) before proceeding
            try:
                await InteractionRegistry.handle_interactions(page, self.full_site_config)
            except Exception as e:
                logger.debug(f"Interaction handling in auth: {e}")
            
            # Handle login trigger if specified (e.g., clicking a button to show login modal)
            login_trigger = self.config.get('login_trigger')
            if login_trigger:
                trigger_selector = login_trigger.get('selector')
                wait_after_click = login_trigger.get('wait_after_click', 2000)
                
                logger.info(f"Clicking login trigger: {trigger_selector}")
                try:
                    await page.wait_for_selector(trigger_selector, state="visible", timeout=10000)
                    await page.click(trigger_selector)
                    await asyncio.sleep(wait_after_click / 1000)
                    logger.info("Login trigger clicked - waiting for form to appear")
                    
                    # Wait for modal to appear and be fully interactive
                    if is_ionic:
                        modal_detected = await self._wait_for_ionic_modal(page, timeout=10000)
                        if not modal_detected:
                            logger.warning("Modal not detected but proceeding with login")
                except Exception as e:
                    logger.warning(f"Login trigger failed: {e} - proceeding anyway")
            
            # Check for iframes that might contain the login form
            frames = page.frames
            logger.info(f"Found {len(frames)} frames on the page")
            
            # Get email field selectors
            email_selector = selectors.get('email_field', 'input[name="email"], input[type="email"], input[name="username"]')
            email_selectors = [s.strip() for s in email_selector.split(',')]
            
            logger.info(f"Filling email field")
            
            # If Ionic page, use specialized Ionic input handler
            if is_ionic:
                success = await self._fill_ionic_input(page, 'email', email, email_selectors)
                if not success:
                    raise LoginFailedException("Could not fill email field on Ionic login page")
            else:
                # Standard form handling
                target_page = page
                filled = False
                
                # Try main page first
                for selector in email_selectors:
                    try:
                        await page.wait_for_selector(selector, state="visible", timeout=5000)
                        await page.fill(selector, email)
                        filled = True
                        break
                    except:
                        continue
                
                # Try frames if main page doesn't have it
                if not filled:
                    logger.info("Email field not found in main page, checking frames...")
                    for i, frame in enumerate(frames):
                        for selector in email_selectors:
                            try:
                                await frame.wait_for_selector(selector, state="visible", timeout=5000)
                                await frame.fill(selector, email)
                                target_page = frame
                                filled = True
                                logger.info(f"Found email field in frame {i}")
                                break
                            except:
                                continue
                        if filled:
                            break
                
                if not filled:
                    raise LoginFailedException("Could not find email/username input field on login page")
            
            await self._human_delay(500, 1000)
            
            # Get password field selectors
            password_selector = selectors.get('password_field', 'input[name="password"], input[type="password"]')
            password_selectors = [s.strip() for s in password_selector.split(',')]
            
            logger.info(f"Filling password field")
            
            # If Ionic page, use specialized handler
            if is_ionic:
                success = await self._fill_ionic_input(page, 'password', password, password_selectors)
                if not success:
                    raise LoginFailedException("Could not fill password field on Ionic login page")
            else:
                # Standard form handling
                filled = False
                for selector in password_selectors:
                    try:
                        await target_page.wait_for_selector(selector, state="visible", timeout=10000)
                        await target_page.fill(selector, password)
                        filled = True
                        break
                    except:
                        continue
                
                if not filled:
                    raise LoginFailedException("Could not find password input field on login page")
            
            await self._human_delay(500, 1000)
            
            # Get submit button selectors
            submit_selector = selectors.get('submit_button', 'button[type="submit"], input[type="submit"]')
            submit_selectors = [s.strip() for s in submit_selector.split(',')]
            
            logger.info(f"Clicking submit button")
            
            # If Ionic page, use specialized handler
            if is_ionic:
                success = await self._click_ionic_button(page, submit_selectors)
                if not success:
                    # Fallback: try Enter key
                    logger.info("Ionic button click failed, trying Enter key...")
                    await page.evaluate("""() => {
                        const ionInput = document.querySelector('ion-input[type="password"]');
                        if (ionInput) {
                            const input = ionInput.querySelector('input') || ionInput.shadowRoot?.querySelector('input');
                            if (input) {
                                input.dispatchEvent(new KeyboardEvent('keypress', {key: 'Enter', code: 'Enter', keyCode: 13}));
                            }
                        }
                    }""")
            else:
                # Standard form handling
                clicked = False
                for selector in submit_selectors:
                    try:
                        await target_page.wait_for_selector(selector, state="visible", timeout=10000)
                        await target_page.click(selector)
                        clicked = True
                        break
                    except:
                        continue
                
                if not clicked:
                    logger.info("Submit button not found, trying Enter key...")
                    await target_page.press(password_selectors[0], "Enter")
            
            await self._human_delay(2000, 3000)
            
            # Wait for navigation
            logger.info("Waiting for navigation after login")
            await page.wait_for_load_state("networkidle", timeout=15000)
            
            current_url = page.url
            logger.info(f"Post-login URL: {current_url}")
            
            # Check for failure indicators first
            failure_indicators = self.config.get('failure_indicators', [])
            for indicator in failure_indicators:
                if await self._check_indicator(page, indicator, is_failure=True):
                    error_msg = "Login failed"
                    
                    # Try to extract error message if configured
                    if indicator.get('extract_error'):
                        try:
                            error_element = await page.query_selector(indicator['selector'])
                            if error_element:
                                error_text = await error_element.inner_text()
                                error_msg = f"Login failed: {error_text.strip()}"
                        except:
                            pass
                    
                    raise LoginFailedException(error_msg)
            
            # Check for success indicators
            success_indicators = self.config.get('success_indicators', [
                {'type': 'url_change', 'pattern': '!login'}
            ])
            
            for indicator in success_indicators:
                if await self._check_indicator(page, indicator, is_failure=False):
                    logger.info("Login successful - indicator matched")
                    return True
            
            # No indicators matched - assume failure
            raise LoginFailedException("Login failed - no success indicators matched")
            
        except PlaywrightTimeoutError as e:
            raise LoginFailedException(f"Login timeout: {str(e)}")
        except LoginFailedException:
            # Re-raise login failures
            raise
        except Exception as e:
            raise LoginFailedException(f"Login error: {str(e)}")
    
    async def _check_indicator(self, page: Page, indicator: Dict, is_failure: bool) -> bool:
        """
        Check if a success/failure indicator is present.
        
        Args:
            page: Playwright Page
            indicator: Indicator config dict
            is_failure: True if this is a failure indicator
            
        Returns:
            True if indicator matches
        """
        indicator_type = indicator.get('type')
        
        if indicator_type == 'url_change':
            pattern = indicator.get('pattern', '')
            current_url = page.url
            
            # Pattern can start with '!' for negation
            if pattern.startswith('!'):
                # Should NOT contain this string
                negated_pattern = pattern[1:]
                return negated_pattern not in current_url.lower()
            else:
                # Should contain this string
                return pattern in current_url.lower()
        
        elif indicator_type == 'element_present':
            selector = indicator.get('selector')
            if not selector:
                return False
            
            try:
                element = await page.query_selector(selector)
                return element is not None
            except:
                return False
        
        elif indicator_type == 'element_absent':
            selector = indicator.get('selector')
            if not selector:
                return False
            
            try:
                element = await page.query_selector(selector)
                return element is None
            except:
                return True
        
        return False
    
    async def validate_session(self, page: Page) -> bool:
        """
        Validate that the session is still active.
        
        Uses the same success indicators as login to check if user is logged in.
        """
        try:
            # Check success indicators
            success_indicators = self.config.get('success_indicators', [
                {'type': 'url_change', 'pattern': '!login'}
            ])
            
            for indicator in success_indicators:
                if await self._check_indicator(page, indicator, is_failure=False):
                    return True
            
            # Check if we're on login page (session expired)
            current_url = page.url
            if 'login' in current_url.lower():
                logger.info("Session expired - redirected to login page")
                return False
            
            return False
            
        except Exception as e:
            logger.warning(f"Session validation error: {e}")
            return False
