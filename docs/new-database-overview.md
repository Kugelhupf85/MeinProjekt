# Arcanovi – Neue Datenbankstruktur (Neuaufbau)

> **Ziel:** Werkzeug für den Spielleiter. Keine User-Verwaltung, kein DM-System.
> Die App verwaltet Welten, Regionen, Orte, NPCs, Charaktere und Sessions.
> Orte und NPCs werden datumsbewusst dargestellt – ihr Zustand ergibt sich
> automatisch aus dem aktuellen Weltdatum und den bisherigen Sessions.

---

## Übersicht der Entitäten

```
World
 ├── start_date  ← Datum, an dem die Welt beginnt
 ├── current_date  ← Aktuelles Weltdatum (manuell weitergestellt)
 ├── Region
 │    └── Location
 │         ├── NPC (Bewohner)
 │         └── LocationSnapshot (automatisch je Datum berechnet)
 ├── NPC (world-weit)
 ├── Session
 │    ├── SessionCharacter → Character
 │    └── SessionLocation → Location
 └── Character
      └── CharacterRuleSetData → RuleSet
```

---

## World – Die Welt

**Tabelle:** `wld_world_entity`

Oberste Ebene. Hat ein Startdatum und ein aktuelles Datum.
Das Startdatum definiert den Beginn der Geschichte.
`current_date` wird nach jeder Session manuell weitergestellt und
steuert alle datumsbewussten Berechnungen.

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `entity_id` | CharField | Format `WLD-{12_digit_id}` |
| `name` | CharField(200) | Name der Welt |
| `description` | TextField(5000) | Detaillierte Weltbeschreibung |
| `general_mood` | TextField(1000) | Atmosphäre der Welt |
| `start_date` | CharField(100) | In-World-Startdatum (z.B. "15. Praios 1000 BF") |
| `current_date` | CharField(100) | Aktuelles Weltdatum |
| `time_system` | JSONField | Benutzerdefinierter Kalender (Monate, Tage, Jahreszeiten) |
| `measurement_units` | JSONField | Maßeinheiten (Distanz, Gewicht, Währung) |
| `magic_system` | JSONField | Magiesystem-Regeln |
| `religions` | JSONField | Religionen und Pantheons |
| `languages` | JSONField | Sprachen der Welt |
| `political_systems` | JSONField | Politische Strukturen |
| `history_timeline` | JSONField | Historische Ereignisse |
| `climate_zones` | JSONField | Klimazonen |
| `conventions` | JSONField | Gesetze und soziale Normen |
| `conflicts_tensions` | JSONField | Aktuelle Konflikte |
| `pill` | JSONField | Auto-generierte Schnell-Zusammenfassung |
| `is_active` | BooleanField | Welt-Status |

**Welt anlegen:**
1. Name, Beschreibung, Atmosphäre eingeben
2. `start_date` festlegen → `current_date` = `start_date`
3. `time_system` konfigurieren
4. Weitere Felder (Magie, Religionen, Sprachen, ...) befüllen

---

## Region – Geografische Gebiete

**Tabelle:** `wld_region_entity`

Unterteilen die Welt in geografische oder politische Bereiche.

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `entity_id` | CharField | Format `RGN-{12_digit_id}` |
| `world` | ForeignKey(World) | Verknüpfte Welt |
| `name` | CharField(200) | Name (unique pro Welt) |
| `description` | TextField(3000) | Beschreibung |
| `general_mood` | TextField(800) | Atmosphäre |
| `terrain_type` | CharField(100) | Geländetyp (Wald, Berge, Ebene, ...) |
| `size_description` | CharField(200) | Größe und Ausdehnung |
| `currencies` | JSONField | Verwendete Währungen |
| `government_type` | JSONField | Regierungsform |
| `cultural_traits` | JSONField | Kulturelle Merkmale |
| `religions` | JSONField | Regionale Religionen |
| `important_personalities` | JSONField | Wichtige Persönlichkeiten (Kurzliste) |
| `major_settlements` | JSONField | Größere Siedlungen |
| `natural_resources` | JSONField | Natürliche Ressourcen |
| `trade_specialties` | JSONField | Handelsgüter |
| `threats_dangers` | JSONField | Gefahren |
| `climate_weather` | JSONField | Klima und Wetter |
| `laws_customs` | JSONField | Gesetze und Gebräuche |
| `festivals_events` | JSONField | Feste und regelmäßige Ereignisse |
| `military_forces` | JSONField | Militär und Verteidigung |
| `pill` | JSONField | Auto-generierte Zusammenfassung |
| `is_active` | BooleanField | Aktiv-Status |

