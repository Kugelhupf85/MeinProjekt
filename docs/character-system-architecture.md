# Character-Management-System - Architektur & Database-Schema

## 🎯 Überblick

Das Character-Management-System ist darauf ausgelegt, verschiedene Pen & Paper Regelsysteme zu unterstützen, wobei DSA 4.1 (Das Schwarze Auge) die primäre Implementation darstellt. Das System nutzt eine flexible JSON-basierte Architektur kombiniert mit strukturierten Referenz-Tabellen.

---

## 🏗️ **Core Architecture**

### **Multi-RuleSet-Design-Prinzipien:**
- **Generic Core Model**: Zentrale `Character`-Tabelle mit Basis-Informationen
- **RuleSet-Specific Extensions**: Erweiterte Daten als JSON-Felder
- **Reference Tables**: Strukturierte Daten für Races, Cultures, Professions, etc.
- **Flexible Linking**: Many-to-Many-Beziehungen für Advantages, Special Abilities, Talents

---

## 📊 **Database Schema Overview**

```
characters/
├── Character (Core Model)
├── RuleSet (System Definitions)
├── CharacterRuleSetData (Extended Data per RuleSet)
│
├── DSA 4.1 Reference Tables:
│   ├── DSARace
│   ├── DSACulture  
│   ├── DSAProfession
│   ├── DSAAdvantage
│   ├── DSADisadvantage
│   │
│   ├── DSA Special Abilities:
│   │   ├── DSASpecialAbilityGeneral
│   │   ├── DSASpecialAbilityTerrain
│   │   ├── DSASpecialAbilityCombat (Fernkampf/Nahkampf/Manöver)
│   │   ├── DSASpecialAbilityMagic (Magisch/Merkmalskenntnis/Objektritual/Ritualkenntnis)
│   │   └── DSASpecialAbilityClerical (Geweiht)
│   │
│   └── DSA Talents:
│       ├── DSATalentCombat
│       ├── DSATalentPhysical
│       ├── DSATalentSocial
│       ├── DSATalentNature
│       ├── DSATalentKnowledge
│       ├── DSATalentLanguage
│       ├── DSATalentScript
│       ├── DSATalentCraft
│       └── DSATalentSpecial
│
└── Character Linking Tables:
    ├── CharacterAdvantage
    ├── CharacterDisadvantage
    ├── CharacterSpecialAbility
    └── CharacterTalent
```

---

## 🎲 **Core Models**

### **1. Character (Central Model)**

```python
class Character(models.Model):
    # Core Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey('core_user.User', on_delete=models.CASCADE)
    world = models.ForeignKey('world.World', on_delete=models.CASCADE)
    rule_set = models.ForeignKey('RuleSet', on_delete=models.PROTECT)
    
    # Basic Character Info
    name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('archived', 'Archived')
        ],
        default='draft'
    )
    
    # Core Attributes (JSON - flexible per RuleSet)
    core_attributes = models.JSONField(default=dict)
    # Example: {"rule_set": "dsa_4_1", "MU": 14, "KL": 13, "IN": 12, ...}
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'characters_character'
        unique_together = ['user', 'world', 'name']
```

### **2. RuleSet (System Definitions)**

```python
class RuleSet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50, unique=True)
    # Examples: "dsa_4_1", "dungeons_and_dragons_5e", "pathfinder_2e"
    
    display_name = models.CharField(max_length=100)
    # Examples: "DSA 4.1", "D&D 5E", "Pathfinder 2E"
    
    version = models.CharField(max_length=20)
    
    # JSON Schema for validation of core_attributes
    attribute_schema = models.JSONField(default=dict)
    # Example: {"required": ["MU", "KL", "IN"], "properties": {"MU": {"type": "integer", "minimum": 8, "maximum": 20}}}
    
    # Default values for character creation
    default_values = models.JSONField(default=dict)
    # Example: {"generation_points_max": 110, "attribute_points_max": 100, "attribute_maximum": 14}
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'characters_ruleset'
```

### **3. CharacterRuleSetData (Extended RuleSet-specific Data)**

