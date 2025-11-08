#!/usr/bin/env python3
"""
Generic web scraper with pluggable authentication and extraction strategies.
"""

import os
import logging
import random
import asyncio
from datetime import datetime
from typing import Dict, Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
try:
    from playwright_stealth import stealth_async
except ImportError:
    # Fallback for newer playwright-stealth versions (2.0+)
    # In v2.0+, use Stealth class with apply_stealth_async method
    from playwright_stealth import Stealth
    async def stealth_async(context):
        stealth = Stealth()
        await stealth.apply_stealth_async(context)

from .session_manager import SessionManager
from .config_loader import get_config_loader, ConfigurationException
try:
    from ..auth.base import AuthStrategy, LoginFailedException, SessionExpiredException
    from ..auth.strategies.form_based import FormBasedAuth
    from ..extractors import get_registry
    from ..credentials import get_credential_manager
    from ..interactions.registry import InteractionRegistry
    from ..interactions import handlers
except ImportError:
    # Fallback for when running as script (cli.py adds backend to path)
    from auth.base import AuthStrategy, LoginFailedException, SessionExpiredException
    from auth.strategies.form_based import FormBasedAuth
    from extractors import get_registry
    from credentials import get_credential_manager
    from interactions.registry import InteractionRegistry
    import interactions.handlers

logger = logging.getLogger(__name__)


class ScraperException(Exception):
    """Base exception for scraper errors."""
    pass


