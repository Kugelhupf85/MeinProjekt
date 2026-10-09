# Arcanovi - Fantasy Tabletop RPG Management Platform

Eine umfassende Plattform für die Verwaltung von Fantasy-Tabletop-Rollenspielen mit Django Backend, React Frontend und Docker-Infrastruktur.

## 🎯 Projektübersicht

Arcanovi ist eine Feature-driven Anwendung für Dungeon Master und Spieler, die es ermöglicht:
- Kampagnen und Charaktere zu verwalten
- Welten und Regionen zu erstellen
- Benutzer-Profile und Parties zu organisieren
- Flexible Rollen zwischen Spieler und Dungeon Master

## 🏗️ Architektur

### Feature-Driven Design (FDD)
- **Backend**: Django Apps in `backend/apps/` mit aspect-basierter Struktur
- **Frontend**: React Features in `frontend/src/features/` mit Atomic Design
- **Infrastruktur**: Docker + Nginx + PostgreSQL

### Technologie-Stack
- **Backend**: Django 4.2 + Django REST Framework + PostgreSQL
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Infrastruktur**: Docker + Nginx + Docker Compose

## 🚀 Schnellstart

### 1. Repository klonen
```bash
git clone <repository-url>
cd arcanovi
```

### 2. Umgebungsvariablen einrichten
```bash
cp .env.example .env
# Bearbeite .env mit deinen Einstellungen
```

### 3. Services starten
```bash
docker-compose up -d
```

### 4. Datenbank migrieren
```bash
docker-compose exec arcanovi-backend python manage.py migrate
```

### 5. ⚠️ Admin-Benutzer erstellen (WICHTIG!)

**NIEMALS `createsuperuser` verwenden!**

Alle Benutzer in Arcanovi werden über das DungeonMaster-System verwaltet. Verwende ausschließlich das bereitgestellte Management-Command:

```bash
# Admin-Benutzer erstellen
docker-compose exec arcanovi-backend python manage.py create_admin_user --password dev123

# Mit benutzerdefinierten Daten
docker-compose exec arcanovi-backend python manage.py create_admin_user \
    --username gamemaster \
    --email gm@yourdomain.com \
    --password "SecurePassword123!" \
    --display-name "Game Master Supreme"
```

### 6. Anwendung aufrufen
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Admin Interface**: http://localhost:8000/admin/

## 📁 Projektstruktur

```
arcanovi/
├── backend/                    # Django Backend
│   ├── apps/                   # Feature-Apps
│   │   ├── adventure/          # Kampagnen-Management
│   │   ├── dungeon_master/     # Benutzer-System
│   │   │   ├── management/     # Admin-Scripts
│   │   │   │   ├── commands/   # Django Commands
│   │   │   │   └── scripts/    # Shell-Scripts
│   │   │   ├── models/         # User-Models
│   │   │   └── api/           # API-Endpoints
│   │   └── world/             # Welten-System
│   ├── config/                # Django-Konfiguration
│   └── manage.py
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── features/         # Feature-basierte Komponenten
│   │   └── components/       # Geteilte Komponenten
│   └── package.json
├── nginx/                    # Nginx-Konfiguration
├── docker-compose.yml       # Service-Orchestrierung
└── .env                     # Umgebungsvariablen
```

## 🔧 Entwicklung

### Backend-Entwicklung
```bash
# Django-Server starten
docker-compose exec arcanovi-backend python manage.py runserver

# Migrationen erstellen
docker-compose exec arcanovi-backend python manage.py makemigrations

# Migrationen anwenden
docker-compose exec arcanovi-backend python manage.py migrate

# Tests ausführen
docker-compose exec arcanovi-backend python manage.py test
```

### Frontend-Entwicklung
```bash
# Development-Server starten
docker-compose exec arcanovi-frontend npm run dev

# Build erstellen
docker-compose exec arcanovi-frontend npm run build

# Tests ausführen
docker-compose exec arcanovi-frontend npm test
```

## 👥 Benutzer-Verwaltung

### ⚠️ WICHTIGE REGEL: Niemals `createsuperuser` verwenden!

**Alle Benutzer werden über das DungeonMaster-System verwaltet.**

### Admin-Benutzer erstellen
```bash
# Standard-Admin
docker-compose exec arcanovi-backend python manage.py create_admin_user --password dev123

# Mit Shell-Script
docker-compose exec arcanovi-backend bash apps/dungeon_master/management/scripts/create_admin.sh
```

### Warum nicht `createsuperuser`?
1. **Konsistenz**: Alle Benutzer folgen dem DungeonMaster-System
2. **Vollständigkeit**: Automatische Erstellung aller Profile und Einstellungen
3. **Sicherheit**: Konsistente Berechtigungen und Validierung
4. **Wartbarkeit**: Zentrale Verwaltung aller Benutzer-Logik

Siehe `backend/apps/dungeon_master/management/README.md` für detaillierte Anweisungen.

## 🐳 Docker-Services

| Service | Port | Beschreibung |
|---------|------|-------------|
| `arcanovi-frontend` | 3000 | React Development Server |
| `arcanovi-backend` | 8000 | Django API Server |
| `arcanovi-db` | 5445 | PostgreSQL Database |
| `arcanovi-nginx` | 80 | Nginx Reverse Proxy |

### Service-Status prüfen
```bash
docker-compose ps
docker-compose logs -f arcanovi-backend
```

## 🔒 Sicherheit

### Produktionsumgebung
- Starke Passwörter für Admin-Benutzer verwenden
- Umgebungsvariablen für Secrets verwenden
- HTTPS aktivieren
- Regelmäßige Sicherheitsupdates

### Entwicklungsumgebung
- Standard-Passwort nach erstem Login ändern
- Keine Produktionsdaten in Entwicklung verwenden

## 📊 Datenbank

### Verbindung zur Datenbank
```bash
docker-compose exec arcanovi-db psql -U arcanovi_user -d arcanovi_db
```

### Backup erstellen
```bash
docker-compose exec arcanovi-db pg_dump -U arcanovi_user arcanovi_db > backup.sql
```

## 🧪 Testing

### Backend-Tests
```bash
docker-compose exec arcanovi-backend python manage.py test
```

### Frontend-Tests
```bash
docker-compose exec arcanovi-frontend npm test
```

## 📚 Dokumentation

- **Backend-Architektur**: Siehe `backend/README.md`
- **Frontend-Architektur**: Siehe `frontend/README.md`
- **Benutzer-Verwaltung**: Siehe `backend/apps/dungeon_master/management/README.md`
- **API-Dokumentation**: http://localhost:8000/api/docs/

## 🤝 Beitragen

1. Fork das Repository
2. Erstelle einen Feature-Branch
3. Implementiere deine Änderungen
4. Teste deine Änderungen
5. Erstelle einen Pull Request

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

## 🆘 Support

Bei Fragen oder Problemen:
1. Überprüfe die Dokumentation
2. Suche in den Issues
3. Erstelle ein neues Issue mit detaillierter Beschreibung 