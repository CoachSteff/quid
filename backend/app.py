#!/usr/bin/env python3
"""
FastAPI application for generic web scraping backend.
Supports multiple sites with configurable authentication and extraction strategies.
"""

import os
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn

# Import new generic components
from core import GenericScraper, ScraperException, get_config_loader, ConfigurationException
from credentials import get_credential_manager
from api.models import QueryRequest, QueryResponse, SiteInfo, SiteListResponse, PluginInfo, PluginListResponse

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
# Supports multiple scenarios:
# 1. Local/venv: Loads .env file from backend directory
# 2. Docker: docker-compose sets env vars via env_file, app.py also tries to load .env
# 3. Any scenario: Falls back to system environment variables and hardcoded defaults
env_paths = [
    Path(__file__).parent / "venv" / ".env",  # venv directory (preferred for credentials)
    Path(".env"),  # Current directory (for Docker if .env is copied)
    Path(__file__).parent / ".env",  # Backend directory (where app.py is)
    Path(__file__).parent.parent / "backend" / ".env",  # From project root
]
env_file_loaded = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded .env file from: {env_path}")
        env_file_loaded = True
        break

# If no .env file found, still call load_dotenv() to check for .env in parent directories
# This is useful for Docker where env vars may already be set via docker-compose env_file
if not env_file_loaded:
    load_dotenv()  # May find .env in parent directories or use existing env vars
    # Check if critical env vars are available (from docker-compose or system)
    if os.getenv("EMIS_EMAIL") or os.getenv("EMIS_PASSWORD") or os.getenv("PORT"):
        logger.info("Using environment variables (from docker-compose or system environment)")
    else:
        logger.info("No .env file found, will use hardcoded fallback credentials")

app = FastAPI(
    title="Generic Web Scraping API",
    version="2.0.0-alpha",
    description="Multi-site web scraping with configurable authentication and extraction"
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Quid MCP API starting...")
    
    # Try to load plugin manager (if available)
    try:
        from core.plugin_manager import get_plugin_manager
        plugin_manager = get_plugin_manager()
        plugins = plugin_manager.get_all_plugins()
        
        if plugins:
            logger.info(f"Loaded {len(plugins)} plugin(s):")
            for plugin_id, plugin in plugins.items():
                status = "✓" if plugin.enabled else "○"
                logger.info(f"  {status} {plugin.name} ({plugin_id}) - {plugin.category}")
        else:
            logger.warning("No plugins loaded")
    except Exception as e:
        logger.warning(f"Plugin system not fully initialized: {e}")
    
    # Log available sites (legacy support)
    config_loader = get_config_loader()
    sites = config_loader.list_sites()
    if sites:
        logger.info(f"Legacy sites available: {', '.join(sites)}")

# CORS configuration - permissive for local development
# For local development, allow all origins (containerized environments need this)
# In production, set CORS_ORIGINS to specific domains
cors_origins_env = os.getenv("CORS_ORIGINS", "").strip()

if cors_origins_env == "*" or not cors_origins_env:
    # Development mode: allow all origins
    allowed_origins = ["*"]
    logger.info("CORS: Allowing all origins (development mode)")
else:
    # Production mode: use configured origins
    allowed_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
    logger.info(f"CORS: Allowing configured origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)

# API Key authentication (optional - configure via API_KEY env var)
API_KEY = os.getenv("API_KEY")


@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    """Optional API key authentication for /query endpoint."""
    # Skip auth for health check
    if request.url.path == "/":
        return await call_next(request)
    
    # If API_KEY is configured, require it for /query endpoint
    if API_KEY and request.url.path == "/query":
        api_key = request.headers.get("X-API-Key")
        if api_key != API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key"}
            )
    
    return await call_next(request)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Generic Web Scraping API",
        "version": "2.0.0-alpha"
    }


@app.get("/sites", response_model=SiteListResponse)
async def list_sites():
    """
    List all available site configurations (legacy sites only).
    
    For plugins, use GET /plugins endpoint.
    
    Returns:
        List of available legacy sites with basic information
    """
    try:
        config_loader = get_config_loader()
        site_ids = config_loader.list_sites()
        
        sites = []
        for site_id in site_ids:
            try:
                info = config_loader.get_site_info(site_id)
                sites.append(SiteInfo(**info))
            except Exception as e:
                logger.warning(f"Failed to load info for site '{site_id}': {e}")
                continue
        
        return SiteListResponse(sites=sites, count=len(sites))
        
    except Exception as e:
        logger.error(f"Failed to list sites: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sites: {str(e)}")


@app.get("/plugins", response_model=PluginListResponse)
async def list_plugins():
    """
    List all available plugins.
    
    Returns:
        List of available plugins with detailed information
    """
    try:
        from core.plugin_manager import get_plugin_manager
        plugin_manager = get_plugin_manager()
        plugins = plugin_manager.get_all_plugins()
        
        plugin_list = []
        for plugin_id in plugins.keys():
            info = plugin_manager.get_plugin_info(plugin_id)
            if info:
                plugin_list.append(PluginInfo(**info))
        
        return PluginListResponse(plugins=plugin_list, count=len(plugin_list))
        
    except ImportError:
        logger.warning("Plugin system not available")
        return PluginListResponse(plugins=[], count=0)
    except Exception as e:
        logger.error(f"Failed to list plugins: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list plugins: {str(e)}")


