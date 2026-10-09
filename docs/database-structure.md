# Arcanovi - Datenbankstruktur Dokumentation

## Übersicht

Diese Dokumentation beschreibt die Datenbankstruktur der Arcanovi-Anwendung. Das System folgt einer **Feature-Driven Design (FDD)** Architektur mit vier Hauptbereichen:

- **Core User App** (`apps.core_user`) - Benutzerverwaltung und Authentifizierung
- **World App** (`apps.world`) - Weltenbau-System mit API-Keys und Party-System
- **Adventure App** (`apps.adventure`) - Kampagnen- und Abenteuer-Management  
- **Characters App** (`apps.characters`) - Charakter-Management-System

---

## 👤 Core User App - Benutzerverwaltung

### 1. User (`core_user_user`)

**Zweck**: Basis-Benutzermodell für alle Arcanovi-Nutzer  
**Erbt von**: Django's `AbstractUser`

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `email` | EmailField | Primäre Email-Adresse (USERNAME_FIELD) |
| `first_name` | CharField(150) | Vorname |
| `last_name` | CharField(150) | Nachname |
| `avatar` | ImageField | Benutzer-Avatar (Upload: `avatars/`) |
| `is_email_verified` | BooleanField | Email-Verifizierungsstatus |
| `date_joined` | DateTimeField | Registrierungsdatum |
| `last_login` | DateTimeField | Letzter Login |
| `is_active` | BooleanField | Account-Status |

### 2. SecurityQuestion (`core_user_security_question`)

**Zweck**: Vordefinierte Sicherheitsfragen für Password-Reset

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `question_text` | TextField | Sicherheitsfrage |
| `category` | CharField(50) | Kategorie (z.B. "childhood", "personal") |
| `is_active` | BooleanField | Aktiv-Status |

### 3. UserSecurityAnswer (`core_user_user_security_answer`)

**Zweck**: Gehashte Antworten auf Sicherheitsfragen

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `user` | ForeignKey(User) | Verknüpfung zum User |
| `question` | ForeignKey(SecurityQuestion) | Verknüpfung zur Frage |
| `hashed_answer` | CharField(255) | Gehashte Antwort |
| `created_at` | DateTimeField | Erstellungsdatum |

### 4. Role (`core_user_role`)

**Zweck**: Standard-Rollen für das System

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(50) | Rollenname (player, dungeon_master, world_admin) |
| `description` | TextField | Rollenbeschreibung |
| `permissions` | JSONField | Rollen-spezifische Berechtigungen |

### 5. UserWorldRole (`core_user_user_world_role`)

**Zweck**: Kontextspezifische Rollen-Zuweisungen pro World

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `user` | ForeignKey(User) | Verknüpfung zum User |
| `world` | ForeignKey(World) | Verknüpfung zur World |
| `role` | ForeignKey(Role) | Verknüpfung zur Rolle |
| `assigned_at` | DateTimeField | Zuweisungsdatum |
| `assigned_by` | ForeignKey(User) | Wer die Rolle zugewiesen hat |

---

## 🌍 World App - Weltenbau-System

### 1. World (`wld_world_entity`)

**Zweck**: Repräsentiert eine komplette Fantasy-Welt

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `entity_id` | CharField(20) | Eindeutige ID mit Format `WLD-{12_digit_id}` |
| `name` | CharField(200) | Name der Welt |
| `description` | TextField(5000) | Detaillierte Weltbeschreibung |
| `general_mood` | TextField(1000) | Allgemeine Atmosphäre |
| `pill` | JSONField(dict) | Schnell-Zusammenfassung |
| `created_by` | ForeignKey(User) | Ersteller der Welt |
| `is_active` | BooleanField | Welt-Status |

### 2. WorldAPIKeys (`wld_world_api_keys`)

**Zweck**: Verschlüsselte API-Schlüssel pro World

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `world` | OneToOneField(World) | Verknüpfung zur World |
| `openai_key_encrypted` | BinaryField | Verschlüsselter OpenAI API-Schlüssel |
| `anthropic_key_encrypted` | BinaryField | Verschlüsselter Anthropic API-Schlüssel |
| `google_key_encrypted` | BinaryField | Verschlüsselter Google API-Schlüssel |
| `deepseek_key_encrypted` | BinaryField | Verschlüsselter DeepSeek API-Schlüssel |
| `usage_statistics` | JSONField(dict) | Nutzungsstatistiken |

