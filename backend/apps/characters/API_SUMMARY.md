# Character Management API - Summary

## 🚀 API-Endpoints für Frontend-Integration

Das Character-Management-System bietet vollständige REST-API-Endpoints für die Frontend-Integration mit umfassenden CRUD-Operationen, Berechtigungssystem und DSA 4.1-Validierung.

---

## 📋 **Verfügbare Endpoints**

### **Character Management**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/characters/` | Liste aller Charaktere (eigene + Admin-Zugriff) | ✅ |
| `POST` | `/api/characters/` | Neuen Charakter erstellen | ✅ |
| `GET` | `/api/characters/{id}/` | Charakter-Details anzeigen | ✅ |
| `PATCH` | `/api/characters/{id}/` | Charakter aktualisieren | ✅ |
| `PUT` | `/api/characters/{id}/` | Charakter vollständig ersetzen | ✅ |
| `DELETE` | `/api/characters/{id}/` | Charakter löschen | ✅ |

### **Reference Data Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/characters/rulesets/` | Verfügbare Regelsysteme |
| `GET` | `/api/characters/races/` | DSA 4.1 Rassen |
| `GET` | `/api/characters/cultures/` | DSA 4.1 Kulturen |
| `GET` | `/api/characters/professions/` | DSA 4.1 Professionen |
| `GET` | `/api/characters/advantages/` | DSA 4.1 Vorteile |
| `GET` | `/api/characters/disadvantages/` | DSA 4.1 Nachteile |

---

## 🔐 **Berechtigungssystem**

### **User Permissions**
- **Eigene Charaktere**: Vollzugriff (CRUD)
- **Fremde Charaktere**: Kein Zugriff

### **Admin Permissions**
- **Alle Charaktere in verwalteten Welten**: Vollzugriff (CRUD)
- **Automatische Berechtigung**: Über World-Admin-Rechte

### **Authentication**
- **JWT-Token erforderlich** für alle Endpoints
- **Authorization Header**: `Bearer <jwt_token>`

---

## 📊 **API Request/Response Examples**

### **1. Character erstellen**

```http
POST /api/characters/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "name": "Thorek Eisenbart",
    "world": "550e8400-e29b-41d4-a716-446655440000",
    "rule_set": "550e8400-e29b-41d4-a716-446655440001",
    "status": "draft",
    "core_attributes": {
        "MU": 14,
        "KL": 13,
        "IN": 12,
        "CH": 11,
        "FF": 10,
        "GE": 9,
        "KO": 8,
        "KK": 8
    }
}
```

**Response (201 Created):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "Thorek Eisenbart",
    "status": "draft",
    "world_name": "Aventurien",
    "rule_set_name": "DSA 4.1",
    "created_at": "2025-01-26T10:30:00Z",
    "updated_at": "2025-01-26T10:30:00Z"
}
```

### **2. Character-Liste abrufen**

```http
GET /api/characters/
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/characters/?page=2",
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "name": "Thorek Eisenbart",
            "status": "active",
            "world_name": "Aventurien",
            "rule_set_name": "DSA 4.1",
            "created_at": "2025-01-26T10:30:00Z"
        }
    ]
}
```

### **3. Character-Details abrufen**

```http
GET /api/characters/550e8400-e29b-41d4-a716-446655440002/
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "Thorek Eisenbart",
    "status": "active",
    "world_name": "Aventurien",
    "rule_set_name": "DSA 4.1",
    "core_attributes": {
        "MU": 14,
        "KL": 13,
        "IN": 12,
        "CH": 11,
        "FF": 10,
        "GE": 9,
        "KO": 8,
        "KK": 8
    },
    "created_at": "2025-01-26T10:30:00Z",
    "updated_at": "2025-01-26T10:30:00Z"
}
```

### **4. Character aktualisieren**

```http
PATCH /api/characters/550e8400-e29b-41d4-a716-446655440002/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "name": "Thorek der Mutige",
    "status": "active"
}
```

**Response (200 OK):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "Thorek der Mutige",
    "status": "active",
    "world_name": "Aventurien",
    "rule_set_name": "DSA 4.1",
    "core_attributes": {
        "MU": 14,
        "KL": 13,
        "IN": 12,
        "CH": 11,
        "FF": 10,
        "GE": 9,
        "KO": 8,
        "KK": 8
    },
    "created_at": "2025-01-26T10:30:00Z",
    "updated_at": "2025-01-26T11:15:00Z"
}
```

---

## 🔍 **Query Parameters**

### **Filtering & Search**

