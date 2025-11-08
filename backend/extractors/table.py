#!/usr/bin/env python3
"""
Table-based data extractor.
Extracts data from HTML tables.
"""

import logging
from typing import Dict, List, Any
from playwright.async_api import Page

from .base import BaseExtractor, ExtractionException
from .registry import register_extractor

logger = logging.getLogger(__name__)


@register_extractor
class TableExtractor(BaseExtractor):
    """
    Extracts data from HTML tables.
    
    Config structure:
    {
        "type": "table",
        "selector": "table.results",  # Table selector (optional)
        "extract_headers": true,      # Extract headers from thead/first row
        "max_rows": 100               # Limit rows (optional)
    }
    """
    
    def get_name(self) -> str:
        return "table"
    
    async def can_extract(self, page: Page) -> bool:
        """Check if page contains tables."""
        selector = self.config.get('selector', 'table')
        
        try:
            tables = await page.query_selector_all(selector)
            return len(tables) > 0
        except:
            return False
    
    async def extract(self, page: Page) -> List[Dict[str, Any]]:
        """
        Extract data from tables on the page.
        
        Returns:
            List of row dictionaries with column headers as keys
        """
        selector = self.config.get('selector', 'table')
        extract_headers = self.config.get('extract_headers', True)
        max_rows = self.config.get('max_rows')
        
        try:
            tables = await page.query_selector_all(selector)
            
            if not tables:
                logger.warning(f"No tables found with selector: {selector}")
                return []
            
            logger.info(f"Found {len(tables)} tables on page")
            
            all_data = []
            
            for table_idx, table in enumerate(tables):
                try:
                    # Extract headers
                    headers = []
                    
                    if extract_headers:
                        # Try thead first
                        header_rows = await table.query_selector_all('thead tr th, thead tr td')
                        
                        # If no thead, use first row
                        if not header_rows:
                            header_rows = await table.query_selector_all('tr:first-child th, tr:first-child td')
                        
                        for header in header_rows:
                            text = await header.inner_text()
                            headers.append(text.strip())
                    
                    # Extract data rows
                    if extract_headers and headers:
                        # Skip first row if we used it for headers
                        rows = await table.query_selector_all('tbody tr, tr:not(:first-child)')
                    else:
                        rows = await table.query_selector_all('tbody tr, tr')
                    
                    logger.info(f"Table {table_idx + 1}: {len(headers)} columns, {len(rows)} rows")
                    
                    for row_idx, row in enumerate(rows):
                        # Check max_rows limit
                        if max_rows and len(all_data) >= max_rows:
                            logger.info(f"Reached max_rows limit: {max_rows}")
                            break
                        
                        cells = await row.query_selector_all('td, th')
                        
                        row_data = {}
                        for col_idx, cell in enumerate(cells):
                            cell_text = await cell.inner_text()
                            
                            # Use header as key if available
                            if headers and col_idx < len(headers):
                                key = headers[col_idx] or f"column_{col_idx}"
                            else:
                                key = f"column_{col_idx}"
                            
                            row_data[key] = cell_text.strip()
                        
                        if row_data:
                            all_data.append(row_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to extract table {table_idx + 1}: {e}")
                    continue
            
            logger.info(f"Extracted {len(all_data)} rows from {len(tables)} tables")
            return all_data
            
        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            raise ExtractionException(f"Failed to extract tables: {str(e)}")