### 3. WorldParty (`wld_world_party`)

**Zweck**: Party-System pro World

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `world` | OneToOneField(World) | Verknüpfung zur World |
| `name` | CharField(200) | Name der Party |
| `description` | TextField(1000) | Party-Beschreibung |
| `current_dm` | ForeignKey(User) | Aktueller DM |
| `max_members` | IntegerField | Maximale Gruppengröße |
| `is_active` | BooleanField | Party-Status |

### 4. WorldPartyMembership (`wld_world_party_membership`)

**Zweck**: Party-Mitgliedschaften

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `party` | ForeignKey(WorldParty) | Verknüpfung zur Party |
| `user` | ForeignKey(User) | Verknüpfung zum User |
| `role` | CharField(50) | Rolle in der Party |
| `joined_at` | DateTimeField | Beitrittsdatum |
| `is_active` | BooleanField | Mitgliedschaft-Status |

---

## 🏰 Adventure App - Kampagnen-Management

### 1. Adventure (`adv_adventure`)

**Zweck**: Repräsentiert eine Kampagne oder ein einzelnes Abenteuer

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `entity_id` | CharField(20) | Eindeutige ID mit Format `adv-{12_digit_id}` |
| `world` | ForeignKey(World) | Verknüpfung zur World |
| `name` | CharField(255) | Name des Abenteuers |
| `description` | TextField | Detaillierte Beschreibung |
| `game_system` | CharField(100) | Spielsystem (z.B. DSA 4.1) |
| `adventure_settings` | JSONField(dict) | Abenteuer-spezifische Einstellungen |
| `status` | CharField(20) | Status (planning, active, paused, completed) |
| `created_by` | ForeignKey(User) | Ersteller des Abenteuers |

---

## 👥 Characters App - Charakter-Management-System

### 1. Character (`chr_character`)

**Zweck**: Basis-Charakter-Modell für alle Regelsysteme

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(200) | Charaktername |
| `user` | ForeignKey(User) | Besitzer des Charakters |
| `world` | ForeignKey(World) | Verknüpfung zur World |
| `ruleset` | ForeignKey(RuleSet) | Verknüpfung zum Regelsystem |
| `character_data` | JSONField | Regelsystem-spezifische Daten |
| `status` | CharField(20) | Status (draft, active, archived) |
| `created_at` | DateTimeField | Erstellungsdatum |

### 2. RuleSet (`chr_ruleset`)

**Zweck**: Verschiedene Regelsysteme (DSA 4.1, D&D 5e, etc.)

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(100) | Name des Regelsystems |
| `version` | CharField(20) | Version |
| `schema_definition` | JSONField | JSON-Schema für Validierung |
| `is_active` | BooleanField | Aktiv-Status |

### 3. CharacterRuleSetData (`chr_character_ruleset_data`)

**Zweck**: Regelsystem-spezifische Charakterdaten

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `character` | ForeignKey(Character) | Verknüpfung zum Charakter |
| `ruleset` | ForeignKey(RuleSet) | Verknüpfung zum Regelsystem |
| `data` | JSONField | Regelsystem-spezifische Daten |
| `version` | CharField(20) | Datenversion |

---

## 🎲 DSA 4.1 Referenz-Modelle

### 1. DSARace (`chr_dsa_race`)

**Zweck**: DSA 4.1 Rassen-Referenzdaten

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(50) | Rassenname |
| `attribute_modifiers` | JSONField | Attributs-Modifikatoren |
| `special_abilities` | JSONField | Rassen-spezifische Fähigkeiten |
| `gp_cost` | IntegerField | Generierungspunkte-Kosten |

### 2. DSACulture (`chr_dsa_culture`)

**Zweck**: DSA 4.1 Kulturen-Referenzdaten

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(50) | Kulturname |
| `language_bonuses` | JSONField | Sprach-Boni |
| `talent_bonuses` | JSONField | Talent-Boni |
| `social_status_range` | JSONField | Sozialstatus-Bereich |

### 3. DSAProfession (`chr_dsa_profession`)

**Zweck**: DSA 4.1 Professionen-Referenzdaten

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(50) | Professionsname |
| `requirements` | JSONField | Anforderungen |
| `starting_equipment` | JSONField | Startausrüstung |
| `talent_bonuses` | JSONField | Talent-Boni |

