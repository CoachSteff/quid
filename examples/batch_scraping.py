#!/usr/bin/env python3
"""
Example: Batch scraping multiple queries
"""

import subprocess
import json
import time
from pathlib import Path

# Queries to scrape
QUERIES = [
    "BBT water treatment",
    "waste management legislation",
    "air quality standards",
    "environmental impact assessment"
]

# Output directory
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def scrape_query(site_id: str, query: str) -> dict:
    """Execute scrape command and return result."""
    print(f"Scraping: {query}")
    
    result = subprocess.run(
        ["./scrape", "query", site_id, query, "--format", "raw"],
        cwd="../backend",
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        print(f"Error: {result.stderr}")
        return {"status": "error", "query": query}

def main():
    """Main batch scraping function."""
    print("Starting batch scraping...")
    
    results = []
    
    for query in QUERIES:
        result = scrape_query("emis", query)
        results.append(result)
        
        # Save individual result
        filename = query.replace(" ", "_").lower() + ".json"
        output_path = OUTPUT_DIR / filename
        
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Saved to: {output_path}")
        
        # Rate limiting - be respectful!
        time.sleep(5)
    
    # Save combined results
    combined_path = OUTPUT_DIR / "all_results.json"
    with open(combined_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nCompleted! Scraped {len(results)} queries")
    print(f"Combined results: {combined_path}")

if __name__ == "__main__":
    main()