```python
class CharacterRuleSetData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character = models.OneToOneField('Character', on_delete=models.CASCADE, related_name='ruleset_data')
    
    # DSA 4.1 Specific Fields
    # Generation Data (wichtig für Charaktererstellung)
    generation_points_max = models.IntegerField(default=110)
    generation_points_attributes_max = models.IntegerField(default=100)
    attribute_maximum = models.IntegerField(default=14)
    
    # Experience & Level
    xp_total = models.IntegerField(default=0)
    xp_current = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    
    # Personal Data
    birthday = models.CharField(max_length=50, blank=True)
    age = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)  # in kg
    height = models.IntegerField(null=True, blank=True)  # in cm
    gender = models.CharField(max_length=20, blank=True)
    hair_color = models.CharField(max_length=30, blank=True)
    eye_color = models.CharField(max_length=30, blank=True)
    
    # DSA 4.1 Derived Values (calculated from core_attributes)
    magic_resistance = models.IntegerField(default=0)  # Magieresistenz (MR)
    life_energy = models.IntegerField(default=0)       # Lebensenergie (LE)
    endurance = models.IntegerField(default=0)         # Ausdauer (AU)
    astral_energy = models.IntegerField(null=True, blank=True)  # Astralenergie (AE) - nur für Magier
    karma_energy = models.IntegerField(null=True, blank=True)   # Karmaenergie (KE) - nur für Geweihte
    
    # Combat Values
    attack_base = models.IntegerField(default=0)       # Attacke-Basis (AT)
    parade_base = models.IntegerField(default=0)       # Parade-Basis (PA)
    ranged_combat_base = models.IntegerField(default=0) # Fernkampf-Basis (FK)
    initiative = models.IntegerField(default=0)        # Initiative (INI)
    
    # Social Values
    social_status = models.IntegerField(default=1)     # Sozialstatus
    guild_membership = models.CharField(max_length=100, blank=True)  # Gildenzugehörigkeit
    
    # Extended Data (JSON for flexibility)
    extended_data = models.JSONField(default=dict)
    # For future RuleSets or additional data
    
    class Meta:
        db_table = 'characters_character_ruleset_data'
```

---

## 🏛️ **DSA 4.1 Reference Tables**

### **Race System**

```python
class DSARace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50, unique=True)
    # Examples: "Mensch", "Elf", "Zwerg", "Halbling", "Ork"
    
    # Attribute Modifiers (JSON)
    attribute_modifiers = models.JSONField(default=dict)
    # Example: {"MU": 0, "KL": 1, "IN": 0, "CH": 0, "FF": 1, "GE": 0, "KO": -1, "KK": 0}
    
    # Special Abilities granted by race
    granted_special_abilities = models.JSONField(default=list)
    # Example: ["Infrared Vision", "Resistance to Magic"]
    
    # Starting modifications (JSON)
    starting_modifications = models.JSONField(default=dict)
    # Example: {"life_points": 5, "astral_energy": -5, "social_status": {"min": 1, "max": 6}}
    
    # Generation Point Cost
    generation_point_cost = models.IntegerField(default=0)
    
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'characters_dsa_race'
```

### **Culture System**

```python
class DSACulture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50, unique=True)
    # Examples: "Mittelreich", "Horasreich", "Bornland", "Thorwal"
    
    # Language Bonuses (JSON)
    language_bonuses = models.JSONField(default=dict)
    # Example: {"Garethi": 10, "Bosparano": 7, "Alaani": 4}
    
    # Script Bonuses (JSON) 
    script_bonuses = models.JSONField(default=dict)
    # Example: {"Kusliker Zeichen": 8, "Imperiale Zeichen": 5}
    
    # Talent Modifications (JSON)
    talent_modifications = models.JSONField(default=dict)
    # Example: {"Reiten": 2, "Schwimmen": -2, "Singen": 1}
    
    # Typical Professions (JSON list)
    typical_professions = models.JSONField(default=list)
    # Example: ["Krieger", "Handwerker", "Gelehrter"]
    
    # Social Status Range
    social_status_min = models.IntegerField(default=1)
    social_status_max = models.IntegerField(default=6)
    
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'characters_dsa_culture'
```

### **Profession System**

