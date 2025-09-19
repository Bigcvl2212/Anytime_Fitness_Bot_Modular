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

# Copy essential directories to root for fallback imports
COPY src/utils/ /app/utils/
COPY src/config/ /app/config/
COPY src/services/ /app/services/
COPY src/routes/ /app/routes/
COPY src/monitoring/ /app/monitoring/

# Cloud Run uses PORT environment variable
EXPOSE 8080

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PYTHONPATH=/app:/app/src
ENV PORT=8080

# Use Cloud Run's PORT environment variable
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
