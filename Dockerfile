FROM python:3.11-slim

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only production files (exclude dev/test files)
COPY src/ /app/src/
COPY templates/ /app/templates/
COPY static/ /app/static/
COPY wsgi.py /app/
COPY run_dashboard.py /app/

# Create symlinks for fallback imports
RUN ln -sf /app/src/utils /app/utils && \
    ln -sf /app/src/config /app/config && \
    ln -sf /app/src/services /app/services && \
    ln -sf /app/src/routes /app/routes && \
    ln -sf /app/src/monitoring /app/monitoring

# Cloud Run uses PORT environment variable
EXPOSE 8080

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PYTHONPATH=/app:/app/src
ENV PORT=8080

# Use Cloud Run's PORT environment variable
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
