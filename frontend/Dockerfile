# =====================================================================================
# ⚛️ ARCANOVI REACT FRONTEND DOCKERFILE - MULTI-STAGE BUILD
# =====================================================================================
# ⚠️ ALLE Konfiguration kommt aus der zentralen .env Datei!
# ⚠️ ERWEITERTE Health-Checks und Development/Production-Optimierungen
# =====================================================================================

FROM node:18-alpine AS base

# Metadaten für bessere Wartbarkeit
LABEL maintainer="Arcanovi Team"
LABEL version="1.0.0"
LABEL description="React frontend for Arcanovi fantasy application"

# =====================================================================================
# 🔧 GLOBAL ENVIRONMENT SETUP
# =====================================================================================
# Install system dependencies für Health-Checks
RUN apk add --no-cache curl bash

# Set working directory
WORKDIR /app

# =====================================================================================
# 📦 DEPENDENCIES STAGE
# =====================================================================================
FROM base AS dependencies

# Copy package files first for better Docker layer caching
COPY package*.json ./

# Install dependencies with optimization
RUN npm ci --only=production --silent && \
    npm cache clean --force

# =====================================================================================
# 🚀 DEVELOPMENT STAGE
# =====================================================================================
FROM base AS development

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including dev dependencies)
RUN npm install --silent && \
    npm cache clean --force

# Copy source code
COPY . .

# =====================================================================================
# 🏥 HEALTH CHECK SCRIPT FÜR DEVELOPMENT
# =====================================================================================
# Erstelle Health-Check-Script für Development-Server
RUN echo '#!/bin/bash' > /app/health_check.sh && \
    echo 'set -e' >> /app/health_check.sh && \
    echo '' >> /app/health_check.sh && \
    echo '# ⚠️ ARCANOVI FRONTEND HEALTH-CHECK (DEVELOPMENT)' >> /app/health_check.sh && \
    echo '# Prüft Vite/React Development Server' >> /app/health_check.sh && \
    echo '' >> /app/health_check.sh && \
    echo 'echo "🔍 Starting Arcanovi frontend health check..."' >> /app/health_check.sh && \
    echo '' >> /app/health_check.sh && \
    echo '# 1. Check if Vite dev server is responsive' >> /app/health_check.sh && \
    echo 'echo "1. Checking Vite development server..."' >> /app/health_check.sh && \
    echo 'curl -f http://localhost:3000/ > /dev/null 2>&1 || { echo "❌ Vite server not responding"; exit 1; }' >> /app/health_check.sh && \
    echo 'echo "✅ Vite server is responsive"' >> /app/health_check.sh && \
    echo '' >> /app/health_check.sh && \
    echo '# 2. Check if HMR endpoint is available (optional)' >> /app/health_check.sh && \
    echo 'echo "2. Checking HMR availability..."' >> /app/health_check.sh && \
    echo 'curl -f http://localhost:3000/@vite/client > /dev/null 2>&1 && echo "✅ HMR available" || echo "⚠️  HMR not available (might be normal)"' >> /app/health_check.sh && \
    echo '' >> /app/health_check.sh && \
    echo 'echo "🎉 Arcanovi frontend health check completed successfully!"' >> /app/health_check.sh && \
    echo 'exit 0' >> /app/health_check.sh && \
    chmod +x /app/health_check.sh

# =====================================================================================
# 🌐 ENVIRONMENT VARIABLES - AUS .env DATEI
# =====================================================================================
# Diese werden zur Laufzeit durch docker-compose gesetzt:
# - NODE_ENV
# - VITE_API_BASE_URL
# - VITE_API_URL  
# - VITE_BACKEND_URL
# - REACT_APP_API_URL

# =====================================================================================
# 🔌 NETWORK CONFIGURATION
# =====================================================================================
# Expose port für Development Server
EXPOSE 3000

# =====================================================================================
# 🏥 HEALTH CHECK - DEVELOPMENT
# =====================================================================================
# Health-Check für Development-Stage
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/health_check.sh

# =====================================================================================
# 🎯 STARTUP COMMAND - DEVELOPMENT
# =====================================================================================
# Start Vite development server with proper host binding
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]

# =====================================================================================
# 🏗️ BUILD STAGE (für Production)
# =====================================================================================
FROM base AS build

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --silent && \
    npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# =====================================================================================
# 🚀 PRODUCTION STAGE (für Production Builds)
# =====================================================================================
FROM nginx:alpine AS production

# Metadaten für Production
LABEL stage="production"

# Install curl für Health-Checks
RUN apk add --no-cache curl

# Copy built application
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config for SPA
RUN echo 'server {' > /etc/nginx/conf.d/default.conf && \
    echo '    listen 80;' >> /etc/nginx/conf.d/default.conf && \
    echo '    server_name localhost;' >> /etc/nginx/conf.d/default.conf && \
    echo '    root /usr/share/nginx/html;' >> /etc/nginx/conf.d/default.conf && \
    echo '    index index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '    location / {' >> /etc/nginx/conf.d/default.conf && \
    echo '        try_files $uri $uri/ /index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '}' >> /etc/nginx/conf.d/default.conf

# Health-Check für Production
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]