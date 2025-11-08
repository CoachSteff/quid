#!/usr/bin/env python3
"""
Command-line interface for the generic web scraping framework.
Provides easy terminal access for testing and scripting.
"""

import asyncio
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()  # Try to find .env in parent directories
except ImportError:
    pass  # python-dotenv not installed, environment variables must be set manually

from core import GenericScraper, ScraperException, get_config_loader, ConfigurationException
from credentials import get_credential_manager


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def print_json(data: dict, pretty: bool = True):
    """Print JSON data to stdout."""
    if pretty:
        print(json.dumps(data, indent=2))
    else:
        print(json.dumps(data))


def print_error(message: str):
    """Print error message to stderr."""
    print(f"ERROR: {message}", file=sys.stderr)


async def list_sites():
    """List all available site configurations."""
    try:
        config_loader = get_config_loader()
        sites = config_loader.list_sites()
        
        if not sites:
            print("No sites configured. Add YAML files to backend/sites/")
            return 0
        
        print(f"\nAvailable Sites ({len(sites)}):")
        print("-" * 60)
        
        for site_id in sites:
            try:
                info = config_loader.get_site_info(site_id)
                print(f"\n  {site_id}")
                print(f"    Name: {info['name']}")
                print(f"    URL:  {info['base_url']}")
                if info.get('description'):
                    print(f"    Info: {info['description']}")
            except Exception as e:
                print(f"  {site_id} - ERROR: {e}")
        
        print()
        return 0
        
    except Exception as e:
        print_error(f"Failed to list sites: {e}")
        return 1


async def show_site_config(site_id: str):
    """Show configuration for a specific site."""
    try:
        config_loader = get_config_loader()
        config = config_loader.load_site(site_id)
        
        print(f"\nConfiguration for '{site_id}':")
        print("-" * 60)
        print_json(config)
        return 0
        
    except ConfigurationException as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Failed to load config: {e}")
        return 1


async def check_credentials(site_id: str):
    """Check if credentials are available for a site."""
    try:
        config_loader = get_config_loader()
        config = config_loader.load_site(site_id)
        
        auth_config = config.get('auth', {})
        auth_type = auth_config.get('type', 'none')
        
        print(f"\nCredential Check for '{site_id}':")
        print("-" * 60)
        print(f"Auth Type: {auth_type}")
        
        if auth_type == 'none':
            print("Status: No authentication required")
            return 0
        
        # Check credentials
        cred_manager = get_credential_manager()
        credentials = cred_manager.get_credentials(site_id)
        
        if not credentials:
            print("Status: ❌ No credentials found")
            print(f"\nSet credentials with environment variables:")
            print(f"  export {site_id.upper()}_EMAIL=your_email")
            print(f"  export {site_id.upper()}_PASSWORD=your_password")
            return 1
        
        print("Status: ✅ Credentials found")
        print("\nAvailable fields:")
        for key in credentials.keys():
            if key in ['password', 'api_key', 'token']:
                print(f"  {key}: ******")
            elif key == 'email':
                email = credentials[key]
                print(f"  {key}: {email[:3]}***{email[-10:] if len(email) > 13 else '***'}")
            else:
                print(f"  {key}: {credentials[key][:20]}...")
        
        return 0
        
    except ConfigurationException as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Failed to check credentials: {e}")
        return 1


async def query_site(site_id: str, query: str, output_format: str = 'summary', raw: bool = False):
    """
    Query a site and display results.
    
    Args:
        site_id: Site identifier
        query: Search query
        output_format: Output format (summary, json, table, raw)
        raw: Show raw data only
    """
    try:
        print(f"Querying '{site_id}' for: {query}", file=sys.stderr)
        print("Please wait...", file=sys.stderr)
        
        async with GenericScraper(site_id) as scraper:
            result = await asyncio.wait_for(
                scraper.query(query),
                timeout=120.0
            )
        
        # Output based on format
        if raw or output_format == 'raw':
            print_json(result, pretty=True)
            return 0
        
        if output_format == 'json':
            print_json({
                'status': 'success',
                'citation': result.get('citation'),
                'summary': result.get('summary'),
                'results_count': len(result.get('raw_data', []))
            }, pretty=True)
            return 0
        
        if output_format == 'table':
            raw_data = result.get('raw_data', [])
            if raw_data:
                print("\nResults:")
                print("-" * 60)
                for idx, row in enumerate(raw_data, 1):
                    print(f"\n[{idx}]")
                    for key, value in row.items():
                        # Truncate long values
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:100] + "..."
                        print(f"  {key}: {value}")
            else:
                print("No results found.")
            return 0
        
        # Default: summary format
        summary = result.get('summary', '')
        citation = result.get('citation', {})
        raw_data = result.get('raw_data', [])
        
        print("\n" + "=" * 60)
        print("QUERY RESULTS")
        print("=" * 60)
        
        if summary:
            print(f"\nSummary: {summary}")
        
        print(f"\nResults: {len(raw_data)} records found")
        
        if citation:
            print(f"\nSource: {citation.get('source_name')}")
            print(f"URL: {citation.get('source_url')}")
            print(f"Retrieved: {citation.get('retrieved_on')}")
        
        # Show first few results
        if raw_data:
            print("\nTop Results:")
            print("-" * 60)
            for idx, row in enumerate(raw_data[:5], 1):
                print(f"\n[{idx}]")
                for key, value in row.items():
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    print(f"  {key}: {value}")
            
            if len(raw_data) > 5:
                print(f"\n... and {len(raw_data) - 5} more results")
                print(f"Use --format=raw to see all data")
        
        print("\n" + "=" * 60)
        return 0
        
    except asyncio.TimeoutError:
        print_error("Query timeout - operation took too long")
        return 1
    except ScraperException as e:
        print_error(f"Scraping error: {e}")
        return 1
    except ConfigurationException as e:
        print_error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        print_error(f"Query failed: {e}")
        logging.exception("Full error:")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generic Web Scraping CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available sites
  %(prog)s list
  
  # Show site configuration
  %(prog)s config emis
  
  # Check credentials
  %(prog)s check emis
  
  # Query a site (default format)
  %(prog)s query emis "BBT water treatment"
  
  # Query with JSON output
  %(prog)s query emis "search term" --format json
  
  # Query with raw data
  %(prog)s query emis "search term" --raw
  
  # Verbose mode for debugging
  %(prog)s query emis "search term" -v
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    subparsers.add_parser('list', help='List all available sites')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Show site configuration')
    config_parser.add_argument('site_id', help='Site identifier')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check credentials for a site')
    check_parser.add_argument('site_id', help='Site identifier')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query a site')
    query_parser.add_argument('site_id', help='Site identifier (e.g., emis)')
    query_parser.add_argument('query', help='Search query')
    query_parser.add_argument('--format', choices=['summary', 'json', 'table', 'raw'],
                              default='summary', help='Output format (default: summary)')
    query_parser.add_argument('--raw', action='store_true',
                              help='Show complete raw response (same as --format=raw)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show help if no command
    if not args.command:
        parser.print_help()
        return 0
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Execute command
    if args.command == 'list':
        return asyncio.run(list_sites())
    
    elif args.command == 'config':
        return asyncio.run(show_site_config(args.site_id))
    
    elif args.command == 'check':
        return asyncio.run(check_credentials(args.site_id))
    
    elif args.command == 'query':
        return asyncio.run(query_site(
            args.site_id,
            args.query,
            output_format=args.format,
            raw=args.raw
        ))
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        logging.exception("Full error:")
        sys.exit(1)
