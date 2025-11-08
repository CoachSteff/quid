#!/usr/bin/env python3
"""
Claude Skill execution script for EMIS portal queries.
This script is called by Claude when the skill is triggered.
"""

import os
import sys
import json
import requests
from typing import Optional


def get_user_query() -> str:
    """
    Get the user's query from environment variable or command line argument.
    
    Claude Skills typically pass the query via:
    - CLAUDE_PROMPT environment variable, or
    - Command line argument
    """
    # Try environment variable first
    query = os.environ.get("CLAUDE_PROMPT") or os.environ.get("QUERY")
    
    # Try command line argument
    if not query and len(sys.argv) > 1:
        query = sys.argv[1]
    
    # Fallback: read from stdin if available
    if not query:
        try:
            query = sys.stdin.read().strip()
        except:
            pass
    
    if not query:
        return json.dumps({
            "status": "error",
            "error_message": "No query provided. Please provide a query via CLAUDE_PROMPT environment variable or command line argument."
        })
    
    return query


def call_backend_api(query: str) -> dict:
    """
    Call the backend API to execute the EMIS query.
    
    Args:
        query: The search query string
        
    Returns:
        dict: JSON response from the backend API
    """
    # Get backend URL from environment or use default
    backend_url = os.environ.get("EMIS_BACKEND_URL", "http://localhost:38153")
    api_key = os.environ.get("EMIS_API_KEY")  # Optional API key for future use
    
    endpoint = f"{backend_url}/query"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Add API key if configured
    if api_key:
        headers["X-API-Key"] = api_key
    
    payload = {
        "query": query
    }
    
    try:
        # Make request with timeout
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=90  # Allow up to 90 seconds for scraping (handles auth + search)
        )
        
        # Raise error for bad status codes
        response.raise_for_status()
        
        # Return JSON response
        return response.json()
        
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "error_message": "Request timed out. The EMIS portal query took too long to complete."
        }
    except requests.exceptions.ConnectionError as e:
        backend_url = os.environ.get("EMIS_BACKEND_URL", "http://localhost:38153")
        
        # Try fallback to direct scraping if enabled
        use_direct_fallback = os.getenv("EMIS_USE_DIRECT_FALLBACK", "true").lower() == "true"
        
        if use_direct_fallback:
            # Attempt direct scraping as fallback
            try:
                # Import the direct scraper
                from run_query_direct import scrape_directly
                result = scrape_directly(query)
                if result.get("status") == "success":
                    return result
                # If direct scraping also fails, return combined error message
                return {
                    "status": "error",
                    "error_message": (
                        f"Backend API unavailable at {backend_url} and direct scraping also failed.\n\n"
                        f"Backend error: Could not connect to backend service.\n"
                        f"Direct scraping error: {result.get('error_message', 'Unknown error')}\n\n"
                        "To use backend mode:\n"
                        "1. Navigate to backend directory: cd backend\n"
                        "2. Copy .env.example to .env and add EMIS credentials\n"
                        "3. Start with: docker-compose up OR python app.py\n\n"
                        "To use direct mode:\n"
                        "1. Install: pip install playwright playwright-stealth\n"
                        "2. Install browser: playwright install chromium\n"
                        "3. Set EMIS_EMAIL and EMIS_PASSWORD environment variables"
                    )
                }
            except ImportError:
                # Direct scraper not available
                pass
            except Exception as e:
                # Direct scraping failed
                pass
        
        # Return backend connection error
        return {
            "status": "error",
            "error_message": (
                f"Could not connect to backend API at {backend_url}. "
                "The EMIS backend service is not running or not accessible.\n\n"
                "To start the backend service:\n"
                "1. Navigate to the backend directory: cd backend\n"
                "2. Copy .env.example to .env and add your EMIS credentials\n"
                "3. Start with Docker: docker-compose up\n"
                "   OR run locally: python app.py\n\n"
                "The backend should be running on port 38153 by default.\n"
                "You can also set EMIS_BACKEND_URL environment variable to use a different endpoint.\n\n"
                "Alternatively, set EMIS_USE_DIRECT_FALLBACK=false to disable direct scraping fallback."
            )
        }
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_json = e.response.json()
            error_detail = error_json.get("detail", e.response.text)
        except:
            error_detail = e.response.text or f"HTTP {e.response.status_code}"
        
        # Provide helpful messages for common HTTP errors
        if e.response.status_code == 401:
            error_detail += "\n\nNote: API key authentication may be required. Set EMIS_API_KEY environment variable."
        elif e.response.status_code == 500:
            error_detail += "\n\nNote: The backend may be misconfigured. Check that EMIS_EMAIL and EMIS_PASSWORD are set correctly."
        
        return {
            "status": "error",
            "error_message": f"Backend API error ({e.response.status_code}): {error_detail}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}"
        }


def main():
    """
    Main entry point for the skill script.
    """
    # Get user query
    query = get_user_query()
    
    # If query is already a JSON error, print and exit
    if isinstance(query, str) and query.startswith('{"status": "error"'):
        print(query)
        sys.exit(1)
    
    # Call backend API
    result = call_backend_api(query)
    
    # Print JSON result to stdout (Claude will read this)
    print(json.dumps(result, indent=2))
    
    # Exit with error code if status is error
    if result.get("status") == "error":
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()