```python
class DSAProfession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50, unique=True)
    # Examples: "Krieger", "Magier", "Geweihter", "Streuner", "Handwerker"
    
    category = models.CharField(
        max_length=20,
        choices=[
            ('mundane', 'Mundane'),
            ('magic', 'Magic User'), 
            ('clerical', 'Blessed One'),
            ('combat', 'Fighter')
        ]
    )
    
    # Attribute Requirements (JSON)
    attribute_requirements = models.JSONField(default=dict)
    # Example: {"MU": 13, "KL": 11, "IN": 12} for Magier
    
    # Talent Bonuses (JSON)
    talent_bonuses = models.JSONField(default=dict)
    # Example: {"Schwerter": 5, "Raufen": 3, "Körperbeherrschung": 4}
    
    # Special Abilities granted (JSON)
    granted_special_abilities = models.JSONField(default=list)
    # Example: ["Kampfreflexe", "Wuchtschlag"] for Krieger
    
    # Starting Equipment (JSON)
    starting_equipment = models.JSONField(default=dict)
    # Example: {"weapons": ["Schwert", "Schild"], "armor": ["Lederrüstung"], "money": 150}
    
    # Generation Point Cost
    generation_point_cost = models.IntegerField(default=0)
    
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'characters_dsa_profession'
```

---

## ⚡ **Advantages & Disadvantages System**

### **DSA Advantages**

```python
class DSAAdvantage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    # Examples: "Glück", "Hohe Lebenskraft", "Verbesserte Regeneration"
    
    # Generation Point Cost (can be variable)
    gp_cost_base = models.IntegerField()
    gp_cost_per_level = models.IntegerField(default=0)  # For scalable advantages
    
    # Maximum levels (1 for binary advantages)
    max_levels = models.IntegerField(default=1)
    
    # Requirements (JSON)
    requirements = models.JSONField(default=dict)
    # Example: {"attributes": {"MU": 13}, "other_advantages": ["Magiedilettant"]}
    
    # Effects (JSON)
    effects = models.JSONField(default=dict)
    # Example: {"life_points": 7, "regeneration_bonus": 1}
    
    # Incompatible with (JSON list)
    incompatible_with = models.JSONField(default=list)
    # Example: ["Pech", "Niedrige Lebenskraft"]
    
    category = models.CharField(max_length=30, blank=True)
    # Examples: "Körperlich", "Geistig", "Sozial", "Übernatürlich"
    
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'characters_dsa_advantage'
```

### **DSA Disadvantages**

```python
class DSADisadvantage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    # Examples: "Pech", "Niedrige Lebenskraft", "Aberglaube"
    
    # Generation Points gained (positive value)
    gp_gain_base = models.IntegerField()
    gp_gain_per_level = models.IntegerField(default=0)
    
    max_levels = models.IntegerField(default=1)
    
    # Effects (JSON)
    effects = models.JSONField(default=dict)
    # Example: {"life_points": -7, "social_status": -1}
    
    # Incompatible with (JSON list)
    incompatible_with = models.JSONField(default=list)
    # Example: ["Glück", "Hohe Lebenskraft"]
    
    category = models.CharField(max_length=30, blank=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'characters_dsa_disadvantage'
```

---

## 🌟 **Special Abilities System**

### **General Special Abilities**

```python
class DSASpecialAbilityGeneral(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    # Examples: "Kampfreflexe", "Wuchtschlag", "Berittener Kampf"
    
    # AP (Adventure Point) Cost
    ap_cost_base = models.IntegerField()
    ap_cost_per_level = models.IntegerField(default=0)
    max_levels = models.IntegerField(default=1)
    
    # Requirements (JSON)
    requirements = models.JSONField(default=dict)
    # Example: {"attributes": {"GE": 13, "KK": 15}, "talents": {"Schwerter": 10}, "special_abilities": ["Kampfreflexe"]}
    
    # Effects (JSON)
    effects = models.JSONField(default=dict)
    # Example: {"attack_bonus": 2, "damage_bonus": 1}
    
    category = models.CharField(max_length=30, default="Allgemein")
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'characters_dsa_special_ability_general'
```

### **Combat Special Abilities (Fernkampf/Nahkampf/Manöver)**

```python
class DSASpecialAbilityCombat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    
    combat_type = models.CharField(
        max_length=20,
        choices=[
            ('melee', 'Nahkampf'),
            ('ranged', 'Fernkampf'), 
            ('maneuver', 'Manöver')
        ]
    )
    
    ap_cost_base = models.IntegerField()
    ap_cost_per_level = models.IntegerField(default=0)
    max_levels = models.IntegerField(default=1)
    
    # Weapon/Combat restrictions (JSON)
    applicable_weapons = models.JSONField(default=list)
    # Example: ["Schwerter", "Säbel", "Anderthalbhänder"] for specific maneuvers
    
    requirements = models.JSONField(default=dict)
    effects = models.JSONField(default=dict)
    
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'characters_dsa_special_ability_combat'
```