### 4. DSAAdvantage (`chr_dsa_advantage`)

**Zweck**: DSA 4.1 Vorteile-Referenzdaten

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(60) | Vorteilsname |
| `gp_cost` | IntegerField | GP-Kosten |
| `effects` | JSONField | Effekte |
| `requirements` | JSONField | Anforderungen |

### 5. DSADisadvantage (`chr_dsa_disadvantage`)

**Zweck**: DSA 4.1 Nachteile-Referenzdaten

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(60) | Nachteilsname |
| `gp_bonus` | IntegerField | GP-Bonus |
| `effects` | JSONField | Effekte |
| `restrictions` | JSONField | Einschränkungen |

---

## ⚔️ DSA 4.1 Sonderfähigkeiten-Modelle

### 1. DSASpecialAbilityGeneral (`chr_dsa_special_ability_general`)

**Zweck**: Allgemeine Sonderfähigkeiten

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(60) | Fähigkeitsname |
| `ap_cost_base` | IntegerField | Basis AP-Kosten |
| `ap_cost_per_level` | IntegerField | AP-Kosten pro Level |
| `max_levels` | IntegerField | Maximale Level |
| `category` | CharField(20) | Kategorie |
| `requirements` | JSONField | Anforderungen |
| `effects` | JSONField | Effekte |

### 2. DSASpecialAbilityCombat (`chr_dsa_special_ability_combat`)

**Zweck**: Kampfsonderfähigkeiten

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(60) | Fähigkeitsname |
| `combat_type` | CharField(20) | Kampftyp |
| `applicable_weapons` | JSONField | Anwendbare Waffen |
| `combat_situations` | JSONField | Kampfsituationen |
| `combat_mechanics` | JSONField | Kampfmechaniken |

### 3. DSASpecialAbilityMagic (`chr_dsa_special_ability_magic`)

**Zweck**: Magische Sonderfähigkeiten

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(60) | Fähigkeitsname |
| `magic_type` | CharField(20) | Magietyp |
| `magic_traditions` | JSONField | Magische Traditionen |
| `affected_categories` | JSONField | Betroffene Kategorien |
| `magic_mechanics` | JSONField | Magiemechaniken |

### 4. DSASpecialAbilityTerrain (`chr_dsa_special_ability_terrain`)

**Zweck**: Geländekunde Sonderfähigkeiten

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(60) | Fähigkeitsname |
| `terrain_type` | CharField(20) | Geländetyp |
| `terrain_bonuses` | JSONField | Gelände-Boni |
| `terrain_mechanics` | JSONField | Gelände-Mechaniken |

### 5. DSASpecialAbilityClerical (`chr_dsa_special_ability_clerical`)

**Zweck**: Geweihte Sonderfähigkeiten

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(60) | Fähigkeitsname |
| `clerical_type` | CharField(20) | Geweihtentyp |
| `deities` | JSONField | Gottheiten |
| `liturgy_categories` | JSONField | Liturgie-Kategorien |
| `clerical_mechanics` | JSONField | Geweihten-Mechaniken |

---

## 🎯 DSA 4.1 Talent-Modelle

### 1. DSATalentCombat (`chr_dsa_talent_combat`)

**Zweck**: Kampftalente

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(60) | Talentname |
| `combat_type` | CharField(20) | Kampftyp |
| `applicable_weapons` | JSONField | Anwendbare Waffen |
| `combat_bonuses` | JSONField | Kampf-Boni |
| `combat_rules` | JSONField | Kampfregeln |

### 2. DSATalentSocial (`chr_dsa_talent_social`)

**Zweck**: Soziale Talente

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(60) | Talentname |
| `social_type` | CharField(20) | Sozialtyp |
| `social_contexts` | JSONField | Soziale Kontexte |
| `social_bonuses` | JSONField | Soziale Boni |
| `social_rules` | JSONField | Soziale Regeln |

### 3. DSATalentKnowledge (`chr_dsa_talent_knowledge`)

**Zweck**: Wissens- und Sprachtalente

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(60) | Talentname |
| `knowledge_type` | CharField(20) | Wissenstyp |
| `knowledge_domains` | JSONField | Wissensbereiche |
| `language_difficulty` | CharField(1) | Sprachschwierigkeit |
| `script_required` | CharField(30) | Benötigte Schrift |

