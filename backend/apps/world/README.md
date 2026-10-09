# World App - Pen & Paper World Management

Die World App verwaltet komplette Fantasy-Welten für Pen & Paper Rollenspiele mit umfassenden Worldbuilding-Features und **Phase 3: World-zentrierte Architektur**.

## ✅ **PHASE 3 STATUS: VOLLSTÄNDIG IMPLEMENTIERT**

**Alle Tests bestehen erfolgreich: 16/16 Tests ✅**

### 🚀 **Neue Phase 3 Features:**
- **World-API-Keys-System** - API-Schlüssel pro World statt pro User
- **World-Party-System** - World-spezifische Parties mit DM-Management
- **Automatische Permission-Integration** - Admin-Rechte für World-Creator und DM
- **Django Signals** - Automatische Erstellung von API-Keys und Parties
- **Vollständige Test-Abdeckung** - 16 Tests für alle neuen Features

---

## Überblick

Die App implementiert eine hierarchische Struktur für Weltenverwaltung mit **World-zentrierter Architektur**:
- **World**: Komplette Fantasy-Welt mit allen Grundelementen
- **WorldAPIKeys**: API-Schlüssel-Verwaltung pro World
- **WorldParty**: World-spezifische Party-Verwaltung
- **WorldPartyMembership**: Party-Mitgliedschaften mit Rollen
- **Region**: Geografische Bereiche innerhalb einer Welt
- **Location**: Spezifische Orte innerhalb von Regionen

## Modell-Hierarchie

```
World (1) ←→ (1) WorldAPIKeys
  ↓
WorldParty (1:1)
  ↓
WorldPartyMembership (1:n)
  ↓
User (n)

World (1) ←→ (n) Adventure
  ↓
Region (1:n)
  ↓
Location (1:n)
```

## 🗝️ **World-API-Keys-System**

### Features:
- **World-spezifische API-Schlüssel** für verschiedene AI-Provider
- **pgcrypto-Verschlüsselung** für sichere Schlüssel-Speicherung
- **Status-Tracking** für jeden Provider (configured, invalid, expired, etc.)
- **Usage-Statistics** für Rate-Limiting und Monitoring
- **Automatische Erstellung** via Django Signals

### Unterstützte Provider:
- OpenAI
- Anthropic
- Google
- DeepSeek

### Verwendung:
```python
# API-Keys automatisch verfügbar
world = World.objects.create(name="My World", created_by=user)
api_keys = world.api_keys  # Automatisch erstellt

# Provider konfigurieren
api_keys.mark_provider_configured('openai')
api_keys.increment_usage('openai')

# Status prüfen
if api_keys.is_provider_configured('openai'):
    # API-Aufruf durchführen
    pass
```

## 🎭 **World-Party-System**

### Features:
- **World-spezifische Parties** - Jede World hat eine eigene Party
- **DM-Rollen-Management** - Automatische Permission-Verwaltung
- **Party-Mitgliedschaften** mit verschiedenen Rollen
- **Automatische Erstellung** via Django Signals
- **Permission-Integration** mit dem Permission-System

### Rollen:
- **Dungeon Master**: Vollzugriff auf World und API-Keys
- **Co-Dungeon Master**: Kampagnen-Management und API-Keys
- **Player**: Grundlegende World-Zugriffe
- **Observer**: Nur Leserechte

### Verwendung:
```python
# Party automatisch verfügbar
world = World.objects.create(name="My World", created_by=user)
party = world.party  # Automatisch erstellt

# Mitglied einladen
membership = WorldPartyMembership.objects.create(
    user=invited_user,
    party=party,
    role='player',
    status='invited'
)

# DM-Rolle vergeben
membership.promote_to_dm()
```

## 🔐 **Permission-Integration**

### Automatische Permission-Verwaltung:
- **World-Creator** erhält automatisch Admin-Permissions
- **DM-Rollen** erhalten automatisch Admin-Permissions
- **Party-Mitglieder** erhalten View-Permissions
- **Permission-Cleanup** bei Rollen-Änderungen