| Parameter | Description | Example |
|-----------|-------------|---------|
| `search` | Suche nach Charaktername | `?search=Thorek` |
| `status` | Filter nach Status | `?status=active` |
| `world` | Filter nach Welt-ID | `?world=550e8400-e29b-41d4-a716-446655440000` |
| `rule_set` | Filter nach Regelsystem | `?rule_set=550e8400-e29b-41d4-a716-446655440001` |

### **Pagination**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `page` | Seitennummer | 1 |
| `page_size` | Anzahl Ergebnisse pro Seite | 20 |

**Example:**
```http
GET /api/characters/?search=Thorek&status=active&page=1&page_size=10
```

---

## ⚠️ **Error Responses**

### **400 Bad Request - Validierungsfehler**
```json
{
    "errors": [
        "MU (7) ist unter Minimum (8)",
        "Name darf nicht leer sein"
    ]
}
```

### **401 Unauthorized - Fehlende Authentifizierung**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### **403 Forbidden - Fehlende Berechtigung**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### **404 Not Found - Charakter nicht gefunden**
```json
{
    "detail": "Not found."
}
```

---

## 🎯 **DSA 4.1 Validierung**

### **Core Attributes Validation**
- **Minimum-Wert**: 8 für alle Attribute
- **Maximum-Wert**: 14 (Standard, konfigurierbar)
- **Required Attributes**: MU, KL, IN, CH, FF, GE, KO, KK

### **Character Data Validation**
- **Name**: Pflichtfeld, nicht leer
- **World**: Muss existieren und User muss Zugriff haben
- **RuleSet**: Muss aktiv und verfügbar sein
- **Status**: Gültige Werte: `draft`, `active`, `archived`

### **Generierungspunkte-System**
- **Automatische Berechnung** der GP-Kosten
- **Validierung** gegen GP-Limits
- **Error-Messages** bei Überschreitung

---

## 🛠️ **Frontend Integration Guidelines**

### **1. Authentication Setup**
```javascript
// JWT Token in Axios Headers
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

### **2. Character CRUD Operations**
```javascript
// Create Character
const createCharacter = async (characterData) => {
    const response = await axios.post('/api/characters/', characterData);
    return response.data;
};

// Get Characters List
const getCharacters = async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await axios.get(`/api/characters/?${params}`);
    return response.data;
};

// Get Character Details
const getCharacter = async (characterId) => {
    const response = await axios.get(`/api/characters/${characterId}/`);
    return response.data;
};

// Update Character
const updateCharacter = async (characterId, updateData) => {
    const response = await axios.patch(`/api/characters/${characterId}/`, updateData);
    return response.data;
};

// Delete Character
const deleteCharacter = async (characterId) => {
    await axios.delete(`/api/characters/${characterId}/`);
};
```

### **3. Error Handling**
```javascript
try {
    const character = await createCharacter(characterData);
} catch (error) {
    if (error.response?.status === 400) {
        // Handle validation errors
        const errors = error.response.data.errors;
        console.error('Validation errors:', errors);
    } else if (error.response?.status === 403) {
        // Handle permission errors
        console.error('Permission denied');
    }
}
```

### **4. Real-time Updates**
- **WebSocket-Integration** geplant für Live-Updates
- **Polling-Alternative** für Character-Liste-Updates
- **Optimistic Updates** für bessere UX

---

## 📈 **Performance & Caching**

### **Database Optimizations**
- **Queryset-Optimierung** mit select_related/prefetch_related
- **Database-Indexes** auf häufig gefilterte Felder
- **Pagination** für große Datensätze

### **API Performance**
- **Response-Caching** für Reference-Data
- **Efficient Serialization** mit optimierten Serializers
- **Bulk-Operations** für Multiple-Character-Updates

### **Frontend Caching**
- **Character-Liste** cachen mit TTL
- **Reference-Data** langzeit-cachen
- **Character-Details** mit Invalidation-Strategy

---

## 🧪 **Testing Coverage**

### **API Endpoint Tests** ✅
- CRUD-Operations für alle Endpoints
- Permission-Tests für User/Admin-Zugriff
- Validation-Tests für DSA 4.1-Regeln

### **Service Layer Tests** ✅
- Character-Creation-Logic
- Character-Calculation-Engine
- Permission-Integration

### **Model Tests** ✅
- Database-Constraints
- Model-Validation
- Relationship-Integrity

**Total Test Coverage: 148 Tests - Alle bestehen ✅**

---

*API Documentation - Version 1.0*  
*Erstellt: 26. Januar 2025*  
*Status: Production Ready* 🚀 