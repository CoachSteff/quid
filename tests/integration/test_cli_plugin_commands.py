#!/usr/bin/env python3
"""
Integration tests for CLI Plugin Commands.

Tests CLI plugin management commands work correctly.
"""

import pytest
import sys
import subprocess
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))


@pytest.mark.integration
class TestCLIPluginCommands:
    """Test CLI plugin management commands."""
    
    @pytest.fixture
    def cli_path(self):
        """Path to CLI script."""
        return Path(__file__).parent.parent.parent / "backend" / "cli.py"
    
    def test_list_plugins(self, cli_path):
        """TC-CLI-001: List Plugins."""
        result = subprocess.run(
            [sys.executable, str(cli_path), "plugin", "list"],
            capture_output=True,
            text=True,
            cwd=str(cli_path.parent)
        )
        
        assert result.returncode == 0
        assert "Available Plugins" in result.stdout or "No plugins found" in result.stdout
    
    def test_show_plugin_info(self, cli_path):
        """TC-CLI-002: Show Plugin Info."""
        result = subprocess.run(
            [sys.executable, str(cli_path), "plugin", "info", "emis"],
            capture_output=True,
            text=True,
            cwd=str(cli_path.parent)
        )
        
        assert result.returncode == 0
        assert "emis" in result.stdout.lower() or "plugin" in result.stdout.lower()
    
    def test_enable_plugin(self, cli_path):
        """TC-CLI-003: Enable Plugin."""
        result = subprocess.run(
            [sys.executable, str(cli_path), "plugin", "enable", "emis"],
            capture_output=True,
            text=True,
            cwd=str(cli_path.parent)
        )
        
        assert result.returncode == 0
        assert "enabled" in result.stdout.lower()
    
    def test_disable_plugin(self, cli_path):
        """TC-CLI-004: Disable Plugin."""
        result = subprocess.run(
            [sys.executable, str(cli_path), "plugin", "disable", "emis"],
            capture_output=True,
            text=True,
            cwd=str(cli_path.parent)
        )
        
        assert result.returncode == 0
        assert "disabled" in result.stdout.lower()
        
        # Re-enable for other tests
        subprocess.run(
            [sys.executable, str(cli_path), "plugin", "enable", "emis"],
            capture_output=True,
            cwd=str(cli_path.parent)
        )
    
    def test_plugin_not_found(self, cli_path):
        """TC-CLI-005: Plugin Not Found."""
        result = subprocess.run(
            [sys.executable, str(cli_path), "plugin", "info", "nonexistent_plugin_xyz"],
            capture_output=True,
            text=True,
            cwd=str(cli_path.parent)
        )

        assert result.returncode == 1
        # Error messages are written to stderr, not stdout
        error_output = (result.stdout + result.stderr).lower()
        assert "not found" in error_output or "error" in error_output


@pytest.mark.integration
class TestCLIUpdatedCommands:
    """Test updated CLI commands that show plugins."""
    
    @pytest.fixture
    def cli_path(self):
        """Path to CLI script."""
        return Path(__file__).parent.parent.parent / "backend" / "cli.py"
    
    def test_list_shows_plugins_and_legacy(self, cli_path):
        """TC-CLI-006: List Shows Plugins and Legacy."""
        result = subprocess.run(
            [sys.executable, str(cli_path), "list"],
            capture_output=True,
            text=True,
            cwd=str(cli_path.parent)
        )
        
        assert result.returncode == 0
        # Should show plugins section
        output = result.stdout.lower()
        assert "plugin" in output or "legacy" in output or "site" in output
    
    def test_config_shows_plugin_config(self, cli_path):
        """TC-CLI-007: Config Shows Plugin Config."""
        result = subprocess.run(
            [sys.executable, str(cli_path), "config", "emis"],
            capture_output=True,
            text=True,
            cwd=str(cli_path.parent)
        )
        
        assert result.returncode == 0
        # Should show plugin configuration
        assert "emis" in result.stdout.lower()
    
    def test_check_credentials_for_plugin(self, cli_path):
        """TC-CLI-009: Check Credentials for Plugin."""
        result = subprocess.run(
            [sys.executable, str(cli_path), "check", "emis"],
            capture_output=True,
            text=True,
            cwd=str(cli_path.parent)
        )

        # CLI correctly returns exit code 1 when credentials are not found
        # This is the expected behavior - no credentials configured = error state
        assert result.returncode == 1
        # Should show plugin name in output (either stdout or stderr)
        output = (result.stdout + result.stderr).lower()
        assert "emis" in output


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])