---

## Location – Orte

**Tabelle:** `wld_location_entity`

Kleinste geografische Einheit. Enthält NPCs, Dienste, Geheimnisse und
dynamische Informationen. Der Zustand wird automatisch datumsbewusst berechnet.

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `entity_id` | CharField | Format `LOC-{12_digit_id}` |
| `region` | ForeignKey(Region) | Verknüpfte Region |
| `name` | CharField(200) | Name (unique pro Region) |
| `location_type` | CharField(20) | city / town / village / dungeon / ruins / temple / castle / forest / cave / tavern / shop / landmark / other |
| `description` | TextField(2000) | Beschreibung |
| `general_mood` | TextField(600) | Atmosphäre |
| `size_scale` | CharField(100) | Größe (tiny / small / medium / large / massive) |
| `accessibility` | CharField(200) | Zugänglichkeit |
| `important_personalities` | JSONField | Schlüssel-NPCs (Kurzreferenz) |
| `services_available` | JSONField | Verfügbare Dienste |
| `notable_features` | JSONField | Auffällige Merkmale |
| `secrets_hidden` | JSONField | Geheimnisse |
| `encounters_possible` | JSONField | Mögliche Begegnungen |
| `items_treasures` | JSONField | Gegenstände und Schätze |
| `defenses_security` | JSONField | Verteidigung |
| `population_demographics` | JSONField | Bevölkerung |
| `economic_activity` | JSONField | Wirtschaft |
| `connections_travel` | JSONField | Reiseverbindungen |
| `rumors_information` | JSONField | Gerüchte |
| `seasonal_changes` | JSONField | Saisonale Veränderungen |
| `current_events` | JSONField | Aktuelle Ereignisse |
| `quest_opportunities` | JSONField | Quest-Hooks |
| `pill` | JSONField | Auto-generierte Zusammenfassung |
| `is_active` | BooleanField | Aktiv-Status |

**Datumsbewusste Zustandsberechnung – wie es funktioniert:**
Wenn ein Ort zu einem Datum aufgerufen wird, ermittelt das System automatisch:
- Alle Sessions bis zu diesem Datum, die diesen Ort besucht haben → Konsequenzen
- Welche `current_events` zu diesem Datum aktiv sind
- Welche `seasonal_changes` greifen
- Welche NPCs laut `location_schedule` gerade anwesend sind
→ Ergebnis: ein `LocationSnapshot` (automatisch gecacht)

---

## NPC – Nichtspielercharaktere

**Tabelle:** `wld_npc_entity` *(neu – bisher nur als JSON in Locations)*

NPCs sind eigenständige Einträge, verknüpft mit Orten und Sessions.

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `entity_id` | CharField | Format `NPC-{12_digit_id}` |
| `world` | ForeignKey(World) | Verknüpfte Welt |
| `primary_location` | ForeignKey(Location, nullable) | Hauptaufenthaltsort |
| `name` | CharField(200) | Name |
| `title` | CharField(100) | Titel/Funktion (z.B. "Wirt", "Stadtrat") |
| `description` | TextField(2000) | Aussehen, Persönlichkeit, Hintergrund |
| `role_type` | CharField(50) | quest_giver / merchant / ally / enemy / neutral / background |
| `importance` | IntegerField (1-10) | Wichtigkeit für die Geschichte |
| `current_status` | CharField(50) | alive / dead / missing / unknown |
| `known_to_party` | BooleanField | Ist der NPC der Gruppe bekannt? |
| `personality_traits` | JSONField | Persönlichkeitsmerkmale |
| `motivations` | JSONField | Ziele und Motivationen |
| `relationships` | JSONField | Beziehungen zu anderen NPCs/Fraktionen |
| `secrets` | JSONField | Geheimnisse |
| `appearance` | JSONField | Detailliertes Aussehen |
| `abilities_skills` | JSONField | Fähigkeiten (system-unabhängig) |
| `inventory` | JSONField | Wichtige Gegenstände |
| `history` | JSONField | Hintergrundgeschichte |
| `location_schedule` | JSONField | Wo der NPC zu welcher Zeit anzutreffen ist |
| `session_appearances` | JSONField | In welchen Sessions aufgetreten (auto) |
| `notes` | TextField | Freie Notizen |
| `is_active` | BooleanField | Aktiv-Status |

