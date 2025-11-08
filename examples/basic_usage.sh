#!/bin/bash
# Example: Basic CLI usage

cd "$(dirname "$0")/../backend"

# Check available sites
echo "=== Available Sites ==="
./scrape list

# Check credentials for EMIS
echo -e "\n=== Credential Check ==="
./scrape check emis

# Query EMIS
echo -e "\n=== Query Example ==="
./scrape query emis "BBT water treatment" --format table

# Query with JSON output
echo -e "\n=== JSON Output ==="
./scrape query emis "environmental legislation" --format json
