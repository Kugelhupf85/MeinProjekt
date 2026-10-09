# Arcanovi Documentation

Willkommen in der Dokumentationssammlung für das Arcanovi Projekt - einem umfassenden Pen & Paper Management-System.

## 📚 Verfügbare Dokumentationen

### 🗄️ [Database Structure](database-structure.md)
Detaillierte Übersicht über die bestehende Django-Datenbank-Struktur:
- User-Management-System (ArcanoviUser, PlayerProfile, DungeonMasterProfile)
- Dungeon Master System (DungeonMaster, UserKeys, Party)
- Adventure-Management (Adventure)
- World-Building-System (World, Region, Location)
- Beziehungen und Constraints zwischen den Models

### 🚀 [Refactoring Roadmap](refactoring-roadmap.md)
Detaillierte Todo-Liste für die geplante System-Refaktorierung:
- User-Management Refactoring mit Rollen-System
- Erweiterte Berechtigungen und Permission-System
- World-zentrierte Architektur
- Flexibles Character-Management-System (DSA 4.1 & D&D)
- Migration und Integration

### 🎲 [Character System Architecture](character-system-architecture.md)
Umfassende Architektur-Dokumentation für das Character-Management-System:
- Multi-RuleSet-Design für verschiedene Pen & Paper Systeme
- Detaillierte Database-Schemas für DSA 4.1 (Das Schwarze Auge)
- Flexible JSON-basierte Datenstrukturen
- Referenz-Tabellen für Races, Cultures, Professions
- Advantages/Disadvantages und Special Abilities System
- Vollständiges Talent-System mit allen Kategorien

---

## 🏗️ Geplante Architektur-Übersicht

**Aktuelle Struktur**:
```
📁 backend/apps/
├── 👤 dungeon_master/    # User & DM Management (Legacy)
├── 🏰 adventure/         # Kampagnen-Management
└── 🌍 world/             # Weltenbau-System
```

**Geplante Erweiterung**:
```
📁 backend/apps/
├── 👤 core_user/         # Standard SaaS User-Management
├── 🔐 permissions/       # Erweiterte Berechtigungen
├── 🎲 characters/        # Character-Management-System
├── 🎭 dungeon_master/    # DM-spezifische Features
├── 🏰 adventure/         # Kampagnen-Management
└── 🌍 world/             # Weltenbau-System (erweitert)
```

---

## 🎯 Entwicklungsreihenfolge

1. **Phase 1**: User-Management Refactoring (2-3 Wochen)
2. **Phase 2**: Permission-System (1-2 Wochen) 
3. **Phase 3**: World-zentrierte Architektur (1-2 Wochen)
4. **Phase 4**: Character-Management-System (3-4 Wochen)
5. **Phase 5**: Migration & Integration (1-2 Wochen)

---

*Dokumentation erstellt: 26. Januar 2025*  
*Nächste Aktualisierung: Nach Abschluss jeder Entwicklungsphase* 