---

## Session – Spielsitzung

**Tabelle:** `adv_session` *(neu)*

Eine Session repräsentiert eine Spielsitzung mit In-World-Datum.
Sie verankert Ereignisse im Weltkalender und beeinflusst automatisch
den Zustand von Orten und NPCs danach.

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `entity_id` | CharField | Format `SES-{12_digit_id}` |
| `world` | ForeignKey(World) | Verknüpfte Welt |
| `title` | CharField(200) | Titel (z.B. "Die Nacht in Thorwal") |
| `session_number` | IntegerField | Laufende Nummer |
| `world_date_start` | CharField(100) | In-World-Startdatum |
| `world_date_end` | CharField(100) | In-World-Enddatum |
| `real_date` | DateField | Echtes Datum der Sitzung |
| `summary` | TextField | Zusammenfassung |
| `dm_notes` | TextField | Private Notizen |
| `key_events` | JSONField | Wichtige Ereignisse |
| `consequences` | JSONField | Konsequenzen für Welt/Orte/NPCs |
| `loot_found` | JSONField | Gefundene Gegenstände |
| `status` | CharField(20) | planned / completed / cancelled |

**Session anlegen:**
1. Welt auswählen, Titel und `world_date_start` eingeben
2. Charaktere über `SessionCharacter` verknüpfen
3. Besuchte Orte über `SessionLocation` verknüpfen
4. Nach der Session: Zusammenfassung und Konsequenzen befüllen
5. `World.current_date` auf `world_date_end` weiterrücken

---

## SessionCharacter – Charakter in Session

**Tabelle:** `adv_session_character`

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `session` | ForeignKey(Session) | Verknüpfte Session |
| `character` | ForeignKey(Character) | Verknüpfter Charakter |
| `was_present` | BooleanField | War der Charakter anwesend? |
| `experience_gained` | IntegerField | Erhaltene EP |
| `notes` | TextField | Individuelle Notizen |
| `character_state` | JSONField | Zustand am Ende der Session (HP, Status, ...) |

---

## SessionLocation – Ort in Session

**Tabelle:** `adv_session_location`

Verknüpft Orte mit Sessions. Basis für die automatische Ort-Zustandsberechnung.

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `session` | ForeignKey(Session) | Verknüpfte Session |
| `location` | ForeignKey(Location) | Verknüpfter Ort |
| `visit_order` | IntegerField | Reihenfolge innerhalb der Session |
| `events_at_location` | JSONField | Was ist an diesem Ort passiert? |
| `state_before` | JSONField | Zustand vor der Session |
| `state_after` | JSONField | Zustand nach der Session |
| `npc_interactions` | JSONField | NPC-Interaktionen |

---

## LocationSnapshot – Datumsbewusster Ort-Zustand

**Tabelle:** `wld_location_snapshot` *(neu – automatisch berechnet)*

Wird automatisch erstellt wenn ein Ort zu einem Datum abgerufen wird.
Aggregiert den Zustand aus allen Sessions bis zu diesem Datum.

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `location` | ForeignKey(Location) | Verknüpfter Ort |
| `world_date` | CharField(100) | Weltdatum dieses Snapshots |
| `active_npcs` | JSONField | NPCs, die zu diesem Zeitpunkt am Ort sind |
| `current_events` | JSONField | Aktive Ereignisse |
| `seasonal_state` | JSONField | Saisonaler Zustand |
| `session_consequences` | JSONField | Konsequenzen aus vergangenen Sessions |
| `available_services` | JSONField | Verfügbare Dienste |
| `known_secrets` | JSONField | Bereits entdeckte Geheimnisse |
| `generated_at` | DateTimeField | Erstellungszeitpunkt |
| `is_cached` | BooleanField | Gecachter Snapshot? |

---

## Character – Charakter

**Tabelle:** `characters_character`