### **Magic Special Abilities (Magisch/Merkmalskenntnis/Objektritual/Ritualkenntnis)**

```python
class DSASpecialAbilityMagic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    
    magic_type = models.CharField(
        max_length=20,
        choices=[
            ('general', 'Magisch'),
            ('spell_knowledge', 'Merkmalskenntnis'),
            ('object_ritual', 'Objektritual'),
            ('ritual_knowledge', 'Ritualkenntnis')
        ]
    )
    
    ap_cost_base = models.IntegerField()
    ap_cost_per_level = models.IntegerField(default=0)
    max_levels = models.IntegerField(default=1)
    
    # Magic school/tradition restrictions (JSON)
    magic_traditions = models.JSONField(default=list)
    # Example: ["Gildenmagier", "Hexe", "Druide"]
    
    # Spell/Ritual categories affected (JSON)
    affected_categories = models.JSONField(default=list)
    # Example: ["Elementar", "Heilung", "Illusion"] for Merkmalskenntnis
    
    requirements = models.JSONField(default=dict)
    effects = models.JSONField(default=dict)
    
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'characters_dsa_special_ability_magic'
```

### **Terrain Knowledge (Geländekunde)**

```python
class DSASpecialAbilityTerrain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    # Examples: "Geländekunde (Wald)", "Geländekunde (Gebirge)", "Geländekunde (Städte)"
    
    terrain_type = models.CharField(max_length=30)
    # Examples: "Wald", "Gebirge", "Wüste", "Städte", "Sümpfe"
    
    ap_cost_base = models.IntegerField(default=3)
    
    # Bonuses granted in this terrain (JSON)
    terrain_bonuses = models.JSONField(default=dict)
    # Example: {"survival": 3, "tracking": 2, "stealth": 1}
    
    requirements = models.JSONField(default=dict)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'characters_dsa_special_ability_terrain'
```

### **Clerical Special Abilities (Geweiht)**

```python
class DSASpecialAbilityClerical(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    
    # Deity/Church restrictions (JSON)
    deities = models.JSONField(default=list)
    # Example: ["Praios", "Rondra", "Efferd"]
    
    ap_cost_base = models.IntegerField()
    ap_cost_per_level = models.IntegerField(default=0)
    max_levels = models.IntegerField(default=1)
    
    # Liturgy categories affected (JSON)
    liturgy_categories = models.JSONField(default=list)
    # Example: ["Heilung", "Schutz", "Kampf"]
    
    requirements = models.JSONField(default=dict)
    effects = models.JSONField(default=dict)
    
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'characters_dsa_special_ability_clerical'
```

---

## 🎯 **Talent System**

### **Base Talent Structure**

```python
class DSATalentBase(models.Model):
    """Abstract base class for all DSA talent categories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    
    # Governing attributes (JSON - usually 3 attributes)
    governing_attributes = models.JSONField(default=list)
    # Example: ["MU", "KL", "IN"] for most knowledge talents
    
    # Base difficulty for improvement
    improvement_factor = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')],
        default='B'
    )
    
    # Whether this talent can be used untrained
    untrained_use = models.BooleanField(default=True)
    untrained_penalty = models.IntegerField(default=0)  # Usually -3
    
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
```

### **Combat Talents**

```python
class DSATalentCombat(DSATalentBase):
    """Kampftalente - Schwerter, Bögen, Raufen, etc."""
    
    weapon_category = models.CharField(
        max_length=20,
        choices=[
            ('melee', 'Nahkampf'),
            ('ranged', 'Fernkampf'),
            ('unarmed', 'Raufen')
        ]
    )
    
    # Specific weapons this talent covers (JSON)
    applicable_weapons = models.JSONField(default=list)
    # Example: ["Anderthalbhänder", "Bastardschwerter", "Schwerter"] for Schwerter talent
    
    class Meta:
        db_table = 'characters_dsa_talent_combat'
```

### **Physical Talents**