### 4. DSATalentPhysical (`chr_dsa_talent_physical`)

**Zweck**: Körperliche Talente

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `name` | CharField(60) | Talentname |
| `physical_type` | CharField(20) | Körperlicher Typ |
| `physical_contexts` | JSONField | Körperliche Kontexte |
| `physical_bonuses` | JSONField | Körperliche Boni |
| `environmental_modifiers` | JSONField | Umwelt-Modifikatoren |

---

## 🔗 Charakter-Verknüpfungs-Modelle

### 1. CharacterAdvantage (`chr_character_advantage`)

**Zweck**: Charakter-Vorteile

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `character` | ForeignKey(Character) | Verknüpfung zum Charakter |
| `advantage` | ForeignKey(DSAAdvantage) | Verknüpfung zum Vorteil |
| `custom_modifications` | JSONField | Benutzerdefinierte Modifikationen |
| `acquisition_data` | JSONField | Erwerbsdaten |

### 2. CharacterDisadvantage (`chr_character_disadvantage`)

**Zweck**: Charakter-Nachteile

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `character` | ForeignKey(Character) | Verknüpfung zum Charakter |
| `disadvantage` | ForeignKey(DSADisadvantage) | Verknüpfung zum Nachteil |
| `custom_modifications` | JSONField | Benutzerdefinierte Modifikationen |
| `acquisition_data` | JSONField | Erwerbsdaten |

### 3. CharacterSpecialAbility (`chr_character_special_ability`)

**Zweck**: Charakter-Sonderfähigkeiten

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `character` | ForeignKey(Character) | Verknüpfung zum Charakter |
| `special_ability_data` | JSONField | Sonderfähigkeitsdaten |
| `level` | IntegerField | Level der Fähigkeit |
| `specializations` | JSONField | Spezialisierungen |
| `acquisition_data` | JSONField | Erwerbsdaten |

### 4. CharacterTalent (`chr_character_talent`)

**Zweck**: Charakter-Talente

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `character` | ForeignKey(Character) | Verknüpfung zum Charakter |
| `talent_data` | JSONField | Talentdaten |
| `value` | IntegerField | Talentwert |
| `specializations` | JSONField | Spezialisierungen |
| `acquisition_data` | JSONField | Erwerbsdaten |

### 5. CharacterSpell (`chr_character_spell`)

**Zweck**: Charakter-Zauber

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `character` | ForeignKey(Character) | Verknüpfung zum Charakter |
| `spell_data` | JSONField | Zauberdaten |
| `level` | IntegerField | Zauberlevel |
| `modifications` | JSONField | Modifikationen |
| `casting_history` | JSONField | Zauberhistorie |

### 6. CharacterLiturgy (`chr_character_liturgy`)

**Zweck**: Charakter-Liturgien

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `character` | ForeignKey(Character) | Verknüpfung zum Charakter |
| `liturgy_data` | JSONField | Liturgiedaten |
| `level` | IntegerField | Liturgielevel |
| `deity_data` | JSONField | Gottheitsdaten |
| `casting_history` | JSONField | Liturgiehistorie |

### 7. CharacterEquipment (`chr_character_equipment`)

**Zweck**: Charakter-Ausrüstung

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `character` | ForeignKey(Character) | Verknüpfung zum Charakter |
| `equipment_data` | JSONField | Ausrüstungsdaten |
| `equipment_type` | CharField(20) | Ausrüstungstyp |
| `status` | CharField(20) | Status |
| `quantity` | IntegerField | Menge |
| `condition` | IntegerField | Zustand (0-100) |

### 8. CharacterFamily (`chr_character_family`)

**Zweck**: Charakter-Familienbeziehungen

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `character` | ForeignKey(Character) | Verknüpfung zum Charakter |
| `related_character` | ForeignKey(Character) | Verknüpfung zum verwandten Charakter |
| `relationship_type` | CharField(20) | Beziehungstyp |
| `relationship_status` | CharField(20) | Beziehungsstatus |
| `family_member_data` | JSONField | Familienmitgliedsdaten |
| `relationship_details` | JSONField | Beziehungsdetails |

---

## 🔐 Permission-System

### 1. Permission (`permissions_permission`)