class GenericScraper:
    """
    Generic web scraper that uses configuration-driven strategies.
    
    Features:
    - Configurable authentication strategies
    - Pluggable data extraction
    - Session management with persistence
    - Resource cleanup with context manager support
    """
    
    # Realistic user agents for stealth
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]
    
    def __init__(self, site_id: str, trace_id: Optional[str] = None):
        """
        Initialize scraper for a specific site.
        
        Args:
            site_id: Site identifier (e.g., 'emis')
            trace_id: Optional trace ID for logging correlation
        """
        self.site_id = site_id
        self.trace_id = trace_id or f"trace_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # Load site configuration
        config_loader = get_config_loader()
        try:
            self.config = config_loader.load_site(site_id)
        except ConfigurationException as e:
            logger.error(f"[{self.trace_id}] Failed to load site config: {e}")
            raise ScraperException(f"Site configuration error: {str(e)}")
        
        # Initialize components
        self.session_manager = SessionManager(site_id, config=self.config)
        self.credential_manager = get_credential_manager()
        self.extractor_registry = get_registry()
        
        # Browser resources (initialized when needed)
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Auth strategy (initialized when needed)
        self._auth_strategy: Optional[AuthStrategy] = None
        
        logger.info(f"[{self.trace_id}] GenericScraper initialized for site: {site_id}")
    
    async def __aenter__(self):
        """Context manager entry - initialize browser."""
        await self._init_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        await self.cleanup()
    
    def _get_auth_strategy(self) -> AuthStrategy:
        """
        Get authentication strategy for this site.
        
        Returns:
            AuthStrategy instance
            
        Raises:
            ScraperException: If auth type not supported
        """
        if self._auth_strategy:
            return self._auth_strategy
        
        auth_config = self.config.get('auth', {})
        auth_type = auth_config.get('type', 'none')
        
        # Get credentials
        credentials = self.credential_manager.get_credentials(self.site_id)
        
        # Create strategy based on type
        if auth_type == 'none':
            # No authentication needed
            logger.info(f"[{self.trace_id}] Site requires no authentication")
            return None
        elif auth_type == 'form_based':
            self._auth_strategy = FormBasedAuth(auth_config, credentials, self.config)
        else:
            raise ScraperException(f"Unsupported auth type: {auth_type}")
        
        return self._auth_strategy
    
    async def _init_browser(self):
        """Initialize Playwright browser and context."""
        browser_config = self.config.get('browser', {})
        
        # Get browser settings (can be overridden by env vars)
        headless = os.getenv('HEADLESS', str(browser_config.get('headless', True))).lower() == 'true'
        slow_mo = int(os.getenv('PLAYWRIGHT_SLOW_MO', browser_config.get('slow_mo', 500)))
        
        logger.info(f"[{self.trace_id}] Launching browser (headless={headless}, slow_mo={slow_mo}ms)")
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                slow_mo=slow_mo
            )
        except Exception as e:
            logger.error(f"[{self.trace_id}] Failed to launch browser: {e}")
            await self.cleanup()
            raise ScraperException(f"Browser initialization failed: {str(e)}")
    
    async def _create_context(self, session_data: Optional[Dict] = None) -> BrowserContext:
        """
        Create browser context with stealth settings.
        
        Args:
            session_data: Optional session data to restore
            
        Returns:
            BrowserContext
        """
        # Select random user agent
        user_agent = random.choice(self.USER_AGENTS)
        
        # Create context with realistic settings
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': user_agent,
            'locale': 'en-US',
            'timezone_id': 'Europe/Brussels',
        }
        
        # Add session data if provided
        if session_data:
            context_options['storage_state'] = session_data
        
        context = await self.browser.new_context(**context_options)
        
        # Apply stealth plugin
        await stealth_async(context)
        
        return context
    
    async def _quick_session_check(self, context: BrowserContext) -> bool:
        """
        Quick session validation using cookies only (no page load).
        Faster but less reliable than full validation.
        
        Returns:
            True if site-specific cookies are present
        """
        try:
            cookies = await context.cookies()
            
            # Get base domain from config
            base_url = self.config.get('base_url', '')
            # Extract domain (e.g., "emis.vito.be" from "https://emis.vito.be")
            domain = base_url.replace('https://', '').replace('http://', '').split('/')[0]
            
            # Check for cookies from the site's domain
            site_cookies = [c for c in cookies if domain in c.get('domain', '')]
            
            # Also check for common session cookie keywords
            essential_keywords = ['session', 'auth', 'token', 'sid', 'ssid', 'logged', 'ts']  # Added 'ts' for EMIS
            
            has_essential = any(
                any(keyword in cookie['name'].lower() for keyword in essential_keywords)
                for cookie in cookies
            )
            
            # Consider valid if we have site-specific cookies OR essential cookies
            has_session = len(site_cookies) > 0 or has_essential
            
            if has_session:
                logger.debug(f"[{self.trace_id}] Quick session check: found {len(site_cookies)} site cookies")
            else:
                logger.debug(f"[{self.trace_id}] Quick session check: no site cookies found")
            
            return has_session
            
        except Exception as e:
            logger.debug(f"[{self.trace_id}] Quick session check failed: {e}")
            return False
    
    async def _validate_session(self) -> bool:
        """
        Try to load and validate existing session.
        
        Returns:
            True if session is valid
        """
        # Quick TTL check before expensive network validation
        if self.session_manager.is_session_expired():
            logger.info(f"[{self.trace_id}] Session expired (TTL exceeded)")
            return False
        
        session_data = self.session_manager.load_session()
        
        if not session_data:
            return False
        
        try:
            # Create context with session
            self.context = await self._create_context(session_data)
            
            # Try quick cookie check first (no page load required)
            validation_method = self.config.get('session', {}).get('validation', {}).get('method', 'full')
            
            if validation_method in ['quick', 'cookies_only']:
                if await self._quick_session_check(self.context):
                    # Cookie check passed - create page without full validation
                    self.page = await self.context.new_page()
                    logger.info(f"[{self.trace_id}] Session validated (quick check)")
                    return True
                elif validation_method == 'cookies_only':
                    # Cookies-only mode failed
                    logger.info(f"[{self.trace_id}] Session validation failed (cookies only)")
                    await self.context.close()
                    self.context = None
                    return False
                # If quick check failed but method is 'quick', fall through to full validation
            
            # Full validation: load page and check
            self.page = await self.context.new_page()
            
            # Navigate to base URL to test session
            base_url = self.config.get('base_url')
            # Increased timeout from 15s to 30s for slower-loading sites
            validation_timeout = self.config.get('session', {}).get('validation', {}).get('timeout_ms', 30000)
            await self.page.goto(base_url, wait_until="networkidle", timeout=validation_timeout)
            await asyncio.sleep(random.uniform(1, 2))
            
            # Use auth strategy to validate
            auth_strategy = self._get_auth_strategy()
            
            if auth_strategy and not await auth_strategy.validate_session(self.page):
                logger.info(f"[{self.trace_id}] Session validation failed")
                await self.context.close()
                self.context = None
                self.page = None
                return False
            
            logger.info(f"[{self.trace_id}] Session validated successfully")
            return True
            
        except Exception as e:
            logger.warning(f"[{self.trace_id}] Session validation error: {e}")
            if self.context:
                await self.context.close()
                self.context = None
                self.page = None
            return False
    
    async def _handle_interactions(self, page: Page) -> None:
        """
        Handle common UI interactions (popups, modals, etc.).
        
        Called at strategic points in the scraping flow:
        - After page navigation
        - Before authentication
        - Before form interactions
        
        Args:
            page: Playwright page instance
        """
        try:
            results = await InteractionRegistry.handle_interactions(
                page,
                self.config
            )
            
            # Log results
            for result in results:
                if result.success:
                    logger.debug(f"[{self.trace_id}] Interaction handled: {result.message}")
                else:
                    logger.warning(f"[{self.trace_id}] Interaction failed: {result.message}")
                    
        except Exception as e:
            logger.error(f"[{self.trace_id}] Interaction handling error: {e}")
            # Never fail the scraping flow due to interaction handling
    
    async def _login(self):
        """Perform authentication."""
        auth_strategy = self._get_auth_strategy()
        
        if not auth_strategy:
            # No auth required
            return
        
        logger.info(f"[{self.trace_id}] Starting authentication")
        
        # Create new context if not exists
        if not self.context:
            self.context = await self._create_context()
            self.page = await self.context.new_page()
        
        try:
            # Handle any popups before authentication
            await self._handle_interactions(self.page)
            
            # Perform login
            await auth_strategy.login(self.page, self.context)
            
            # Save session
            await self.session_manager.save_session(self.context)
            
            logger.info(f"[{self.trace_id}] Authentication successful")
            
        except LoginFailedException as e:
            logger.error(f"[{self.trace_id}] Login failed: {e}")
            raise ScraperException(f"Authentication failed: {str(e)}")
    
    async def _fill_ionic_search(self, query: str, selector: str) -> bool:
        """
        Fill Ionic search input (ion-input, ion-searchbar) with query.
        
        Args:
            query: Search query string
            selector: CSS selector for the search input
            
        Returns:
            True if successfully filled, False otherwise
        """
        try:
            result = await self.page.evaluate("""
                ({selector, query}) => {
                    // Try to find ion-input or ion-searchbar
                    let element = document.querySelector(selector);
                    
                    if (!element) {
                        // Try first ion-input if selector doesn't match
                        element = document.querySelector('ion-input');
                    }
                    
                    if (!element) {
                        return {success: false, reason: 'element not found'};
                    }
                    
                    // Get actual input element (may be in shadow DOM)
                    let input = element.querySelector('input');
                    if (!input && element.shadowRoot) {
                        input = element.shadowRoot.querySelector('input');
                    }
                    
                    if (!input) {
                        return {success: false, reason: 'input element not found'};
                    }
                    
                    // Fill the input
                    input.value = query;
                    input.dispatchEvent(new Event('input', {bubbles: true}));
                    input.dispatchEvent(new Event('change', {bubbles: true}));
                    
                    // Also dispatch ionInput for Ionic components
                    if (element.tagName.toLowerCase().startsWith('ion-')) {
                        element.dispatchEvent(new Event('ionInput', {bubbles: true}));
                    }
                    
                    return {success: true, value: input.value};
                }
            """, {"selector": selector, "query": query})
            
            if result.get('success'):
                logger.info(f"[{self.trace_id}] Filled Ionic search input: {result.get('value')}")
                return True
            else:
                logger.debug(f"[{self.trace_id}] Ionic search fill failed: {result.get('reason')}")
                return False
                
        except Exception as e:
            logger.debug(f"[{self.trace_id}] Ionic search fill error: {e}")
            return False
    
    async def _perform_search(self, query: str):
        """
        Navigate to search page and execute query.
        
        Args:
            query: Search query string
        """
        search_config = self.config.get('search', {})
        
        if not search_config:
            logger.warning(f"[{self.trace_id}] No search configuration, staying on current page")
            return
        
        search_url = search_config.get('url')
        
        if not search_url:
            return
        
        logger.info(f"[{self.trace_id}] Navigating to search: {search_url}")
        
        try:
            await self.page.goto(search_url, wait_until="networkidle", timeout=15000)
            await asyncio.sleep(random.uniform(1, 2))
            
            # Handle any popups before search
            await self._handle_interactions(self.page)
            
            # Fill search input
            selectors = search_config.get('selectors', {})
            search_input_selector = selectors.get('search_input')
            search_button_selector = selectors.get('search_button')
            
            if search_input_selector:
                logger.info(f"[{self.trace_id}] Filling search query: {query}")
                
                # Try to wait for selector
                try:
                    await self.page.wait_for_selector(search_input_selector, timeout=10000)
                except:
                    logger.warning(f"[{self.trace_id}] Search input selector timeout, attempting fill anyway")
                
                # Try Ionic-aware fill first (for ion-input, ion-searchbar)
                if 'ion-' in search_input_selector:
                    filled = await self._fill_ionic_search(query, search_input_selector)
                    if not filled:
                        # Fallback to regular fill
                        try:
                            await self.page.fill(search_input_selector, query)
                        except:
                            logger.warning(f"[{self.trace_id}] Could not fill search input")
                else:
                    # Regular input - use standard fill
                    await self.page.fill(search_input_selector, query)
                
                await asyncio.sleep(random.uniform(0.5, 1))
                
                if search_button_selector:
                    logger.info(f"[{self.trace_id}] Submitting search")
                    await self.page.click(search_button_selector)
                    await asyncio.sleep(random.uniform(2, 3))
                    await self.page.wait_for_load_state("networkidle", timeout=15000)
            
        except Exception as e:
            logger.warning(f"[{self.trace_id}] Search execution error: {e}")
            # Continue anyway - maybe we're already on the right page
    
    async def _extract_data(self, query: str) -> Dict:
        """
        Extract data from current page using configured strategies.
        
        Args:
            query: Original query (for context)
            
        Returns:
            Dict with extracted data and metadata
        """
        extraction_config = self.config.get('extraction', {})
        strategies = extraction_config.get('strategies', [])
        
        if not strategies:
            raise ScraperException("No extraction strategies configured")
        
        logger.info(f"[{self.trace_id}] Extracting data with {len(strategies)} strategies")
        
        try:
            # Try each strategy until one works
            extractor = await self.extractor_registry.select_extractor(self.page, strategies)
            
            # Extract data
            raw_data = await extractor.extract(self.page)
            
            logger.info(f"[{self.trace_id}] Extracted {len(raw_data)} records")
            
            return {
                'raw_data': raw_data,
                'citation': {
                    'source_name': self.config.get('name'),
                    'source_url': self.page.url,
                    'retrieved_on': datetime.now().isoformat() + 'Z'
                },
                'summary': f"Retrieved {len(raw_data)} results from {self.config.get('name')} for query: {query}"
            }
            
        except Exception as e:
            logger.error(f"[{self.trace_id}] Data extraction failed: {e}")
            raise ScraperException(f"Data extraction failed: {str(e)}")
    
    async def query(self, query: str) -> Dict:
        """
        Main query method: orchestrates authentication, search, and extraction.
        
        Args:
            query: Search query string
            
        Returns:
            Dict with extracted data and metadata
        """
        try:
            # Initialize browser if not already done
            if not self.browser:
                await self._init_browser()
            
            # Try to validate existing session
            session_valid = await self._validate_session()
            
            # Login if session invalid
            if not session_valid:
                await self._login()
            
            # Perform search
            await self._perform_search(query)
            
            # Extract data
            result = await self._extract_data(query)
            
            # Save session (may have been updated)
            if self.context:
                await self.session_manager.save_session(self.context)
            
            return result
            
        except ScraperException:
            # Re-raise scraper exceptions
            raise
        except Exception as e:
            logger.error(f"[{self.trace_id}] Query failed: {e}", exc_info=True)
            raise ScraperException(f"Query execution failed: {str(e)}")
    
    async def cleanup(self):
        """Clean up browser resources."""
        logger.info(f"[{self.trace_id}] Cleaning up resources")
        
        try:
            if self.page:
                await self.page.close()
                self.page = None
        except Exception as e:
            logger.warning(f"[{self.trace_id}] Error closing page: {e}")
        
        try:
            if self.context:
                await self.context.close()
                self.context = None
        except Exception as e:
            logger.warning(f"[{self.trace_id}] Error closing context: {e}")
        
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
        except Exception as e:
            logger.warning(f"[{self.trace_id}] Error closing browser: {e}")
        
        try:
            if self.playwright:
                # Optional: keep browser open for debugging
                keep_open = os.getenv('PLAYWRIGHT_KEEP_OPEN', 'false').lower() == 'true'
                if keep_open:
                    logger.info(f"[{self.trace_id}] Keeping browser open for 30s (PLAYWRIGHT_KEEP_OPEN=true)")
                    await asyncio.sleep(30)
                
                await self.playwright.stop()
                self.playwright = None
        except Exception as e:
            logger.warning(f"[{self.trace_id}] Error stopping playwright: {e}")