```python
class DSATalentPhysical(DSATalentBase):
    """Körpertalente - Klettern, Schwimmen, Zechen, etc."""
    
    # Physical category for grouping
    physical_category = models.CharField(
        max_length=20,
        choices=[
            ('athletics', 'Athletik'),
            ('endurance', 'Ausdauer'),
            ('dexterity', 'Geschicklichkeit'),
            ('resistance', 'Widerstand')
        ],
        blank=True
    )
    
    class Meta:
        db_table = 'characters_dsa_talent_physical'
```

### **Social Talents**

```python
class DSATalentSocial(DSATalentBase):
    """Gesellschaftstalente - Überreden, Menschenkenntnis, Etikette, etc."""
    
    # Social interaction type
    interaction_type = models.CharField(
        max_length=20,
        choices=[
            ('persuasion', 'Überzeugung'),
            ('deception', 'Täuschung'),
            ('insight', 'Menschenkenntnis'),
            ('performance', 'Darbietung'),
            ('etiquette', 'Etikette')
        ],
        blank=True
    )
    
    class Meta:
        db_table = 'characters_dsa_talent_social'
```

### **Nature Talents**

```python
class DSATalentNature(DSATalentBase):
    """Naturtalente - Fährtensuchen, Wildnisleben, Tierkunde, etc."""
    
    nature_category = models.CharField(
        max_length=20,
        choices=[
            ('survival', 'Überleben'),
            ('tracking', 'Spurenlesen'),
            ('animal_handling', 'Tierkunde'),
            ('herbalism', 'Pflanzenkunde')
        ],
        blank=True
    )
    
    class Meta:
        db_table = 'characters_dsa_talent_nature'
```

### **Knowledge Talents**

```python
class DSATalentKnowledge(DSATalentBase):
    """Wissenstalente - Götter/Kulte, Geschichte, Magiekunde, etc."""
    
    knowledge_domain = models.CharField(
        max_length=30,
        choices=[
            ('history', 'Geschichte'),
            ('religion', 'Götter/Kulte'),
            ('magic', 'Magiekunde'),
            ('geography', 'Geographie'),
            ('law', 'Rechtskunde'),
            ('medicine', 'Heilkunde'),
            ('alchemy', 'Alchimie')
        ],
        blank=True
    )
    
    class Meta:
        db_table = 'characters_dsa_talent_knowledge'
```

### **Language Talents**

```python
class DSATalentLanguage(DSATalentBase):
    """Sprachtalente - Garethi, Bosparano, Alaani, etc."""
    
    language_family = models.CharField(
        max_length=20,
        choices=[
            ('human', 'Menschensprachen'),
            ('elven', 'Elfensprachen'),
            ('dwarven', 'Zwergische Sprachen'),
            ('ancient', 'Alte Sprachen'),
            ('exotic', 'Exotische Sprachen')
        ],
        blank=True
    )
    
    # Complexity for learning
    complexity_level = models.IntegerField(default=1)  # 1-5, higher = more complex
    
    class Meta:
        db_table = 'characters_dsa_talent_language'
```

### **Script Talents**

```python
class DSATalentScript(DSATalentBase):
    """Schriftentalente - Kusliker Zeichen, Imperiale Zeichen, etc."""
    
    script_family = models.CharField(
        max_length=20,
        choices=[
            ('common', 'Gewöhnliche Schriften'),
            ('ancient', 'Alte Schriften'),
            ('magical', 'Magische Schriften'),
            ('exotic', 'Exotische Schriften')
        ],
        blank=True
    )
    
    complexity_level = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'characters_dsa_talent_script'
```

### **Craft Talents**

```python
class DSATalentCraft(DSATalentBase):
    """Handwerkstalente - Schmieden, Lederarbeiten, Kochen, etc."""
    
    craft_category = models.CharField(
        max_length=20,
        choices=[
            ('metalworking', 'Metallverarbeitung'),
            ('woodworking', 'Holzverarbeitung'),
            ('textiles', 'Textilverarbeitung'),
            ('food', 'Nahrungsmittel'),
            ('artistic', 'Künstlerisch'),
            ('mechanical', 'Mechanisch')
        ],
        blank=True
    )
    
    # Tools/workshop requirements (JSON)
    required_tools = models.JSONField(default=list)
    # Example: ["Schmiede", "Amboss", "Hammer"] for Schmieden
    
    class Meta:
        db_table = 'characters_dsa_talent_craft'
```

### **Special Talents**