### Permission-Hierarchie:
```
admin > delete > edit > view
```

## Features

### World (Welt)
- **Grundinformationen**: Name, Beschreibung (max. 5000 Zeichen), Grundstimmung
- **Zeitsystem**: Benutzerdefinierte Zeitrechnung und aktuelles Datum
- **Maßeinheiten**: Eigene Maßsysteme für Entfernung, Gewicht, Währung
- **Religionen**: Pantheons und Glaubenssysteme (JSON)
- **Magiesystem**: Regeln und Mechaniken der Magie
- **Politik**: Regierungsformen und Machtstrukturen
- **Sprachen**: Gesprochene Sprachen mit kulturellem Kontext
- **Geschichte**: Zeitleiste wichtiger Ereignisse
- **Klima**: Klimazonen und Wetterphänomene
- **Handel**: Handelsrouten und wirtschaftliche Verbindungen
- **Konflikte**: Aktuelle Spannungen und Plot-Hooks
- **Creator-Tracking**: Wer hat die World erstellt

### WorldAPIKeys
- **Verschlüsselte API-Schlüssel** für alle Provider
- **Status-Tracking** und Validierung
- **Usage-Statistics** für Monitoring
- **Security-Notes** für Admin-Dokumentation

### WorldParty
- **World-spezifische Party** mit automatischer Erstellung
- **DM-Management** mit Rollen-Wechsel
- **Party-Einstellungen** und Konfiguration
- **Mitglieder-Verwaltung** mit Rollen

### WorldPartyMembership
- **Rollen-basierte Permissions** (DM, Co-DM, Player, Observer)
- **Status-Management** (active, inactive, invited, banned)
- **Automatische Permission-Zuweisung** basierend auf Rolle
- **API-Key-Zugriff** für DM und Co-DM

### Region
- **Grundinformationen**: Name, Beschreibung, Grundstimmung, Terrain
- **Wirtschaft**: Währungen und Wechselkurse
- **Persönlichkeiten**: Wichtige NPCs und Herrscher (JSON)
- **Kultur**: Traditionen, Bräuche und kulturelle Eigenarten
- **Regierung**: Politische Struktur und Verwaltung
- **Ressourcen**: Natürliche Ressourcen und Handelsspezialitäten
- **Gefahren**: Bedrohungen, Monster und Risiken
- **Militär**: Verteidigungskräfte und militärische Organisation
- **Events**: Feste, Feiern und wiederkehrende Ereignisse

### Location
- **Grundinformationen**: Name, Typ, Beschreibung, Grundstimmung
- **NPCs**: Wichtige Persönlichkeiten vor Ort
- **Services**: Verfügbare Dienstleistungen und Preise
- **Geheimnisse**: Versteckte Informationen für Spielleiter
- **Encounters**: Vordefinierte Begegnungsmöglichkeiten
- **Quests**: Abenteuer-Möglichkeiten und Missionen

## API-Endpoints

### World CRUD
- `GET /api/world/worlds/` - Liste aller zugänglichen Worlds
- `POST /api/world/worlds/create/` - Neue World erstellen
- `GET /api/world/worlds/{id}/` - World-Details abrufen
- `PUT /api/world/worlds/{id}/` - World aktualisieren
- `DELETE /api/world/worlds/{id}/` - World löschen

### World API Keys
- `GET /api/world/worlds/{id}/api-keys/` - API-Keys abrufen (Admin)
- `PUT /api/world/worlds/{id}/api-keys/update/` - API-Key-Status aktualisieren (Admin)
- `POST /api/world/worlds/{id}/api-keys/test/` - API-Key testen (Admin)

### World Party
- `GET /api/world/worlds/{id}/party/` - Party-Details abrufen
- `PUT /api/world/worlds/{id}/party/update/` - Party aktualisieren (Edit)
- `GET /api/world/worlds/{id}/party/members/` - Party-Mitglieder abrufen
- `POST /api/world/worlds/{id}/party/invite/` - Mitglied einladen (Edit)
- `PUT /api/world/worlds/{id}/party/members/{id}/` - Mitgliedschaft aktualisieren (Edit)
- `DELETE /api/world/worlds/{id}/party/members/{id}/remove/` - Mitglied entfernen (Edit)

