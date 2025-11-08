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


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    status: str
    timestamp: str
    citation: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    raw_data: Optional[List[Dict[str, Any]]] = None
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
