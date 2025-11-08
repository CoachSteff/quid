#!/usr/bin/env python3
"""
Session management with file locking support for concurrent access.
Handles browser session persistence across multiple scraping requests.
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional
from playwright.async_api import BrowserContext

logger = logging.getLogger(__name__)

# Platform-specific imports for file locking
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False


class SessionManager:
    """
    Manages session persistence for web scraping with file locking.
    
    Features:
    - Per-site session storage (no collisions)
    - File locking for concurrent access (Unix and Windows)
    - Session validation and TTL support
    """
    
    def __init__(self, site_id: str, session_dir: Optional[str] = None, config: Optional[Dict] = None):
        """
        Initialize session manager for a specific site.
        
        Args:
            site_id: Unique identifier for the site (used in filename)
            session_dir: Directory for session files (default: data/sessions/)
            config: Site configuration (for TTL and validation settings)
        """
        self.site_id = site_id
        self.config = config or {}
        
        # Make session directory configurable via environment variable
        default_dir = os.getenv("SESSION_DIR", "data/sessions")
        self.session_dir = Path(session_dir or default_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Session file per site
        self.session_file = self.session_dir / f"{site_id}.json"
        
        logger.info(f"SessionManager initialized for site '{site_id}': {self.session_file}")
    
    def _lock_file(self, file_handle, exclusive: bool = False):
        """
        Lock file for safe concurrent access (cross-platform).
        
        Args:
            file_handle: File handle to lock
            exclusive: True for exclusive lock (write), False for shared lock (read)
        """
        if HAS_FCNTL:
            # Unix/Linux/Mac
            lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.flock(file_handle.fileno(), lock_type)
        elif HAS_MSVCRT:
            # Windows
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            # No locking available
            logger.warning("File locking not available on this platform")
    
    def _unlock_file(self, file_handle):
        """
        Unlock file (cross-platform).
        
        Args:
            file_handle: File handle to unlock
        """
        if HAS_FCNTL:
            fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
        elif HAS_MSVCRT:
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
    
    def load_session(self) -> Optional[Dict]:
        """
        Load session from file if it exists (with file locking).
        
        Returns:
            Session data dict, or None if file doesn't exist or is invalid
        """
        if not self.session_file.exists():
            logger.info(f"No session file found for site '{self.site_id}'")
            return None
        
        try:
            with open(self.session_file, 'r') as f:
                try:
                    # Acquire shared lock for reading
                    self._lock_file(f, exclusive=False)
                    data = json.load(f)
                    self._unlock_file(f)
                    
                    logger.info(f"Session loaded successfully for site '{self.site_id}'")
                    return data
                    
                except Exception as e:
                    # Unlock on error
                    try:
                        self._unlock_file(f)
                    except:
                        pass
                    raise e
                    
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse session file for '{self.site_id}': {e}")
            # Delete corrupted session file
            self.delete_session()
            return None
            
        except Exception as e:
            logger.warning(f"Failed to load session for '{self.site_id}': {e}")
            return None
    
    def is_session_expired(self) -> bool:
        """
        Check if session has exceeded TTL without making network call.
        
        Returns:
            True if session is expired or doesn't exist
        """
        if not self.session_file.exists():
            return True
        
        try:
            # Get file modification time
            mtime = self.session_file.stat().st_mtime
            age_seconds = time.time() - mtime
            
            # Get TTL from config (default 1 hour)
            ttl_seconds = self.config.get('session', {}).get('ttl_seconds', 3600)
            
            is_expired = age_seconds > ttl_seconds
            
            if is_expired:
                logger.debug(f"Session for '{self.site_id}' expired (age: {age_seconds:.0f}s, TTL: {ttl_seconds}s)")
            else:
                logger.debug(f"Session for '{self.site_id}' still valid (age: {age_seconds:.0f}s, TTL: {ttl_seconds}s)")
            
            return is_expired
            
        except Exception as e:
            logger.warning(f"Failed to check session age for '{self.site_id}': {e}")
            return True  # Assume expired on error
    
    async def save_session(self, context: BrowserContext):
        """
        Save browser context state to file (with file locking).
        
        Args:
            context: Playwright BrowserContext to persist
        """
        try:
            # Get session state from browser context
            session_state = await context.storage_state()
            
            # Write with exclusive lock
            with open(self.session_file, 'w') as f:
                try:
                    # Acquire exclusive lock for writing
                    self._lock_file(f, exclusive=True)
                    json.dump(session_state, f, indent=2)
                    self._unlock_file(f)
                    
                    logger.info(f"Session saved successfully for site '{self.site_id}'")
                    
                except Exception as e:
                    # Unlock on error
                    try:
                        self._unlock_file(f)
                    except:
                        pass
                    raise e
                    
        except Exception as e:
            logger.error(f"Failed to save session for '{self.site_id}': {e}")
            raise
    
    def delete_session(self):
        """
        Delete session file (for logout or cleanup).
        """
        try:
            if self.session_file.exists():
                self.session_file.unlink()
                logger.info(f"Session deleted for site '{self.site_id}'")
        except Exception as e:
            logger.warning(f"Failed to delete session for '{self.site_id}': {e}")
    
    def session_exists(self) -> bool:
        """
        Check if session file exists.
        
        Returns:
            True if session file exists
        """
        return self.session_file.exists()
