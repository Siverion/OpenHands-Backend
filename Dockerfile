# Medium Power Dockerfile for HF Spaces
# Advanced AI Assistant with Code Execution & File Management

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for code execution
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_medium.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app_medium_power.py app.py

# Create workspace and database directories
RUN mkdir -p /tmp/openhands_workspace
RUN mkdir -p /tmp/db

# Set permissions
RUN chmod 755 /tmp/openhands_workspace
RUN chmod 755 /tmp/db

# Expose port
EXPOSE 7860

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=7860
ENV PYTHONUNBUFFERED=1
ENV WORKSPACE_DIR=/tmp/openhands_workspace
ENV DB_PATH=/tmp/openhands.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/health')"

# Run application
CMD ["python", "app.py"]