#!/usr/bin/env python3
"""
Unit tests for Authentication Registry.

Tests auth strategy registration, retrieval, and management.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from core.auth_registry import AuthRegistry, register_auth_strategy
from auth.base import AuthStrategy


class MockAuthStrategy(AuthStrategy):
    """Mock authentication strategy for testing."""
    
    async def login(self, page, context):
        return True
    
    async def validate_session(self, page):
        return True


class TestAuthRegistry:
    """Test authentication registry functionality."""
    
    def setup_method(self):
        """Clear registry before each test."""
        # Note: In production, you might not want to clear the registry
        # This is just for testing isolation
        pass
    
    def test_register_strategy(self):
        """TC-AR-001: Test registering a new auth strategy."""
        AuthRegistry.register('test_scenario', MockAuthStrategy)
        
        assert 'test_scenario' in AuthRegistry.list_scenarios()
    
    def test_get_registered_strategy(self):
        """TC-AR-002: Test retrieving registered strategy."""
        AuthRegistry.register('test_get', MockAuthStrategy)
        
        strategy = AuthRegistry.get('test_get')
        
        assert strategy is not None
        assert strategy == MockAuthStrategy
    
    def test_get_nonexistent_strategy(self):
        """TC-AR-003: Test getting unregistered strategy returns None."""
        strategy = AuthRegistry.get('nonexistent_strategy_xyz')
        
        assert strategy is None
    
    def test_list_all_scenarios(self):
        """TC-AR-004: Test listing all registered scenarios."""
        scenarios = AuthRegistry.list_scenarios()
        
        assert isinstance(scenarios, list)
        # Should have at least the built-in strategies
        assert len(scenarios) > 0
    
    def test_is_registered(self):
        """Test checking if scenario is registered."""
        AuthRegistry.register('test_check', MockAuthStrategy)
        
        assert AuthRegistry.is_registered('test_check') is True
        assert AuthRegistry.is_registered('not_registered') is False


class TestBuiltInStrategies:
    """Test that built-in strategies are registered."""
    
    def test_simple_form_registered(self):
        """TC-AR-005: Verify simple_form strategy is registered."""
        assert AuthRegistry.is_registered('simple_form')
        
        strategy = AuthRegistry.get('simple_form')
        assert strategy is not None
    
    def test_form_based_registered(self):
        """TC-AR-005: Verify form_based (legacy) strategy is registered."""
        assert AuthRegistry.is_registered('form_based')
        
        strategy = AuthRegistry.get('form_based')
        assert strategy is not None
    
    def test_api_key_registered(self):
        """TC-AR-005: Verify api_key strategy is registered."""
        assert AuthRegistry.is_registered('api_key')
        
        strategy = AuthRegistry.get('api_key')
        assert strategy is not None
    
    def test_none_registered(self):
        """TC-AR-005: Verify none strategy is registered."""
        assert AuthRegistry.is_registered('none')
        
        strategy = AuthRegistry.get('none')
        assert strategy is not None
    
    def test_all_expected_strategies_present(self):
        """Test that all expected built-in strategies are present."""
        scenarios = AuthRegistry.list_scenarios()
        
        expected = ['simple_form', 'form_based', 'api_key', 'none']
        
        for expected_scenario in expected:
            assert expected_scenario in scenarios, \
                f"Expected scenario '{expected_scenario}' not found in registry"


class TestRegistryDecorator:
    """Test decorator-based registration."""
    
    def test_decorator_registration(self):
        """Test @register_auth_strategy decorator."""
        
        @register_auth_strategy('decorator_test')
        class DecoratorTestAuth(AuthStrategy):
            async def login(self, page, context):
                return True
            
            async def validate_session(self, page):
                return True
        
        assert AuthRegistry.is_registered('decorator_test')
        
        strategy = AuthRegistry.get('decorator_test')
        assert strategy == DecoratorTestAuth


class TestRegistryEdgeCases:
    """Test edge cases and error handling."""
    
    def test_overwrite_strategy_succeeds(self):
        """TC-AR-006: Test that overwriting strategy works (with warning)."""
        
        class Strategy1(AuthStrategy):
            async def login(self, page, context):
                return True
            async def validate_session(self, page):
                return True
        
        class Strategy2(AuthStrategy):
            async def login(self, page, context):
                return False
            async def validate_session(self, page):
                return False
        
        AuthRegistry.register('overwrite_test', Strategy1)
        AuthRegistry.register('overwrite_test', Strategy2)
        
        # Should get the second one
        strategy = AuthRegistry.get('overwrite_test')
        assert strategy == Strategy2
    
    def test_empty_scenario_name(self):
        """Test registering with empty scenario name."""
        AuthRegistry.register('', MockAuthStrategy)
        
        # Should still work, though not recommended
        assert AuthRegistry.is_registered('')
    
    def test_case_sensitive_scenarios(self):
        """Test that scenario names are case-sensitive."""
        AuthRegistry.register('TestCase', MockAuthStrategy)
        
        assert AuthRegistry.is_registered('TestCase')
        assert not AuthRegistry.is_registered('testcase')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
