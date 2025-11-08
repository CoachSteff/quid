#!/bin/bash
# Helper script to start the EMIS backend server on the correct port
# Works with both virtual environments and system Python

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Note: .env file is automatically loaded by app.py via load_dotenv()
# No need to manually export here - app.py handles it more reliably
# This ensures consistent behavior whether running via script or directly

# Default port if not set (can be overridden by .env file or environment)
PORT=${PORT:-38153}

echo "Starting EMIS Scraping API on port $PORT..."
echo "Note: .env file will be automatically loaded by app.py if present"
python app.py

