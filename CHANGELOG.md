# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0-alpha] - 2025-11-08

### 🎉 Major Transformation: EMIS MCP → Quid MCP

This release transforms the EMIS-specific scraper into **Quid MCP**, a universal content access platform with plugin-based architecture.

### Added

#### Core Architecture
- **Plugin System**: Complete plugin manager with discovery, loading, and validation
- **Plugin Registry**: Self-contained plugins with YAML configuration
- **Auth Registry**: Centralized authentication strategy management
- **Multi-scenario Auth**: Support for simple forms, API keys, OAuth 2.0, CAPTCHA, MFA

#### Authentication Strategies
- **API Key Auth**: Header, query parameter, and bearer token support
- **None Auth**: For public websites without authentication
- **Enhanced Form Auth**: Maintained with improvements

#### Plugins
- **EMIS Plugin**: Migrated EMIS to plugin architecture (`plugins/emis/`)
- **Plugin Template**: Complete template for creating new plugins (`plugins/template/`)

#### Documentation
- **Ethical Guidelines**: Comprehensive ethical framework for responsible use
- **Plugin Development Guide**: Template and documentation for plugin creators
- **Updated README**: New vision, use cases, and plugin-focused structure

### Changed

- **Project Name**: Generic Web Scraping Framework → Quid MCP
- **Project Vision**: "Perplexity for protected documents" - AI-first content access
- **Architecture**: Moved from site configs to plugin system
- **Directory Structure**: New `plugins/` directory for self-contained modules

### Backwards Compatibility

- ✅ All existing EMIS integrations continue to work
- ✅ Legacy `backend/sites/emis.yaml` still supported
- ✅ API endpoints unchanged (`/query`, `/query/emis`)
- ✅ CLI commands unchanged
- ✅ MCP server unchanged

### Migration Path

Existing users can continue using EMIS without changes. New plugin system is opt-in.

### For Contributors

- Plugin-based architecture makes it easy to add new content sources
- Template plugin provides starting point
- Ethical guidelines ensure responsible development

---

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-06

### Added
- 🎉 Initial public release
- Generic multi-site scraping framework with YAML configuration
- Command-line interface (CLI) for easy testing and usage
- REST API with multi-site support
- Pluggable authentication strategies (form-based auth implemented)
- Pluggable data extraction strategies (table and content extractors)
- Session management with file locking for concurrent access
- Per-site credential management
- Comprehensive documentation
- Example site configurations
- Security policy and contributing guidelines

### Changed
- Refactored from EMIS-specific to generic framework
- Improved error handling with proper HTTP status codes
- Enhanced session management to prevent race conditions
- Better resource cleanup with context managers

### Security
- Removed all hardcoded credentials
- Added security best practices documentation
- Improved .gitignore to prevent credential leaks
- Session files properly protected

### Documentation
- User guides for CLI and framework
- Developer documentation for extending the framework
- Quick reference card
- Example scripts and configurations
- GitHub issue and PR templates

## [1.1.0] - 2025-11-08

### Changed
- Enhanced documentation with equal prominence for MCP Server and CLI methods
- Improved non-technical user guidance with clear "Choose Your Method" sections

### Documentation
- Updated project structure documentation
- Enhanced MCP Server setup instructions
- Improved CLI usage examples for non-technical users

## [Unreleased]

### Planned
- OAuth authentication strategy
- API token authentication
- Cookie-based authentication
- Pagination support
- Result caching
- Browser pooling for better performance
- Async task queue
- Monitoring and metrics

---

## Version History

- **1.1.0** - Documentation improvements (2025-11-08)
- **1.0.0** - Initial public release (2024-11-06)