```python
class DSATalentSpecial(DSATalentBase):
    """Sondertalente - Rare or unique talents"""
    
    rarity = models.CharField(
        max_length=20,
        choices=[
            ('uncommon', 'Ungewöhnlich'),
            ('rare', 'Selten'),
            ('very_rare', 'Sehr selten'),
            ('legendary', 'Legendär')
        ],
        default='uncommon'
    )
    
    # Special requirements (JSON)
    special_requirements = models.JSONField(default=dict)
    # Example: {"advantages": ["Magiedilettant"], "professions": ["Magier"]}
    
    class Meta:
        db_table = 'characters_dsa_talent_special'
```

---

## 🔗 **Character Linking Tables**

### **Character-Race Link**

```python
class CharacterRace(models.Model):
    character = models.OneToOneField('Character', on_delete=models.CASCADE, related_name='race_data')
    race = models.ForeignKey('DSARace', on_delete=models.PROTECT)
    
    # Custom modifications for this character (JSON)
    custom_modifiers = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'characters_character_race'
```

### **Character-Culture Link**

```python
class CharacterCulture(models.Model):
    character = models.OneToOneField('Character', on_delete=models.CASCADE, related_name='culture_data')
    culture = models.ForeignKey('DSACulture', on_delete=models.PROTECT)
    
    # Custom modifications (JSON)
    custom_modifiers = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'characters_character_culture'
```

### **Character-Profession Links**

```python
class CharacterProfession(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='professions')
    profession = models.ForeignKey('DSAProfession', on_delete=models.PROTECT)
    
    # Profession order (1st, 2nd, 3rd)
    profession_order = models.IntegerField(
        choices=[(1, '1. Profession'), (2, '2. Profession'), (3, '3. Profession')]
    )
    
    # Custom modifications (JSON)
    custom_modifiers = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'characters_character_profession'
        unique_together = ['character', 'profession_order']
```

### **Character-Advantage Link**

```python
class CharacterAdvantage(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='advantages')
    advantage = models.ForeignKey('DSAAdvantage', on_delete=models.PROTECT)
    
    # Level taken (for scalable advantages)
    level = models.IntegerField(default=1)
    
    # Custom notes/modifications (JSON)
    custom_data = models.JSONField(default=dict)
    
    # Generation Points spent
    gp_cost = models.IntegerField()
    
    class Meta:
        db_table = 'characters_character_advantage'
        unique_together = ['character', 'advantage']
```

### **Character-Disadvantage Link**

```python
class CharacterDisadvantage(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='disadvantages')
    disadvantage = models.ForeignKey('DSADisadvantage', on_delete=models.PROTECT)
    
    level = models.IntegerField(default=1)
    custom_data = models.JSONField(default=dict)
    
    # Generation Points gained
    gp_gain = models.IntegerField()
    
    class Meta:
        db_table = 'characters_character_disadvantage'
        unique_together = ['character', 'disadvantage']
```

### **Character-Special Ability Link**

```python
class CharacterSpecialAbility(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='special_abilities')
    
    # Generic Foreign Key to any special ability type
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    special_ability = GenericForeignKey('content_type', 'object_id')
    
    level = models.IntegerField(default=1)
    custom_data = models.JSONField(default=dict)
    
    # Adventure Points spent
    ap_cost = models.IntegerField()
    
    # When acquired
    acquired_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'characters_character_special_ability'
        unique_together = ['character', 'content_type', 'object_id']
```

### **Character-Talent Link**

```python
class CharacterTalent(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='talents')
    
    # Generic Foreign Key to any talent type
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    talent = GenericForeignKey('content_type', 'object_id')
    
    # Current talent value
    value = models.IntegerField(default=0)
    
    # Specializations (JSON list)
    specializations = models.JSONField(default=list)
    # Example: ["Langschwert", "Säbel"] for Schwerter talent
    
    # Custom modifications (JSON)
    custom_modifiers = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'characters_character_talent'
        unique_together = ['character', 'content_type', 'object_id']
```

---

## 🎒 **Inventory Integration**

Das Character-System ist darauf ausgelegt, mit einer separaten **Inventory-App** zu arbeiten. Die Verknüpfung erfolgt über die Character-UUID.

### **Character-Inventory Relationship**

```python
# In der separaten inventory app
class CharacterInventory(models.Model):
    character_id = models.UUIDField()  # Reference to Character.id
    # Inventory-specific fields...
    
    class Meta:
        db_table = 'inventory_character_inventory'
```

