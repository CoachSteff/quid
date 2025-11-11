#!/usr/bin/env python3
"""
Performance tests for Phase 2 Integration.

Tests that plugin system doesn't introduce significant performance overhead.
"""

import pytest
import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))


@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Performance tests."""
    
    def test_plugin_loading_performance(self):
        """TC-PERF-002: Plugin Loading Performance."""
        from core.plugin_manager import get_plugin_manager
        
        start_time = time.time()
        plugin_manager = get_plugin_manager()
        plugins = plugin_manager.get_all_plugins()
        end_time = time.time()
        
        elapsed = (end_time - start_time) * 1000  # Convert to ms
        
        # Should load plugins in < 100ms
        assert elapsed < 100, f"Plugin loading took {elapsed}ms, expected < 100ms"
        assert len(plugins) > 0
    
    def test_plugin_query_performance(self):
        """TC-PERF-001: Plugin Query Performance."""
        # This test requires actual query execution, so it's marked as slow
        # and may require credentials
        pytest.skip("Requires actual query execution - run manually with credentials")
    
    def test_scraper_initialization_performance(self):
        """Test scraper initialization performance."""
        from core.scraper import GenericScraper
        
        start_time = time.time()
        scraper = GenericScraper('emis')
        end_time = time.time()
        
        elapsed = (end_time - start_time) * 1000  # Convert to ms
        
        # Should initialize in < 50ms
        assert elapsed < 50, f"Scraper initialization took {elapsed}ms, expected < 50ms"
        assert scraper.config is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])