Charaktere gehören zu einer Welt. Können Spielercharaktere (SCs)
oder vollständig ausgearbeitete NPCs sein.

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `world` | ForeignKey(World) | Verknüpfte Welt |
| `rule_set` | ForeignKey(RuleSet) | Regelsystem |
| `name` | CharField(100) | Name |
| `character_type` | CharField(20) | player_character / npc_full / companion |
| `status` | CharField(20) | draft / active / archived |
| `core_attributes` | JSONField | Regelsystem-spezifische Basiswerte |

**Verknüpfte Charakter-Modelle:**
- `CharacterRuleSetData` – Erweiterte Regelsystem-Daten
- `CharacterAdvantage` / `CharacterDisadvantage`
- `CharacterSpecialAbility` / `CharacterTalent`
- `CharacterSpell` / `CharacterLiturgy`
- `CharacterEquipment` / `CharacterFamily`

---

## RuleSet – Regelsystem

**Tabelle:** `chr_ruleset`

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | UUID |
| `name` | CharField(50) | z.B. `dsa_4_1` |
| `display_name` | CharField(100) | z.B. `DSA 4.1` |
| `version` | CharField(20) | Version |
| `attribute_schema` | JSONField | JSON-Schema zur Validierung |
| `default_values` | JSONField | Standardwerte bei Charaktererstellung |
| `is_active` | BooleanField | Aktiv-Status |

---

## DSA 4.1 Referenzdaten

Unveränderliche Referenztabellen, einmalig aus Fixtures geladen.

- `chr_dsa_race` – Rassen mit Attributs-Modifikatoren und GP-Kosten
- `chr_dsa_culture` – Kulturen mit Sprach- und Talent-Boni
- `chr_dsa_profession` – Professionen mit Anforderungen
- `chr_dsa_advantage` / `chr_dsa_disadvantage` – Vor-/Nachteile
- `chr_dsa_special_ability_general/combat/magic/terrain/clerical` – Sonderfähigkeiten
- `chr_dsa_talent_combat/physical/social/knowledge` – Talente

---

## Datumssystem

Die Welt hat einen eigenen Kalender in `time_system` (komplett anpassbar).

| Konzept | Beschreibung |
|---------|-------------|
| `World.start_date` | Tag 0 der Welt, z.B. "15. Praios 1000 BF" |
| `World.current_date` | Heute in der Welt (nach jeder Session gesetzt) |
| `Session.world_date_start` | In-World-Datum der Spielsitzung |

**Ort-Abfrage mit Datum:**
`GET /api/locations/LOC-123456/?at_date=15.+Firun+1000+BF`
→ System holt alle Sessions ≤ diesem Datum, wertet Konsequenzen aus, gibt Snapshot zurück.

---

## Entfernte Systeme

Folgende Systeme werden im Neuaufbau **nicht** implementiert:

- ~~`core_user`~~ – Benutzerverwaltung, Login, Authentifizierung
- ~~`core_user_security_question`~~ – Sicherheitsfragen
- ~~`core_user_user_world_role`~~ – World-spezifische Benutzerrollen
- ~~`wld_world_party`~~ / ~~`wld_world_party_membership`~~ – Party-System
- ~~`wld_world_api_keys`~~ – API-Schlüssel-Verwaltung
- ~~`dungeon_master`~~ – Gesamte DM-App
- ~~`permissions_permission`~~ – Granulares Berechtigungssystem

---

## Tabellen-Übersicht

| Tabelle | System | Status |
|---------|--------|--------|
| `wld_world_entity` | World | bestehend |
| `wld_region_entity` | World | bestehend |
| `wld_location_entity` | World | bestehend |
| `wld_npc_entity` | World | **neu** |
| `wld_location_snapshot` | World | **neu** |
| `adv_session` | Adventure | **neu** |
| `adv_session_character` | Adventure | **neu** |
| `adv_session_location` | Adventure | **neu** |
| `characters_character` | Characters | bestehend (vereinfacht) |
| `chr_ruleset` | Characters | bestehend |
| `chr_character_ruleset_data` | Characters | bestehend |
| `chr_character_*` | Characters | bestehend |
| `chr_dsa_*` | DSA Reference | bestehend |

---

*Erstellt: Februar 2026 – Neuaufbau ohne User-System und DM-Verwaltung*
