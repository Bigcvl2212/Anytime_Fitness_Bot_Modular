FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create app directory and copy source files
WORKDIR /app

# Copy the entire src directory contents to /app (flattening the structure)
COPY src/ /app/
COPY wsgi.py /app/

# Cloud Run uses PORT environment variable
EXPOSE 8080

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=8080

# Use Cloud Run's PORT environment variable
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
