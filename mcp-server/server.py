#!/usr/bin/env python3
"""
MCP Server for EMIS Backend
Provides tools for querying the VITO EMIS portal via the backend API.
"""

import os
import sys
import json
import logging
import requests
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
env_paths = [
    Path(__file__).parent.parent / "backend" / ".env",
    Path(__file__).parent / ".env",
    Path(".env"),
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded .env from: {env_path}")
        break
else:
    load_dotenv()

# Create MCP server instance
mcp = FastMCP("EMIS Backend MCP Server")

# Configuration
BACKEND_URL = os.getenv("EMIS_BACKEND_URL", "http://localhost:38153")
API_KEY = os.getenv("EMIS_API_KEY")  # Optional


def call_backend_api(query: str) -> dict:
    """
    Call the EMIS backend API to execute a query.
    
    Args:
        query: The search query string
        
    Returns:
        dict: Response from the backend API
    """
    endpoint = f"{BACKEND_URL}/query"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    
    payload = {
        "query": query
    }
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=120  # Allow up to 120 seconds for scraping
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "error_message": "Request timed out. The EMIS portal query took too long to complete."
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "error_message": (
                f"Could not connect to EMIS backend at {BACKEND_URL}. "
                "Please ensure the backend service is running."
            )
        }
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_json = e.response.json()
            error_detail = error_json.get("detail", e.response.text)
        except:
            error_detail = e.response.text or f"HTTP {e.response.status_code}"
        
        return {
            "status": "error",
            "error_message": f"Backend API error ({e.response.status_code}): {error_detail}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}"
        }


@mcp.tool()
def query_emis(query: str) -> dict:
    """
    Query the VITO EMIS portal for environmental and energy data.
    
    This tool performs a live, authenticated query against the EMIS portal
    and returns structured results including citations, summaries, and raw data.
    
    Args:
        query: Natural language query about EMIS data (e.g., "Find recent BBT updates for water treatment",
               "What does EMIS say about waste management legislation?", "Search EMIS for information about...")
    
    Returns:
        dict: Response containing:
            - status: "success" or "error"
            - timestamp: ISO timestamp of the query
            - citation: Source information (source_name, source_url, retrieved_on)
            - summary: AI-generated summary of findings
            - raw_data: List of structured data records
            - error_message: Error details (if status is "error")
    
    Example:
        query_emis("Find BBT information for wastewater treatment")
    """
    logger.info(f"EMIS query received: {query}")
    result = call_backend_api(query)
    logger.info(f"EMIS query completed with status: {result.get('status')}")
    return result


@mcp.tool()
def check_backend_health() -> dict:
    """
    Check if the EMIS backend service is running and accessible.
    
    Returns:
        dict: Health status with backend URL and availability
    """
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        response.raise_for_status()
        return {
            "status": "healthy",
            "backend_url": BACKEND_URL,
            "message": "EMIS backend is running and accessible"
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "unavailable",
            "backend_url": BACKEND_URL,
            "message": f"EMIS backend is not accessible at {BACKEND_URL}. Please start the backend service."
        }
    except Exception as e:
        return {
            "status": "error",
            "backend_url": BACKEND_URL,
            "message": f"Error checking backend health: {str(e)}"
        }


# Add resource for backend configuration info
@mcp.resource("emis://backend/config")
def get_backend_config() -> str:
    """
    Get the current backend configuration.
    """
    config = {
        "backend_url": BACKEND_URL,
        "api_key_configured": API_KEY is not None,
    }
    return json.dumps(config, indent=2)


if __name__ == "__main__":
    # Run the server using stdio transport (standard for MCP)
    # This allows Claude Desktop to communicate with the server
    import asyncio
    
    logger.info(f"Starting EMIS MCP Server")
    logger.info(f"Backend URL: {BACKEND_URL}")
    logger.info(f"API Key configured: {API_KEY is not None}")
    
    # Run the server
    asyncio.run(mcp.run(transport="stdio"))

