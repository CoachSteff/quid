#!/usr/bin/env python3
"""
API request and response models.
"""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, field_validator


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate query string - reject empty and limit length."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Query cannot be empty')
        if len(v) > 1000:
            raise ValueError('Query too long (max 1000 characters)')
        return v.strip()


class DocumentMetadata(BaseModel):
    """Metadata for a document."""
    woId: Optional[str] = None
    woVersion: Optional[str] = None
    # Add more metadata fields as needed
    category: Optional[str] = None
    authority: Optional[str] = None
    effective_date: Optional[str] = None


class Document(BaseModel):
    """
    Document model representing a source document.
    
    Supports multiple document types:
    - detail_page: EMIS detail pages with regulations/articles
    - pdf: Downloadable PDF documents
    - download: Other downloadable files
    - external: External website links
    """
    title: str
    url: str
    type: str  # detail_page, pdf, download, external
    metadata: Optional[DocumentMetadata] = None
    description: Optional[str] = None
    source: Optional[str] = None  # Source system/database (e.g., "EMIS", "VLAREM")


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    status: str
    timestamp: str
    citation: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    raw_data: Optional[List[Dict[str, Any]]] = None
    documents: Optional[List[Document]] = None
    error_message: Optional[str] = None


class SiteInfo(BaseModel):
    """Basic site information."""
    site_id: str
    name: str
    description: str
    base_url: str


class SiteListResponse(BaseModel):
    """Response for list sites endpoint."""
    sites: List[SiteInfo]
    count: int


class HumanIntervention(BaseModel):
    """Human intervention requirements for a plugin."""
    captcha: bool = False
    mfa: bool = False
    initial_setup: bool = False


class PluginInfo(BaseModel):
    """Plugin information model."""
    id: str
    name: str
    version: str
    author: str
    description: str
    homepage: Optional[str] = None
    category: str
    tags: List[str] = []
    license: Optional[str] = None
    auth_scenario: str
    enabled: bool
    loaded_at: Optional[str] = None
    human_intervention: HumanIntervention


class PluginListResponse(BaseModel):
    """Response for list plugins endpoint."""
    plugins: List[PluginInfo]
    count: int