### **Integration Points**

- **Character.id (UUID)** als Foreign Key für Inventory-Items
- **Separate App** für komplexe Inventory-Logic (Gewicht, Kapazität, etc.)
- **API-Integration** zwischen Character- und Inventory-Services
- **Permission-System** shared zwischen beiden Apps

---

## 💾 **JSON Data Examples**

### **Character Core Attributes (DSA 4.1) - Erweitert**

```json
{
    "rule_set": "dsa_4_1",
    "attributes": {
        "MU": 14,    // Mut
        "KL": 14,    // Klugheit  
        "IN": 14,    // Intuition
        "CH": 14,    // Charisma
        "FF": 9,     // Fingerfertigkeit
        "GE": 12,    // Gewandtheit
        "KO": 13,    // Konstitution
        "KK": 11     // Körperkraft
    },
    "derived_values": {
        "LE": 31,    // Lebensenergie
        "AU": 31,    // Ausdauer
        "AE": null,  // Astralenergie (null wenn kein Magier)
        "KE": 24,    // Karmaenergie (für Geweihte)
        "MR": 10,    // Magieresistenz
        "INI": 11,   // Initiative
        "AT": 7,     // Attacke-Basis
        "PA": 7,     // Parade-Basis
        "FK": 7,     // Fernkampf-Basis
        "GS": 8      // Geschwindigkeit (calculated)
    },
    "social_values": {
        "social_status": 11,
        "guild_membership": "Gildenzugehörigkeit"
    }
}
```

### **Character Advantage Data**

```json
{
    "advantages": [
        {
            "advantage_id": "uuid-glück",
            "name": "Glück",
            "level": 2,
            "gp_cost": 10,
            "effects": {
                "schips_per_session": 2,
                "reroll_bonus": true
            }
        },
        {
            "advantage_id": "uuid-hohe-lebenskraft", 
            "name": "Hohe Lebenskraft",
            "level": 1,
            "gp_cost": 15,
            "effects": {
                "life_points_bonus": 7
            }
        }
    ]
}
```

### **Character Special Abilities Data**

```json
{
    "special_abilities": {
        "general": [
            {
                "ability_id": "uuid-kampfreflexe",
                "name": "Kampfreflexe", 
                "level": 1,
                "ap_cost": 10,
                "effects": {
                    "initiative_bonus": 4,
                    "surprise_resistance": true
                }
            }
        ],
        "combat": [
            {
                "ability_id": "uuid-wuchtschlag",
                "name": "Wuchtschlag",
                "level": 2,
                "ap_cost": 15,
                "applicable_weapons": ["Schwerter", "Äxte"],
                "effects": {
                    "damage_bonus": 2,
                    "attack_penalty": -2
                }
            }
        ],
        "magic": [
            {
                "ability_id": "uuid-merkmalskenntnis-elementar",
                "name": "Merkmalskenntnis (Elementar)",
                "level": 1, 
                "ap_cost": 3,
                "effects": {
                    "spell_bonus": 1,
                    "affected_spells": ["Ignifaxius", "Aquafaxius", "Aerofugo"]
                }
            }
        ]
    }
}
```

### **Character Talent Data**

```json
{
    "talents": {
        "combat": [
            {
                "talent_id": "uuid-schwerter",
                "name": "Schwerter",
                "value": 12,
                "specializations": ["Langschwert", "Säbel"],
                "governing_attributes": ["MU", "GE", "KK"]
            }
        ],
        "physical": [
            {
                "talent_id": "uuid-klettern", 
                "name": "Klettern",
                "value": 8,
                "specializations": [],
                "governing_attributes": ["MU", "GE", "KK"]
            }
        ],
        "knowledge": [
            {
                "talent_id": "uuid-magiekunde",
                "name": "Magiekunde", 
                "value": 10,
                "specializations": ["Gildenmagie", "Elementarmagie"],
                "governing_attributes": ["KL", "KL", "IN"]
            }
        ],
        "languages": [
            {
                "talent_id": "uuid-garethi",
                "name": "Garethi",
                "value": 15,
                "specializations": ["Mittelreich-Dialekt"],
                "governing_attributes": ["KL", "IN", "CH"]
            }
        ]
    }
}
```

---

## 🔧 **Implementation Notes**

