# PassAudit Docker Image
# Multi-stage build for smaller final image

FROM python:3.9-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download password database
RUN python scripts/download_passwords.py --force || true

# Create data directories
RUN mkdir -p /app/data /app/logs

# Expose port for web interface
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=5)" || exit 1

# Default command: run web server
CMD ["python", "run_web.py", "--host", "0.0.0.0", "--port", "5000"]
