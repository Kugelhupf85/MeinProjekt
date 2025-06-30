# World App - Pen & Paper World Management

Die World App verwaltet komplette Fantasy-Welten für Pen & Paper Rollenspiele mit umfassenden Worldbuilding-Features.

## Überblick

Die App implementiert eine hierarchische Struktur für Weltenverwaltung:
- **World**: Komplette Fantasy-Welt mit allen Grundelementen
- **Region**: Geografische Bereiche innerhalb einer Welt
- **Location**: Spezifische Orte innerhalb von Regionen

## Modell-Hierarchie

```
World (1) ←→ (n) Adventure
  ↓
Region (1:n)
  ↓
Location (1:n)
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
- **Services**: Verfügbare Dienstleistungen (Gasthäuser, Läden, etc.)
- **Features**: Bemerkenswerte architektonische oder natürliche Merkmale
- **Geheimnisse**: Versteckte Geheimnisse und Mysterien
- **Encounters**: Mögliche Begegnungen und Events
- **Schätze**: Besondere Gegenstände und Artefakte
- **Sicherheit**: Verteidigungsmaßnahmen und Sicherheitsvorkehrungen
- **Demografie**: Bevölkerungsgröße und -zusammensetzung
- **Quests**: Abenteuer-Möglichkeiten und Plot-Hooks

## API Endpoints

### World Endpoints
```
GET    /api/v1/worlds/                     # Liste aller Welten
POST   /api/v1/worlds/create/              # Neue Welt erstellen
GET    /api/v1/worlds/{world_id}/          # Welt-Details
PUT    /api/v1/worlds/{world_id}/update/   # Welt aktualisieren
DELETE /api/v1/worlds/{world_id}/delete/   # Welt löschen
GET    /api/v1/worlds/search/?q={query}    # Welten suchen
GET    /api/v1/worlds/{world_id}/statistics/ # Welt-Statistiken
```

### Region Endpoints
```
GET    /api/v1/regions/                    # Liste aller Regionen
POST   /api/v1/regions/create/             # Neue Region erstellen
GET    /api/v1/regions/{region_id}/        # Region-Details
PUT    /api/v1/regions/{region_id}/update/ # Region aktualisieren
DELETE /api/v1/regions/{region_id}/delete/ # Region löschen
GET    /api/v1/regions/search/?q={query}   # Regionen suchen
GET    /api/v1/regions/{region_id}/statistics/ # Region-Statistiken
```

### Location Endpoints
```
GET    /api/v1/locations/                     # Liste aller Orte
POST   /api/v1/locations/create/              # Neuen Ort erstellen
GET    /api/v1/locations/{location_id}/       # Ort-Details
PUT    /api/v1/locations/{location_id}/update/ # Ort aktualisieren
DELETE /api/v1/locations/{location_id}/delete/ # Ort löschen
GET    /api/v1/locations/search/?q={query}    # Orte suchen
GET    /api/v1/locations/{location_id}/statistics/ # Ort-Statistiken
GET    /api/v1/locations/type/{type}/         # Orte nach Typ filtern
```

## Beispiel-Datenstrukturen

### World Creation
```json
{
  "name": "Aethermoor",
  "description": "Eine mystische Welt voller Magie und alter Geheimnisse...",
  "general_mood": "Mystisch und geheimnisvoll mit unterschwelliger Spannung",
  "time_system": {
    "calendar": "Aethermoor-Kalender",
    "months": ["Frostmond", "Windmond", "Blütenmond", "Sonnenmond"],
    "days_per_month": 30,
    "hours_per_day": 24
  },
  "current_date": "15. Tag des Blütenmondes, Jahr 1247 nach der Großen Vereinigung",
  "measurement_units": {
    "distance": {"league": "5 km", "mile": "1.6 km"},
    "weight": {"stone": "6.35 kg", "pound": "0.45 kg"},
    "currency": {"gold_crown": 1, "silver_mark": 0.1, "copper_penny": 0.01}
  },
  "religions": [
    {
      "name": "Orden des Ewigen Lichts",
      "description": "Hauptreligion mit Fokus auf Licht und Ordnung",
      "deities": ["Solaris", "Lumina"],
      "influence": "hoch"
    }
  ]
}
```

### Region Creation
```json
{
  "world_id": "WLD-123456789012",
  "name": "Nordmark",
  "description": "Eine raue Grenzregion mit dichten Wäldern und alten Ruinen",
  "general_mood": "Rau und ungezähmt, aber mit versteckter Schönheit",
  "terrain_type": "Bergwald",
  "currencies": [
    {
      "name": "Nordmark-Taler",
      "exchange_rate": 0.8,
      "primary": true
    }
  ],
  "important_personalities": [
    {
      "name": "Graf Aldric von Nordmark",
      "role": "Regionaler Herrscher",
      "importance": 9,
      "description": "Weiser aber strenger Herrscher"
    }
  ]
}
```

### Location Creation
```json
{
  "region_id": "RGN-123456789012",
  "name": "Die Goldene Krone",
  "location_type": "tavern",
  "description": "Ein gemütliches Gasthaus im Herzen der Stadt",
  "general_mood": "Warm und einladend mit lebhaften Gesprächen",
  "services_available": [
    {
      "type": "accommodation",
      "name": "Übernachtung",
      "price": "2 Silber pro Nacht",
      "available": true
    },
    {
      "type": "food",
      "name": "Warme Mahlzeiten",
      "price": "5 Kupfer",
      "available": true
    }
  ],
  "important_personalities": [
    {
      "name": "Martha Goldherz",
      "role": "Wirtin",
      "importance": 7,
      "description": "Freundliche Wirtin mit vielen Geschichten"
    }
  ]
}
```

## Worldbuilding-Konzepte

### Konsistentes Worldbuilding
Die App unterstützt konsistentes Worldbuilding durch:
- **Hierarchische Struktur**: Klare Beziehungen zwischen Welt, Region und Ort
- **Vererbung**: Regionale Eigenschaften können von der Welt übernommen werden
- **Querverweise**: Verbindungen zwischen verschiedenen Elementen
- **Statistiken**: Übersicht über Zusammenhänge und Abhängigkeiten

### Fantasy-Rollenspiel Features
- **Plot-Hooks**: Abenteuer-Aufhänger auf allen Ebenen
- **NPCs**: Wichtige Persönlichkeiten mit Rollen und Wichtigkeit
- **Geheimnisse**: Versteckte Informationen für Spielleiter
- **Encounters**: Vordefinierte Begegnungsmöglichkeiten
- **Quests**: Abenteuer-Möglichkeiten und Missionen

## Technische Details

### Entity IDs
- World: `WLD-{12_digit_id}`
- Region: `RGN-{12_digit_id}`
- Location: `LOC-{12_digit_id}`

### Datenbank-Tabellen
- `wld_world_entity`
- `wld_region_entity`
- `wld_location_entity`

### JSON-Felder
Alle komplexen Datenstrukturen werden als JSON gespeichert für maximale Flexibilität bei der Weltenerstellung.

### Soft Delete
Alle Entitäten unterstützen Soft Delete über das `is_active` Feld.

## Integration mit Adventure App

Welten können von mehreren Adventures verwendet werden:
- Ein Adventure hat genau eine Welt
- Eine Welt kann von mehreren Adventures genutzt werden
- Statistiken zeigen aktive Adventures pro Welt 