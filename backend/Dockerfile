# Backend Dockerfile - Django
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

# Create directories for media and static files
RUN mkdir -p /app/media /app/static /app/questions

# Install netcat for healthcheck
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Expose port
EXPOSE 8000

# Use a simple command that waits for DB and starts server
CMD sh -c "echo 'Waiting for database...' && while ! nc -z db 3306; do sleep 1; done && echo 'Database is ready!' && (python manage.py migrate --fake-initial 2>/dev/null || python manage.py migrate || true) && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"

