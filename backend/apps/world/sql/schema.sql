-- ==================================================
-- World Management System - Simplified Tables
-- ==================================================

-- ==================================================
-- 1. WORLD TABLE
-- ==================================================
CREATE TABLE wld_world_entity (
    id BIGSERIAL PRIMARY KEY,
    entity_id VARCHAR(20) UNIQUE NOT NULL CHECK (entity_id ~ '^WLD-[0-9]{12}$'),
    
    -- Basic Information
    name VARCHAR(200) NOT NULL,
    description TEXT CHECK (char_length(description) <= 5000),
    general_mood TEXT CHECK (char_length(general_mood) <= 1000),
    game_system VARCHAR(100) NOT NULL,
    current_date VARCHAR(100),
    
    -- Tags for categorization
    tags JSONB DEFAULT '[]',
    
    -- Quick Access Summary
    pill JSONB DEFAULT '{}',
    
    -- Core World Elements
    important_locations JSONB DEFAULT '[]',
    conventions JSONB DEFAULT '{}',
    time_system JSONB DEFAULT '{}',
    measurement_units JSONB DEFAULT '{}',
    
    -- Cultural & Religious Systems
    religions JSONB DEFAULT '[]',
    languages JSONB DEFAULT '[]',
    
    -- World Building Systems
    magic_system JSONB DEFAULT '{}',
    political_systems JSONB DEFAULT '[]',
    
    -- Environmental & Geographic
    climate_zones JSONB DEFAULT '[]',
    natural_phenomena JSONB DEFAULT '[]',
    trade_routes JSONB DEFAULT '[]',
    
    -- Narrative Elements
    history_timeline JSONB DEFAULT '[]',
    conflicts_tensions JSONB DEFAULT '[]',
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- ==================================================
-- 2. REGION TABLE
-- ==================================================
CREATE TABLE wld_region_entity (
    id BIGSERIAL PRIMARY KEY,
    entity_id VARCHAR(20) UNIQUE NOT NULL CHECK (entity_id ~ '^RGN-[0-9]{12}$'),
    world_id BIGINT NOT NULL REFERENCES wld_world_entity(id) ON DELETE CASCADE,
    
    -- Basic Information
    name VARCHAR(200) NOT NULL,
    description TEXT CHECK (char_length(description) <= 3000),
    general_mood TEXT CHECK (char_length(general_mood) <= 800),
    terrain_type VARCHAR(100),
    size_description VARCHAR(200),
    
    -- Tags for categorization
    tags JSONB DEFAULT '[]',
    
    -- Quick Access Summary
    pill JSONB DEFAULT '{}',
    
    -- Economic & Cultural
    currencies JSONB DEFAULT '[]',
    important_personalities JSONB DEFAULT '[]',
    religions JSONB DEFAULT '[]',
    government_type JSONB DEFAULT '{}',
    cultural_traits JSONB DEFAULT '[]',
    
    -- Infrastructure & Resources
    major_settlements JSONB DEFAULT '[]',
    natural_resources JSONB DEFAULT '[]',
    trade_specialties JSONB DEFAULT '[]',
    
    -- Environmental & Social
    threats_dangers JSONB DEFAULT '[]',
    climate_weather JSONB DEFAULT '{}',
    laws_customs JSONB DEFAULT '[]',
    festivals_events JSONB DEFAULT '[]',
    
    -- Security & Military
    military_forces JSONB DEFAULT '[]',
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    UNIQUE(world_id, name)
);

-- ==================================================
-- 3. LOCATION TABLE
-- ==================================================
CREATE TABLE wld_location_entity (
    id BIGSERIAL PRIMARY KEY,
    entity_id VARCHAR(20) UNIQUE NOT NULL CHECK (entity_id ~ '^LOC-[0-9]{12}$'),
    region_id BIGINT NOT NULL REFERENCES wld_region_entity(id) ON DELETE CASCADE,
    
    -- Basic Information
    name VARCHAR(200) NOT NULL,
    location_type VARCHAR(20) DEFAULT 'other' CHECK (
        location_type IN ('city', 'town', 'village', 'dungeon', 'ruins', 'temple', 
                         'castle', 'forest', 'mountain', 'cave', 'tavern', 'shop', 
                         'landmark', 'other')
    ),
    description TEXT CHECK (char_length(description) <= 2000),
    general_mood TEXT CHECK (char_length(general_mood) <= 600),
    size_scale VARCHAR(100),
    accessibility VARCHAR(200),
    
    -- Tags for categorization
    tags JSONB DEFAULT '[]',
    
    -- Quick Access Summary
    pill JSONB DEFAULT '{}',
    
    -- Characters & Services
    important_personalities JSONB DEFAULT '[]',
    services_available JSONB DEFAULT '[]',
    
    -- Physical Characteristics
    notable_features JSONB DEFAULT '[]',
    secrets_hidden JSONB DEFAULT '[]',
    
    -- Adventure Elements
    encounters_possible JSONB DEFAULT '[]',
    items_treasures JSONB DEFAULT '[]',
    defenses_security JSONB DEFAULT '[]',
    
    -- Demographics & Economy
    population_demographics JSONB DEFAULT '{}',
    economic_activity JSONB DEFAULT '[]',
    
    -- Travel & Information
    connections_travel JSONB DEFAULT '[]',
    rumors_information JSONB DEFAULT '[]',
    
    -- Dynamic Elements
    seasonal_changes JSONB DEFAULT '[]',
    current_events JSONB DEFAULT '[]',
    quest_opportunities JSONB DEFAULT '[]',
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    UNIQUE(region_id, name)
);

-- ==================================================
-- 4. NPC TABLE
-- ==================================================
CREATE TABLE wld_npc_entity (
    id BIGSERIAL PRIMARY KEY,
    entity_id VARCHAR(20) UNIQUE NOT NULL CHECK (entity_id ~ '^NPC-[0-9]{12}$'),
    
    -- Location Assignments (at least one must be set)
    world_id BIGINT REFERENCES wld_world_entity(id) ON DELETE CASCADE,
    region_id BIGINT REFERENCES wld_region_entity(id) ON DELETE CASCADE,
    location_id BIGINT REFERENCES wld_location_entity(id) ON DELETE CASCADE,
    
    -- Basic Information
    name VARCHAR(200) NOT NULL,
    species VARCHAR(100) DEFAULT 'Human',
    description TEXT,
    
    -- Tags for categorization
    tags JSONB DEFAULT '[]',
    
    -- Birth and Dating Information
    birth_date VARCHAR(100), -- World-specific date format
    birth_location VARCHAR(200),
    current_age INTEGER,
    death_date VARCHAR(100), -- Null if alive
    death_location VARCHAR(200),
    
    -- Physical Characteristics (JSON for flexibility)
    physical_traits JSONB DEFAULT '{}', -- height, hair, eyes, spirit_animal, etc.
    
    -- Social and Cultural Information
    social_standing JSONB DEFAULT '{}', -- status, family, titles, positions, organizations
    
    -- Personal Information
    personality JSONB DEFAULT '{}', -- traits, motivations, fears, goals
    
    -- Relationships and Acquaintances
    acquaintances JSONB DEFAULT '[]', -- partners, friends, enemies, etc.
    
    -- Family Structure (Genealogy)
    parents JSONB DEFAULT '[]', -- Array of parent NPC entity_ids with relationship details
    children JSONB DEFAULT '[]', -- Array of child NPC entity_ids with relationship details
    siblings JSONB DEFAULT '[]', -- Array of sibling NPC entity_ids
    extended_family JSONB DEFAULT '[]', -- Other family members
    
    -- Locations and Movement
    birth_place JSONB DEFAULT '{}',
    current_residence JSONB DEFAULT '{}',
    frequent_locations JSONB DEFAULT '[]',
    
    -- Game-Specific Information
    game_stats JSONB DEFAULT '{}', -- Stats, abilities, skills
    equipment JSONB DEFAULT '[]', -- Items, weapons, armor
    
    -- Quick Access Summary
    pill JSONB DEFAULT '{}',
    
    -- Status and Notes
    status VARCHAR(50) DEFAULT 'alive' CHECK (
        status IN ('alive', 'dead', 'missing', 'unknown', 'undead', 'transformed')
    ),
    notes TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Must belong to at least one location level
    CHECK (world_id IS NOT NULL OR region_id IS NOT NULL OR location_id IS NOT NULL)
);

-- ==================================================
-- 5. EVENT TABLE
-- ==================================================
CREATE TABLE wld_event_entity (
    id BIGSERIAL PRIMARY KEY,
    entity_id VARCHAR(20) UNIQUE NOT NULL CHECK (entity_id ~ '^EVT-[0-9]{12}$'),
    
    -- Location Assignments (at least one must be set)
    world_id BIGINT REFERENCES wld_world_entity(id) ON DELETE CASCADE,
    region_id BIGINT REFERENCES wld_region_entity(id) ON DELETE CASCADE,
    location_id BIGINT REFERENCES wld_location_entity(id) ON DELETE CASCADE,
    
    -- Basic Event Information
    name VARCHAR(200) NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- battle, festival, political, natural disaster, etc.
    event_date VARCHAR(100), -- World-specific date format
    duration VARCHAR(100), -- How long the event lasted
    
    -- Tags for categorization
    tags JSONB DEFAULT '[]',
    
    -- Event Details
    description TEXT,
    importance_level INTEGER CHECK (importance_level BETWEEN 1 AND 10) DEFAULT 5,
    
    -- Event Context
    causes JSONB DEFAULT '[]', -- What led to this event
    consequences JSONB DEFAULT '[]', -- Results and outcomes of the event
    
    -- Participants and Witnesses
    key_participants JSONB DEFAULT '[]', -- Primary figures involved
    witnesses JSONB DEFAULT '[]', -- People who witnessed the event
    affected_groups JSONB DEFAULT '[]', -- Groups/populations affected
    
    -- Event Scope and Impact
    scope VARCHAR(50) DEFAULT 'local' CHECK (
        scope IN ('local', 'regional', 'national', 'continental', 'global', 'planar')
    ),
    political_impact JSONB DEFAULT '{}',
    economic_impact JSONB DEFAULT '{}',
    social_impact JSONB DEFAULT '{}',
    
    -- Documentation and Sources
    sources JSONB DEFAULT '[]', -- How this information was recorded
    reliability INTEGER CHECK (reliability BETWEEN 1 AND 10) DEFAULT 5,
    
    -- Related Events
    predecessor_events JSONB DEFAULT '[]', -- Events that came before
    successor_events JSONB DEFAULT '[]', -- Events that followed
    
    -- Quick Access Summary
    pill JSONB DEFAULT '{}',
    
    -- Status
    status VARCHAR(50) DEFAULT 'historical' CHECK (
        status IN ('historical', 'ongoing', 'planned', 'mythical', 'cancelled')
    ),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Must belong to at least one location level
    CHECK (world_id IS NOT NULL OR region_id IS NOT NULL OR location_id IS NOT NULL)
);

-- ==================================================
-- 6. RELATIONSHIP TABLES
-- ==================================================

-- NPC Event Participation
CREATE TABLE wld_npc_event_participation (
    id BIGSERIAL PRIMARY KEY,
    npc_id BIGINT NOT NULL REFERENCES wld_npc_entity(id) ON DELETE CASCADE,
    event_id BIGINT NOT NULL REFERENCES wld_event_entity(id) ON DELETE CASCADE,
    participation_type VARCHAR(50) NOT NULL, -- organizer, participant, witness, victim, hero
    role_description TEXT,
    importance INTEGER CHECK (importance BETWEEN 1 AND 10) DEFAULT 5,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(npc_id, event_id)
);

-- NPC Relationships (beyond family)
CREATE TABLE wld_npc_relationships (
    id BIGSERIAL PRIMARY KEY,
    source_npc_id BIGINT NOT NULL REFERENCES wld_npc_entity(id) ON DELETE CASCADE,
    target_npc_id BIGINT NOT NULL REFERENCES wld_npc_entity(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL, -- friend, enemy, ally, rival, mentor, student
    strength INTEGER CHECK (strength BETWEEN 1 AND 10) DEFAULT 5,
    description TEXT,
    is_mutual BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(source_npc_id, target_npc_id, relationship_type)
);

-- Entity Connections (generic relationships between any entities)
CREATE TABLE wld_entity_connections (
    id BIGSERIAL PRIMARY KEY,
    source_entity_id VARCHAR(20) NOT NULL,
    source_entity_type VARCHAR(10) NOT NULL CHECK (
        source_entity_type IN ('world', 'region', 'location', 'npc', 'event')
    ),
    target_entity_id VARCHAR(20) NOT NULL,
    target_entity_type VARCHAR(10) NOT NULL CHECK (
        target_entity_type IN ('world', 'region', 'location', 'npc', 'event')
    ),
    connection_type VARCHAR(50) NOT NULL, -- origin, destination, related, influences, etc.
    strength INTEGER CHECK (strength BETWEEN 1 AND 10) DEFAULT 5,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(source_entity_id, target_entity_id, connection_type)
);

-- ==================================================
-- INDEXES
-- ==================================================

-- Primary entity indexes
CREATE INDEX idx_world_entity_id ON wld_world_entity(entity_id);
CREATE INDEX idx_region_entity_id ON wld_region_entity(entity_id);
CREATE INDEX idx_location_entity_id ON wld_location_entity(entity_id);
CREATE INDEX idx_npc_entity_id ON wld_npc_entity(entity_id);
CREATE INDEX idx_event_entity_id ON wld_event_entity(entity_id);

-- Relationship indexes
CREATE INDEX idx_region_world_id ON wld_region_entity(world_id);
CREATE INDEX idx_location_region_id ON wld_location_entity(region_id);
CREATE INDEX idx_npc_world_id ON wld_npc_entity(world_id);
CREATE INDEX idx_npc_region_id ON wld_npc_entity(region_id);
CREATE INDEX idx_npc_location_id ON wld_npc_entity(location_id);
CREATE INDEX idx_event_world_id ON wld_event_entity(world_id);
CREATE INDEX idx_event_region_id ON wld_event_entity(region_id);
CREATE INDEX idx_event_location_id ON wld_event_entity(location_id);

-- JSONB indexes for tags
CREATE INDEX idx_world_tags_gin ON wld_world_entity USING GIN(tags);
CREATE INDEX idx_region_tags_gin ON wld_region_entity USING GIN(tags);
CREATE INDEX idx_location_tags_gin ON wld_location_entity USING GIN(tags);
CREATE INDEX idx_npc_tags_gin ON wld_npc_entity USING GIN(tags);
CREATE INDEX idx_event_tags_gin ON wld_event_entity USING GIN(tags);

-- Relationship table indexes
CREATE INDEX idx_participation_npc ON wld_npc_event_participation(npc_id);
CREATE INDEX idx_participation_event ON wld_npc_event_participation(event_id);
CREATE INDEX idx_npc_rel_source ON wld_npc_relationships(source_npc_id);
CREATE INDEX idx_npc_rel_target ON wld_npc_relationships(target_npc_id);
CREATE INDEX idx_entity_conn_source ON wld_entity_connections(source_entity_id);
CREATE INDEX idx_entity_conn_target ON wld_entity_connections(target_entity_id);