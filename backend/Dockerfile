# backend/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (depuis le contexte racine, backend/requirements.txt)
COPY backend/requirements.txt backend/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r backend/requirements.txt

# Note: Le code sera monté via volume dans docker-compose.yml
# On copie juste pour le build initial
# manage.py est à la racine, backend/ contient le code Django
COPY manage.py .
COPY backend/ backend/

# Vérifie la structure
RUN echo "=== Vérification ===" && \
    pwd && \
    ls -la && \
    echo "manage.py:" && test -f manage.py && echo "✅" || echo "❌" && \
    echo "backend/:" && test -d backend && echo "✅" || echo "❌"

# Create necessary directories
RUN mkdir -p static media

# Collect static files (gestion d'erreur si pas encore configuré)
RUN python manage.py collectstatic --noinput || echo "Collectstatic skipped - may need migrations first"

EXPOSE 8000

# Command to run Django
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]