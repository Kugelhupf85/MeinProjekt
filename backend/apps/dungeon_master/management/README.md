# Arcanovi User Management

## ⚠️ WICHTIGE REGEL: NIEMALS `createsuperuser` VERWENDEN!

**Verwende NIEMALS den Django-Standard `createsuperuser` Command!**

Alle Benutzer in Arcanovi werden über das DungeonMaster-System verwaltet. Superuser werden ausschließlich über die bereitgestellten Management-Scripts erstellt.

## Admin-Benutzer erstellen

### Methode 1: Django Management Command (Empfohlen)

```bash
# Im Backend-Container
docker-compose exec arcanovi-backend python manage.py create_admin_user --username admin --email admin@arcanovi.com --password mypassword

# Mit allen Optionen
docker-compose exec arcanovi-backend python manage.py create_admin_user \
    --username admin \
    --email admin@arcanovi.com \
    --password mypassword \
    --display-name "System Administrator" \
    --force
```

### Methode 2: Shell-Script (Benutzerfreundlich)

```bash
# Im Backend-Container
docker-compose exec arcanovi-backend bash apps/dungeon_master/management/scripts/create_admin.sh admin admin@arcanovi.com mypassword "System Administrator"

# Mit Umgebungsvariable
docker-compose exec -e ADMIN_PASSWORD=mypassword arcanovi-backend bash apps/dungeon_master/management/scripts/create_admin.sh admin admin@arcanovi.com
```

## Command-Optionen

### `create_admin_user` Command

| Option | Beschreibung | Standard | Erforderlich |
|--------|-------------|----------|--------------|
| `--username` | Benutzername | `admin` | Nein |
| `--email` | E-Mail-Adresse | `admin@arcanovi.com` | Nein |
| `--password` | Passwort | `$ADMIN_PASSWORD` | Ja |
| `--display-name` | Anzeigename | `System Administrator` | Nein |
| `--force` | Überschreibt bestehende Benutzer | `False` | Nein |

## Was wird erstellt?

Wenn du einen Admin-Benutzer erstellst, werden automatisch folgende Komponenten angelegt:

1. **Django User** mit Superuser-Rechten
   - `is_staff = True`
   - `is_superuser = True`
   - `is_active = True`

2. **DungeonMaster Profile**
   - Vollständiges DM-Profil mit Admin-Einstellungen
   - `experience_level = 'master'`
   - `is_public = False`
   - Spezielle Admin-Flags

3. **UserSettings**
   - UI-Einstellungen mit Admin-Modus
   - AI-Einstellungen mit vollem Zugriff
   - Feature-Flags für Admin-Funktionen
   - Erweiterte Datenschutz-Einstellungen

4. **UserKeys**
   - Leere API-Keys-Struktur
   - Admin-Sicherheitsnotizen

## Sicherheitshinweise

- **Niemals Standard-Passwörter verwenden**
- **Passwörter nach dem ersten Login ändern**
- **Admin-Zugangsdaten sicher aufbewahren**
- **In der Produktion starke Passwörter verwenden**

## Beispiele

### Entwicklungsumgebung
```bash
# Schnelle Admin-Erstellung für Entwicklung
docker-compose exec arcanovi-backend python manage.py create_admin_user --password dev123

# Ergebnis:
# Username: admin
# Email: admin@arcanovi.com
# Password: dev123
# Display Name: System Administrator
```

### Produktionsumgebung
```bash
# Sicherer Admin für Produktion
docker-compose exec arcanovi-backend python manage.py create_admin_user \
    --username gamemaster \
    --email gm@yourdomain.com \
    --password "SecurePassword123!" \
    --display-name "Game Master Supreme"
```

### Benutzer aktualisieren
```bash
# Bestehenden Benutzer aktualisieren
docker-compose exec arcanovi-backend python manage.py create_admin_user \
    --username admin \
    --password newpassword \
    --force
```

## Fehlerbehebung

### "User already exists"
Verwende die `--force` Option, um bestehende Benutzer zu aktualisieren.

### "Password is required"
Stelle sicher, dass du ein Passwort über `--password` oder die Umgebungsvariable `ADMIN_PASSWORD` bereitstellst.

### "This script must be run from the Django project root directory"
Navigiere zum Backend-Verzeichnis oder verwende den Docker-Container.

## Warum nicht `createsuperuser`?

1. **Konsistenz**: Alle Benutzer folgen dem DungeonMaster-System
2. **Vollständigkeit**: Automatische Erstellung aller zugehörigen Profile
3. **Sicherheit**: Konsistente Berechtigungen und Einstellungen
4. **Wartbarkeit**: Zentrale Verwaltung aller Benutzer-Erstellungslogik

## Integration mit Docker

```bash
# Alle Commands funktionieren im Docker-Container
docker-compose exec arcanovi-backend python manage.py create_admin_user --password mypassword

# Oder mit Shell-Script
docker-compose exec arcanovi-backend bash apps/dungeon_master/management/scripts/create_admin.sh
``` 