**Zweck**: Granulares Permission-System

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | UUIDField | Eindeutige UUID |
| `user` | ForeignKey(User) | Verknüpfung zum User |
| `resource_type` | CharField(20) | Ressourcentyp |
| `resource_id` | UUIDField | Ressourcen-ID |
| `permission_type` | CharField(20) | Berechtigungstyp |
| `granted_at` | DateTimeField | Gewährungsdatum |
| `granted_by` | ForeignKey(User) | Wer die Berechtigung gewährt hat |

---

## 📊 Tabellen-Präfixe Übersicht

### Core User System
- `core_user_user` - Hauptbenutzer
- `core_user_security_question` - Sicherheitsfragen
- `core_user_user_security_answer` - Benutzerantworten
- `core_user_role` - Rollen
- `core_user_user_world_role` - World-spezifische Rollen

### World System
- `wld_world_entity` - Welten
- `wld_region_entity` - Regionen
- `wld_location_entity` - Orte
- `wld_world_api_keys` - API-Schlüssel
- `wld_world_party` - Parties
- `wld_world_party_membership` - Party-Mitgliedschaften

### Adventure System
- `adv_adventure` - Abenteuer

### Character System
- `chr_character` - Charaktere
- `chr_ruleset` - Regelsysteme
- `chr_character_ruleset_data` - Regelsystem-Daten

### DSA Reference Data
- `chr_dsa_race` - Rassen
- `chr_dsa_culture` - Kulturen
- `chr_dsa_profession` - Professionen
- `chr_dsa_advantage` - Vorteile
- `chr_dsa_disadvantage` - Nachteile

### DSA Special Abilities
- `chr_dsa_special_ability_general` - Allgemeine Sonderfähigkeiten
- `chr_dsa_special_ability_combat` - Kampfsonderfähigkeiten
- `chr_dsa_special_ability_magic` - Magische Sonderfähigkeiten
- `chr_dsa_special_ability_terrain` - Geländekunde
- `chr_dsa_special_ability_clerical` - Geweihte Sonderfähigkeiten

### DSA Talents
- `chr_dsa_talent_combat` - Kampftalente
- `chr_dsa_talent_social` - Soziale Talente
- `chr_dsa_talent_knowledge` - Wissens- und Sprachtalente
- `chr_dsa_talent_physical` - Körperliche Talente

### Character Linking Models
- `chr_character_advantage` - Charakter-Vorteile
- `chr_character_disadvantage` - Charakter-Nachteile
- `chr_character_special_ability` - Charakter-Sonderfähigkeiten
- `chr_character_talent` - Charakter-Talente
- `chr_character_spell` - Charakter-Zauber
- `chr_character_liturgy` - Charakter-Liturgien
- `chr_character_equipment` - Charakter-Ausrüstung
- `chr_character_family` - Charakter-Familienbeziehungen

### Permission System
- `permissions_permission` - Berechtigungen

---

## 🔗 Beziehungen und Hierarchien

### Benutzer-Hierarchie
```
User (1) → UserWorldRole (n) → World (n)
User (1) → Character (n) → World (1)
```

### World-Hierarchie
```
World (1) → WorldAPIKeys (1)
World (1) → WorldParty (1) → WorldPartyMembership (n) → User (n)
World (1) → Adventure (n)
World (1) → Region (n) → Location (n)
```

### Character-Hierarchie
```
Character (1) → CharacterRuleSetData (1) → RuleSet (1)
Character (1) → CharacterAdvantage (n) → DSAAdvantage (n)
Character (1) → CharacterDisadvantage (n) → DSADisadvantage (n)
Character (1) → CharacterSpecialAbility (n)
Character (1) → CharacterTalent (n)
Character (1) → CharacterSpell (n)
Character (1) → CharacterLiturgy (n)
Character (1) → CharacterEquipment (n)
Character (1) → CharacterFamily (n) → Character (n)
```

---

## 📝 Wichtige Constraints

1. **Unique Names**: Welten müssen eindeutige Namen haben
2. **Unique Names**: Regionen müssen eindeutige Namen pro Welt haben
3. **Unique Names**: Orte müssen eindeutige Namen pro Region haben
4. **One DM per World**: Nur ein aktiver DM pro World
5. **Character Ownership**: Charaktere gehören einem User
6. **World Membership**: Charaktere gehören einer World
7. **Permission Hierarchy**: admin > delete > edit > view

---

*Dokumentation erstellt am: 26. Januar 2025*  
*Version: 2.0 - Vollständige DSA 4.1 Integration* 