### **Database Considerations:**
- Use **UUID** primary keys for all models to avoid conflicts
- **JSON fields** for flexible data storage with proper validation
- **Generic Foreign Keys** for linking to different special ability/talent types
- **Proper indexing** on frequently queried fields (character.user, character.world)
- **Database constraints** to ensure data integrity

### **Validation Strategy:**
- **JSON Schema validation** for core_attributes based on RuleSet
- **Business logic validation** in model save() methods
- **Generation Point calculations** and limits enforcement
- **Requirement checking** for advantages/special abilities/talents

### **Performance Optimization:**
- **select_related()** for foreign key relationships
- **prefetch_related()** for many-to-many relationships
- **Database indexes** on commonly filtered fields
- **Caching** for reference data (races, cultures, professions)

### **Future Extensibility:**
- **RuleSet-agnostic** core structure
- **Easy addition** of new rule systems (D&D 5E, Pathfinder, etc.)
- **Modular special ability** system
- **Flexible JSON schemas** for different game systems

---

## 🎯 **Next Steps for Implementation**

1. **Create Character App**: `python manage.py startapp characters`
2. **Implement Core Models**: Character, RuleSet, CharacterRuleSetData
3. **Create DSA Reference Tables**: Race, Culture, Profession models
4. **Implement Advantage/Disadvantage System**
5. **Build Special Abilities Framework**
6. **Create Talent System with all categories**
7. **Add Character Linking Tables**
8. **Create Django Fixtures** for DSA 4.1 reference data
9. **Implement Validation Logic**
10. **Build Character Creation APIs**

---

*Architecture designed for: DSA 4.1 primary support with D&D 5E future compatibility*  
*Database Schema: Flexible JSON + Structured References*  
*Created: 26. Januar 2025* 

### **Character-Calculation-Engine**

```python
class CharacterCalculationEngine:
    """Engine für automatische Berechnungen von DSA 4.1 Charakterwerten"""
    
    @staticmethod
    def calculate_derived_values(core_attributes, race_modifiers=None, advantages=None):
        """Berechnet abgeleitete Werte basierend auf Grundeigenschaften"""
        attrs = core_attributes['attributes']
        
        # Basis-Berechnungen nach DSA 4.1 Regeln
        derived = {
            'LE': (attrs['KO'] * 2) + attrs['KK'] + 6,  # Lebensenergie
            'AU': (attrs['KO'] * 2) + attrs['GE'] + 6,  # Ausdauer
            'MR': (attrs['MU'] + attrs['KL'] + attrs['KO']) // 5,  # Magieresistenz
            'INI': (attrs['MU'] + attrs['GE']) // 2,     # Initiative
            'AT': (attrs['MU'] + attrs['GE'] + attrs['KK']) // 5,  # Attacke-Basis
            'PA': (attrs['IN'] + attrs['GE'] + attrs['KK']) // 5,  # Parade-Basis
            'FK': (attrs['IN'] + attrs['FF'] + attrs['KK']) // 5,  # Fernkampf-Basis
            'GS': 8  # Standard Geschwindigkeit
        }
        
        # Rassen-Modifikatoren anwenden
        if race_modifiers:
            for key, modifier in race_modifiers.items():
                if key in derived:
                    derived[key] += modifier
        
        # Vorteile/Nachteile anwenden
        if advantages:
            for advantage in advantages:
                if 'life_points_bonus' in advantage.get('effects', {}):
                    derived['LE'] += advantage['effects']['life_points_bonus']
        
        return derived
    
    @staticmethod
    def validate_character_rules(character_data):
        """Validiert DSA 4.1 Charaktererstellungsregeln"""
        errors = []
        attrs = character_data.get('core_attributes', {}).get('attributes', {})
        
        # Attributs-Maximum prüfen
        max_attr = character_data.get('generation_data', {}).get('attribute_maximum', 14)
        for attr, value in attrs.items():
            if value > max_attr:
                errors.append(f"{attr} ({value}) überschreitet Maximum ({max_attr})")
        
        # Generierungspunkte prüfen
        total_gp_used = sum(attrs.values()) - 64  # 8 Attribute * 8 Basis-Punkte
        max_gp = character_data.get('generation_data', {}).get('generation_points_max', 110)
        
        if total_gp_used > max_gp:
            errors.append(f"Generierungspunkte überschritten: {total_gp_used}/{max_gp}")
        
        return errors 