## Django Signals

### Automatische Erstellung:
- **WorldAPIKeys** wird automatisch bei World-Erstellung erstellt
- **WorldParty** wird automatisch bei World-Erstellung erstellt
- **WorldPartyMembership** wird für World-Creator mit DM-Rolle erstellt

### Permission-Management:
- **Admin-Permissions** werden automatisch für World-Creator vergeben
- **DM-Rollen** erhalten automatisch Admin-Permissions
- **Permission-Cleanup** bei Rollen-Änderungen und Mitgliedschaft-Löschung

## Technische Details

### Entity IDs
- World: `WLD-{12_digit_id}`
- WorldParty: `WP-{12_digit_id}`
- Region: `RGN-{12_digit_id}`
- Location: `LOC-{12_digit_id}`

### Datenbank-Tabellen
- `wld_world_entity`
- `wld_world_api_keys`
- `wld_world_party`
- `wld_world_party_membership`
- `wld_region_entity`
- `wld_location_entity`

### JSON-Felder
Alle komplexen Datenstrukturen werden als JSON gespeichert für maximale Flexibilität bei der Weltenerstellung.

### Soft Delete
Alle Entitäten unterstützen Soft Delete über das `is_active` Feld.

## Integration mit anderen Apps

### Permission-System (Phase 2)
- **Vollständige Integration** mit dem Permission-System
- **Automatische Permission-Verwaltung** für World-Creator und DM
- **Permission-Hierarchie** wird respektiert

### Core User (Phase 1)
- **User-Integration** über `created_by` und Party-Mitgliedschaften
- **Email-basierte Einladungen** für Party-Mitglieder

### Adventure App
- **World-Adventure-Relationships** bleiben bestehen
- **Permission-Vererbung** von World zu Adventure

## Testing

### Test-Abdeckung:
- **16 Tests** für alle neuen Models und Features
- **Model-Tests**: World, WorldAPIKeys, WorldParty, WorldPartyMembership
- **Permission-Integration-Tests**: Automatische Permission-Verwaltung
- **Signal-Tests**: Automatische Erstellung und Permission-Management

### Test-Ausführung:
```bash
# Alle World-Tests ausführen
python manage.py test apps.world.tests.test_world_models -v 2

# Spezifische Test-Klassen
python manage.py test apps.world.tests.test_world_models.WorldAPIKeysModelTest
python manage.py test apps.world.tests.test_world_models.WorldPartyModelTest
```

## Migration von Phase 2

### Bestehende Daten:
- **World-Daten** bleiben unverändert
- **Neue Felder** werden automatisch hinzugefügt
- **API-Keys** und **Parties** werden für bestehende Worlds erstellt

### Migration-Script:
```python
# Für bestehende Worlds ohne API-Keys/Party
for world in World.objects.all():
    if not hasattr(world, 'api_keys'):
        WorldAPIKeys.objects.create(world=world)
    if not hasattr(world, 'party'):
        WorldParty.objects.create(
            world=world,
            name=f"Party of {world.name}",
            creator=world.created_by
        )
```

---

## 🎯 **Phase 3 Vorteile:**

1. **World-zentrierte Architektur**: Jede World ist ein eigenständiges System
2. **API-Key-Isolation**: Verschiedene Worlds können verschiedene AI-Provider nutzen
3. **Party-Management**: World-spezifische Gruppen mit DM-Rollen
4. **Permission-Integration**: Automatische Berechtigungsverwaltung
5. **Skalierbarkeit**: Einfache Erweiterung für neue Features
6. **Sicherheit**: pgcrypto-Verschlüsselung für API-Keys

**Nächster Schritt: Phase 4 - Character-Management-System** 👥 