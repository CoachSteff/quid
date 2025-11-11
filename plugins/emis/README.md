# EMIS Plugin for Quid MCP

**VITO Environmental Information System** (Energie- en Milieu-Informatiesysteem)

## Overview

The EMIS plugin provides access to the VITO EMIS portal, Belgium's comprehensive environmental and energy information system. It contains information about environmental legislation, best available techniques (BBT/BAT), permits, and environmental impact assessments.

## Category

🌍 Environmental

## Authentication

- **Scenario**: Simple Form Login
- **Requirements**: EMIS portal account credentials (email + password)
- **Human Intervention**: Initial credential setup required

## Credentials Setup

Set the following environment variables:

```bash
export EMIS_EMAIL=your_email@example.com
export EMIS_PASSWORD=your_password
```

Or add to your `.env` file:

```env
EMIS_EMAIL=your_email@example.com
EMIS_PASSWORD=your_password
```

## Usage

### CLI

```bash
# Check authentication
quid auth test emis

# Query EMIS
quid query emis "BBT water treatment"

# JSON output
quid query emis "environmental permits" --format json
```

### API

```bash
# Query EMIS via REST API
curl -X POST http://localhost:91060/query/emis \
  -H "Content-Type: application/json" \
  -d '{"query": "BBT water treatment"}'
```

### MCP (Claude Desktop)

Once configured, simply ask Claude:

> "Query EMIS for information about water treatment techniques"

## Extracted Content

The EMIS plugin can extract:

- **Tables**: Search results, legislation tables, permit information
- **Content**: Article text, regulatory documents, technical descriptions
- **Documents**: Links to detail pages, PDFs, downloadable reports
- **Raw Text**: Fallback for unstructured content

## Technical Details

- **Base URL**: https://emis.vito.be
- **Search URL**: https://navigator.emis.vito.be/zoek
- **Login URL**: https://navigator.emis.vito.be/aanmelden
- **Technology**: Ionic Framework (web components)
- **Session TTL**: 1 hour
- **Rate Limit**: 10 requests/minute

## Known Issues

- EMIS uses Ionic Framework with shadow DOM, requiring specialized selectors
- Login page redirects instead of using modals
- Cookie consent popups may appear on first access

## Support

For issues specific to the EMIS plugin, please check:
- [EMIS Portal](https://emis.vito.be) for service status
- [VITO Contact](https://vito.be/en/contact) for account issues

## License

Plugin code: MIT License  
Content: Public sector information (Belgium)
