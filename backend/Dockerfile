# =====================================================================================
# 🐍 ARCANOVI DJANGO BACKEND DOCKERFILE
# =====================================================================================
# ⚠️ ALLE Konfiguration kommt aus der zentralen .env Datei!
# ⚠️ ERWEITERTE Health-Checks und Production-Optimierungen
# =====================================================================================

FROM python:3.11-slim

# Metadaten für bessere Wartbarkeit
LABEL maintainer="Arcanovi Team"
LABEL version="1.0.0"
LABEL description="Django backend for Arcanovi fantasy application"

# =====================================================================================
# 🔧 ENVIRONMENT VARIABLES - AUS .env DATEI
# =====================================================================================
# Diese werden zur Laufzeit durch docker-compose gesetzt
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# =====================================================================================
# 🏗️ SYSTEM SETUP
# =====================================================================================
# Set work directory
WORKDIR /app

# Install system dependencies inkl. curl für Health-Checks
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
        netcat-traditional \
        gettext \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# =====================================================================================
# 📦 PYTHON DEPENDENCIES
# =====================================================================================
# Install Python dependencies first (better Docker layer caching)
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# =====================================================================================
# 📁 PROJECT FILES
# =====================================================================================
# Copy project files
COPY . /app/

# =====================================================================================
# 🗂️ DIRECTORY SETUP
# =====================================================================================
# Erstelle notwendige Verzeichnisse für statische Dateien und Media
RUN mkdir -p /app/staticfiles /app/media /app/logs \
    && chmod -R 755 /app/staticfiles /app/media /app/logs

# =====================================================================================
# 🏥 HEALTH CHECK SCRIPT
# =====================================================================================
# Erstelle erweiterten Health-Check-Script
RUN echo '#!/bin/bash' > /app/health_check.sh && \
    echo 'set -e' >> /app/health_check.sh && \
    echo '' >> /app/health_check.sh && \
    echo '# ⚠️ ERWEITERTE HEALTH-CHECKS FÜR ARCANOVI BACKEND' >> /app/health_check.sh && \
    echo '# Prüft Django, Datenbank-Verbindung und Migrations' >> /app/health_check.sh && \
    echo '' >> /app/health_check.sh && \
    echo 'echo "🔍 Starting Arcanovi backend health check..."' >> /app/health_check.sh && \
    echo '' >> /app/health_check.sh && \
    echo '# 1. Basis Django Check' >> /app/health_check.sh && \
    echo 'echo "1. Checking Django configuration..."' >> /app/health_check.sh && \
    echo 'python manage.py check --deploy --quiet || { echo "❌ Django check failed"; exit 1; }' >> /app/health_check.sh && \
    echo 'echo "✅ Django configuration OK"' >> /app/health_check.sh && \
    echo '' >> /app/health_check.sh && \
    echo '# 2. Database Connection Check' >> /app/health_check.sh && \
    echo 'echo "2. Checking database connection..."' >> /app/health_check.sh && \
    echo 'python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()" || { echo "❌ Database connection failed"; exit 1; }' >> /app/health_check.sh && \
    echo 'echo "✅ Database connection OK"' >> /app/health_check.sh && \
    echo '' >> /app/health_check.sh && \
    echo '# 3. Migrations Check' >> /app/health_check.sh && \
    echo 'echo "3. Checking migrations..."' >> /app/health_check.sh && \
    echo 'python manage.py showmigrations --plan | grep -q "\[ \]" && { echo "⚠️  Unapplied migrations found - this might be intentional in development"; } || echo "✅ All migrations applied"' >> /app/health_check.sh && \
    echo '' >> /app/health_check.sh && \
    echo 'echo "🎉 Arcanovi backend health check completed successfully!"' >> /app/health_check.sh && \
    echo 'exit 0' >> /app/health_check.sh && \
    chmod +x /app/health_check.sh

# =====================================================================================
# 🚀 STARTUP SCRIPT
# =====================================================================================
# Kopiere und setze Berechtigungen für Startup-Script
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

# =====================================================================================
# 🔌 NETWORK CONFIGURATION
# =====================================================================================
# Expose port (wird von .env überschrieben)
EXPOSE 8000

# =====================================================================================
# 🏥 HEALTH CHECK
# =====================================================================================
# Health-Check verwendet den erweiterten Health-Check-Script
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \
    CMD /app/health_check.sh

# =====================================================================================
# 🎯 STARTUP COMMAND
# =====================================================================================
# Verwende das Startup-Script als Default-Command
CMD ["/app/startup.sh"] 