FROM nginx:alpine

# =====================================================================================
# 🌐 ARCANOVI NGINX DOCKERFILE
# =====================================================================================
# ⚠️ ZENTRALE KONFIGURATION AUS .env DATEI!
# ⚠️ Alle Umgebungsvariablen werden zur Laufzeit durch envsubst substituiert!
# =====================================================================================

# Metadaten für bessere Wartbarkeit
LABEL maintainer="Arcanovi Team"
LABEL version="1.0.0"
LABEL description="Nginx reverse proxy for Arcanovi with dynamic configuration"

# Install envsubst für Template-Substitution und curl für Health-Checks
RUN apk add --no-cache gettext curl

# Nginx-Setup in einem Layer
RUN rm /etc/nginx/conf.d/default.conf && \
    # Erstelle Verzeichnisse für statische Inhalte und Medien
    mkdir -p /static /media /static_backend /media_backend && \
    chmod -R 755 /static /media /static_backend /media_backend && \
    # Verbessere NGINX Logging-Konfiguration
    ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log && \
    # Template-Verzeichnis erstellen
    mkdir -p /etc/nginx/templates

# Kopiere Nginx-Hauptkonfiguration (statisch)
COPY nginx.conf /etc/nginx/nginx.conf

# Kopiere Konfigurationstemplates
COPY conf.d/*.conf /etc/nginx/templates/

# Erstelle erweiterte Health-Check-Datei
RUN echo '{"status":"ok","service":"nginx","project":"arcanovi"}' > /static/health.json

# =====================================================================================
# 🔧 UMGEBUNGSVARIABLEN-SUBSTITUTION SCRIPT
# =====================================================================================
# Erstelle das envsubst-Script für alle .env-Variablen
RUN echo '#!/bin/sh' > /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo 'set -e' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo 'echo "🔧 Starting Arcanovi Nginx environment variable substitution..."' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '# ⚠️ ALLE UMGEBUNGSVARIABLEN AUS ZENTRALER .env VERFÜGBAR MACHEN - KEINE FALLBACKS!' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo 'if [ -z "$SERVER_NAME" ] || [ -z "$CORS_ALLOW_ORIGIN" ] || [ -z "$ENGINE_CONTAINER_NAME" ] || [ -z "$ENGINE_INTERNAL_PORT" ] || [ -z "$FRONTEND_CONTAINER_NAME" ] || [ -z "$FRONTEND_INTERNAL_PORT" ]; then' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '    echo "❌ CRITICAL ERROR: Required environment variables are missing!"' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '    echo "Required: SERVER_NAME, CORS_ALLOW_ORIGIN, ENGINE_CONTAINER_NAME, ENGINE_INTERNAL_PORT, FRONTEND_CONTAINER_NAME, FRONTEND_INTERNAL_PORT"' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '    exit 1' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo 'fi' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '# Template-Substitution für alle .conf Dateien' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo 'for template in /etc/nginx/templates/*.conf; do' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '    if [ -f "$template" ]; then' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '        filename=$(basename "$template")' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '        echo "📄 Substituting environment variables in $filename"' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '        echo "   - SERVER_NAME: $SERVER_NAME"' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '        echo "   - CORS_ALLOW_ORIGIN: $CORS_ALLOW_ORIGIN"' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '        echo "   - ENGINE: $ENGINE_CONTAINER_NAME:$ENGINE_INTERNAL_PORT"' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '        echo "   - FRONTEND: $FRONTEND_CONTAINER_NAME:$FRONTEND_INTERNAL_PORT"' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '        envsubst '\''$SERVER_NAME $CORS_ALLOW_ORIGIN $ENGINE_CONTAINER_NAME $ENGINE_INTERNAL_PORT $FRONTEND_CONTAINER_NAME $FRONTEND_INTERNAL_PORT'\'' < "$template" > "/etc/nginx/conf.d/$filename"' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '    fi' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo 'done' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo '' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo 'echo "✅ Arcanovi Nginx environment variable substitution completed."' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    echo 'echo "🌐 Nginx ready to serve Arcanovi application."' >> /docker-entrypoint.d/20-envsubst-on-templates.sh && \
    chmod +x /docker-entrypoint.d/20-envsubst-on-templates.sh

# Standard Nginx-Port
EXPOSE 80

# =====================================================================================
# 🏥 HEALTH CHECK
# =====================================================================================
# Health-Check ohne hardcodierte Werte
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Standard nginx entrypoint wird verwendet, der automatisch scripts in /docker-entrypoint.d/ ausführt
CMD ["nginx", "-g", "daemon off;"] 