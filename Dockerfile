# Quid MCP Backend - Docker Image
# Uses Python 3.12 for maximum compatibility

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy application code
COPY backend/ .

# Copy plugins directory
COPY plugins/ /app/plugins/

# Expose port (informational - actual mapping in docker-compose.yml)
# Note: EXPOSE is optional; port mapping is controlled by docker-compose.yml
EXPOSE 8000

# Set environment variables
# Use 8000 internally; docker-compose.yml maps it to 91060 externally
ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Health check (checks internal port 8000)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["python", "app.py"]
