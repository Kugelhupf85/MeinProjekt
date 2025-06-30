#!/bin/bash
set -e

echo "🚀 Starting Arcanovi backend..."

# Warte auf Datenbank
echo "⏳ Waiting for database..."
while ! nc -z arcanovi-db 5432; do
    echo "Database not ready, waiting..."
    sleep 2
done
echo "✅ Database is ready!"

# Führe Migrations aus
echo "📊 Running database migrations..."
python manage.py migrate --noinput
echo "✅ Migrations completed!"

# Sammle statische Dateien
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✅ Static files collected!"

# Starte Django Server
echo "🌐 Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000 