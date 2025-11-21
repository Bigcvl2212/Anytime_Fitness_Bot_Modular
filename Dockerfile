FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy source files maintaining structure  
COPY src/ /app/src/
COPY wsgi.py /app/

# Set working directory to /app
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production  
ENV PORT=8080
ENV PYTHONPATH="/app"

# Cloud Run uses PORT environment variable
EXPOSE 8080

# Use Cloud Run's PORT environment variable - run as module to ensure package context
CMD exec python -m gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
