# Changelog

All notable changes to this project will be documented in this file.

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

### Deprecated
- **Claude Skill** (`emis-skill/`) - Deprecated in favor of MCP Server
  - Claude Skill directory, zip file, and specification have been moved to `docs/archived/` for historical reference
  - Users should migrate to MCP Server for Claude Desktop integration
  - See [MCP_CLAUDE_DESKTOP_SETUP.md](MCP_CLAUDE_DESKTOP_SETUP.md) for migration instructions

### Changed
- Updated all documentation to remove Claude Skill references
- Enhanced USER_GUIDE.md with equal prominence for MCP Server and CLI methods
- Updated QUICKSTART.md to focus on MCP Server and CLI equally
- Improved non-technical user guidance with clear "Choose Your Method" sections

### Documentation
- Removed Claude Skill from README.md architecture section
- Updated project structure documentation
- Added deprecation notices in supporting documentation
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

- **1.1.0** - Claude Skill deprecation, documentation improvements (2025-11-08)
- **1.0.0** - Initial public release (2024-11-06)