@app.get("/plugins/{plugin_id}", response_model=PluginInfo)
async def get_plugin(plugin_id: str):
    """
    Get detailed information for a specific plugin.
    
    Args:
        plugin_id: Plugin identifier
        
    Returns:
        Plugin information
    """
    try:
        from core.plugin_manager import get_plugin_manager
        plugin_manager = get_plugin_manager()
        info = plugin_manager.get_plugin_info(plugin_id)
        
        if not info:
            raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")
        
        return PluginInfo(**info)
        
    except ImportError:
        raise HTTPException(status_code=503, detail="Plugin system not available")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get plugin info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get plugin info: {str(e)}")


@app.post("/plugins/{plugin_id}/enable")
async def enable_plugin(plugin_id: str):
    """
    Enable a plugin.
    
    Args:
        plugin_id: Plugin identifier
        
    Returns:
        Success message
    """
    try:
        from core.plugin_manager import get_plugin_manager
        plugin_manager = get_plugin_manager()
        
        if plugin_manager.enable_plugin(plugin_id):
            return {"status": "success", "message": f"Plugin '{plugin_id}' enabled"}
        else:
            raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")
        
    except ImportError:
        raise HTTPException(status_code=503, detail="Plugin system not available")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enable plugin: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enable plugin: {str(e)}")


@app.post("/plugins/{plugin_id}/disable")
async def disable_plugin(plugin_id: str):
    """
    Disable a plugin.
    
    Args:
        plugin_id: Plugin identifier
        
    Returns:
        Success message
    """
    try:
        from core.plugin_manager import get_plugin_manager
        plugin_manager = get_plugin_manager()
        
        if plugin_manager.disable_plugin(plugin_id):
            return {"status": "success", "message": f"Plugin '{plugin_id}' disabled"}
        else:
            raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")
        
    except ImportError:
        raise HTTPException(status_code=503, detail="Plugin system not available")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disable plugin: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to disable plugin: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query_default_site(request: QueryRequest):
    """
    Query the default site (EMIS) - for backwards compatibility.
    
    This endpoint maintains compatibility with existing clients.
    """
    return await query_site("emis", request)


@app.post("/query/{site_id}", response_model=QueryResponse)
async def query_site(site_id: str, request: QueryRequest):
    """
    Query a specific site with a search query.
    
    This endpoint:
    1. Takes a site_id and query string
    2. Uses configured authentication and extraction strategies
    3. Returns structured JSON with results
    
    Args:
        site_id: Site identifier (e.g., 'emis', 'example')
        request: Query request with search string
        
    Returns:
        QueryResponse with extracted data
    """
    trace_id = f"trace_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    logger.info(f"[{trace_id}] Query received for site '{site_id}': {request.query}")
    
    try:
        # Validate site exists
        config_loader = get_config_loader()
        try:
            config_loader.load_site(site_id)
        except ConfigurationException as e:
            logger.error(f"[{trace_id}] Site not found: {site_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Site '{site_id}' not found. Use GET /sites to list available sites."
            )
        
        # Execute query with context manager for proper cleanup
        async with GenericScraper(site_id, trace_id) as scraper:
            # Execute query with timeout (120 seconds max)
            result = await asyncio.wait_for(
                scraper.query(request.query),
                timeout=120.0
            )
        
        logger.info(f"[{trace_id}] Query completed successfully")
        
        # Convert documents to Document models if present
        documents = None
        if result.get("documents"):
            from api.models import Document, DocumentMetadata
            documents = []
            for doc in result.get("documents"):
                # Convert metadata dict to DocumentMetadata model
                metadata = None
                if doc.get("metadata"):
                    metadata = DocumentMetadata(**doc.get("metadata"))
                
                documents.append(Document(
                    title=doc.get("title"),
                    url=doc.get("url"),
                    type=doc.get("type"),
                    metadata=metadata,
                    description=doc.get("description"),
                    source=doc.get("source")
                ))
        
        return QueryResponse(
            status="success",
            timestamp=datetime.now().isoformat() + "Z",
            citation=result.get("citation"),
            summary=result.get("summary"),
            raw_data=result.get("raw_data"),
            documents=documents
        )
        
    except asyncio.TimeoutError:
        logger.error(f"[{trace_id}] Query timed out after 120 seconds")
        raise HTTPException(
            status_code=504,
            detail="Query timeout - the operation took too long to complete"
        )
    except ScraperException as e:
        # Scraper-specific errors
        logger.error(f"[{trace_id}] Scraper error: {str(e)}")
        
        # Determine appropriate status code based on error type
        if "authentication" in str(e).lower() or "login" in str(e).lower():
            status_code = 401
        elif "configuration" in str(e).lower():
            status_code = 400
        else:
            status_code = 500
        
        raise HTTPException(status_code=status_code, detail=str(e))
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"[{trace_id}] Query failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}"
        )


if __name__ == "__main__":
    # Default port is 91060 (can be overridden via PORT env var)
    port = int(os.getenv("PORT", "91060"))
    # Use 127.0.0.1 instead of 0.0.0.0 to avoid macOS DNS resolution issues
    host = os.getenv("HOST", "127.0.0.1")
    
    logger.info(f"Starting Quid MCP API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

