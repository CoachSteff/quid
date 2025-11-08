FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# The Playwright base image already has pwuser (UID 1000), use that
RUN chown -R pwuser:pwuser /app

# Copy application code
COPY . .

# Create data directory for session storage with proper permissions
RUN mkdir -p /app/data && \
    chmod 755 /app/data && \
    chown -R pwuser:pwuser /app/data

# Switch to non-root user
USER pwuser

# Expose port
EXPOSE 38153

# Run the application
CMD ["python", "app.py"]

