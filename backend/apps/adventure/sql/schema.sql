-- ==================================================
-- Adventure System - Updated Database Schema
-- ==================================================

-- ==================================================
-- 1. ADVENTURE TABLE (UPDATED)
-- ==================================================
CREATE TABLE IF NOT EXISTS adv_adventure (
    id BIGSERIAL PRIMARY KEY,
    entity_id VARCHAR(20) UNIQUE NOT NULL,
    dungeon_master_id BIGINT NOT NULL REFERENCES dm_user_dungeonmaster(id) ON DELETE CASCADE,
    world_id BIGINT NOT NULL REFERENCES wld_world_entity(id) ON DELETE RESTRICT,
    
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    
    -- Adventure Content
    adventure_settings JSONB DEFAULT '{}',
    world_building JSONB DEFAULT '{}',
    session_notes JSONB DEFAULT '[]',
    character_sheets JSONB DEFAULT '[]',
    
    -- Status and Metadata
    status VARCHAR(20) DEFAULT 'planning',
    is_public BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE NULL,
    completed_at TIMESTAMP WITH TIME ZONE NULL,
    
    -- Session Tracking
    current_session INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0
);

-- ==================================================
-- 2. ADVENTURE-REGION ASSOCIATION TABLE
-- ==================================================
CREATE TABLE IF NOT EXISTS adv_adventure_regions (
    id BIGSERIAL PRIMARY KEY,
    adventure_id BIGINT NOT NULL REFERENCES adv_adventure(id) ON DELETE CASCADE,
    region_id BIGINT NOT NULL REFERENCES wld_region_entity(id) ON DELETE CASCADE,
    
    -- Optional metadata about region usage
    importance_level INTEGER CHECK (importance_level BETWEEN 1 AND 10) DEFAULT 5,
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique combination
    UNIQUE(adventure_id, region_id)
);

-- ==================================================
-- 3. ADVENTURE-EVENT ASSOCIATION TABLE
-- ==================================================
CREATE TABLE IF NOT EXISTS adv_adventure_events (
    id BIGSERIAL PRIMARY KEY,
    adventure_id BIGINT NOT NULL REFERENCES adv_adventure(id) ON DELETE CASCADE,
    event_id BIGINT NOT NULL REFERENCES wld_event_entity(id) ON DELETE CASCADE,
    
    -- Event relevance to adventure
    relevance_level INTEGER CHECK (relevance_level BETWEEN 1 AND 10) DEFAULT 5,
    usage_type VARCHAR(50) DEFAULT 'background' CHECK (
        usage_type IN ('background', 'plot_point', 'reference', 'inspiration', 'conflict')
    ),
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique combination
    UNIQUE(adventure_id, event_id)
);

-- ==================================================
-- 4. ACT TABLE
-- ==================================================
CREATE TABLE IF NOT EXISTS adv_act (
    id BIGSERIAL PRIMARY KEY,
    entity_id VARCHAR(20) UNIQUE NOT NULL,
    adventure_id BIGINT NOT NULL REFERENCES adv_adventure(id) ON DELETE CASCADE,
    
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    
    -- Act Structure
    act_number INTEGER NOT NULL,
    
    -- Act Content
    objectives JSONB DEFAULT '[]',
    key_events JSONB DEFAULT '[]',
    notes TEXT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'planned',
    is_completed BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE NULL,
    completed_at TIMESTAMP WITH TIME ZONE NULL,
    
    -- Ensure unique act numbers per adventure
    UNIQUE(adventure_id, act_number)
);

-- ==================================================
-- 5. SCENE TABLE
-- ==================================================
CREATE TABLE IF NOT EXISTS adv_scene (
    id BIGSERIAL PRIMARY KEY,
    entity_id VARCHAR(20) UNIQUE NOT NULL,
    act_id BIGINT NOT NULL REFERENCES adv_act(id) ON DELETE CASCADE,
    
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    
    -- Scene Structure
    scene_number INTEGER NOT NULL,
    
    -- Scene Content
    scene_type VARCHAR(50) DEFAULT 'exploration' CHECK (
        scene_type IN ('exploration', 'combat', 'social', 'puzzle', 'investigation', 
                      'travel', 'rest', 'dramatic', 'other')
    ),
    location_notes TEXT,
    objectives JSONB DEFAULT '[]',
    npcs_involved JSONB DEFAULT '[]',
    items_rewards JSONB DEFAULT '[]',
    
    -- Scene Mechanics
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 10) DEFAULT 5,
    estimated_duration INTEGER, -- in minutes
    
    -- Story Elements
    mood_atmosphere TEXT,
    key_moments JSONB DEFAULT '[]',
    player_choices JSONB DEFAULT '[]',
    
    -- DM Notes
    dm_notes TEXT,
    preparation_notes TEXT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'planned',
    is_completed BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE NULL,
    completed_at TIMESTAMP WITH TIME ZONE NULL,
    
    -- Session Tracking
    session_played INTEGER NULL, -- which session this scene was played in
    
    -- Ensure unique scene numbers per act
    UNIQUE(act_id, scene_number)
);

-- ==================================================
-- CONSTRAINTS
-- ==================================================

-- Adventure constraints
ALTER TABLE adv_adventure ADD CONSTRAINT chk_adv_entity_id_format 
    CHECK (entity_id ~ '^ADV-[0-9]{12}$');

ALTER TABLE adv_adventure ADD CONSTRAINT chk_adv_status_valid 
    CHECK (status IN ('planning', 'active', 'paused', 'completed', 'archived'));

ALTER TABLE adv_adventure ADD CONSTRAINT chk_adv_session_count_positive 
    CHECK (current_session >= 0 AND total_sessions >= 0);

-- Act constraints
ALTER TABLE adv_act ADD CONSTRAINT chk_act_entity_id_format 
    CHECK (entity_id ~ '^ACT-[0-9]{12}$');

ALTER TABLE adv_act ADD CONSTRAINT chk_act_number_positive 
    CHECK (act_number > 0);

ALTER TABLE adv_act ADD CONSTRAINT chk_act_status_valid 
    CHECK (status IN ('planned', 'active', 'completed', 'skipped'));

-- Scene constraints
ALTER TABLE adv_scene ADD CONSTRAINT chk_scene_entity_id_format 
    CHECK (entity_id ~ '^SCN-[0-9]{12}$');

ALTER TABLE adv_scene ADD CONSTRAINT chk_scene_number_positive 
    CHECK (scene_number > 0);

ALTER TABLE adv_scene ADD CONSTRAINT chk_scene_status_valid 
    CHECK (status IN ('planned', 'active', 'completed', 'skipped'));

ALTER TABLE adv_scene ADD CONSTRAINT chk_scene_duration_positive 
    CHECK (estimated_duration IS NULL OR estimated_duration > 0);

-- ==================================================
-- INDEXES FOR PERFORMANCE
-- ==================================================

-- Adventure indexes
CREATE INDEX IF NOT EXISTS idx_adv_adventure_entity_id ON adv_adventure(entity_id);
CREATE INDEX IF NOT EXISTS idx_adv_adventure_dungeon_master_id ON adv_adventure(dungeon_master_id);
CREATE INDEX IF NOT EXISTS idx_adv_adventure_world_id ON adv_adventure(world_id);
CREATE INDEX IF NOT EXISTS idx_adv_adventure_status ON adv_adventure(status);
CREATE INDEX IF NOT EXISTS idx_adv_adventure_is_public ON adv_adventure(is_public);
CREATE INDEX IF NOT EXISTS idx_adv_adventure_created_at ON adv_adventure(created_at);
CREATE INDEX IF NOT EXISTS idx_adv_adventure_updated_at ON adv_adventure(updated_at);

-- Adventure-Region association indexes
CREATE INDEX IF NOT EXISTS idx_adv_adventure_regions_adventure_id ON adv_adventure_regions(adventure_id);
CREATE INDEX IF NOT EXISTS idx_adv_adventure_regions_region_id ON adv_adventure_regions(region_id);

-- Adventure-Event association indexes
CREATE INDEX IF NOT EXISTS idx_adv_adventure_events_adventure_id ON adv_adventure_events(adventure_id);
CREATE INDEX IF NOT EXISTS idx_adv_adventure_events_event_id ON adv_adventure_events(event_id);
CREATE INDEX IF NOT EXISTS idx_adv_adventure_events_usage_type ON adv_adventure_events(usage_type);

-- Act indexes
CREATE INDEX IF NOT EXISTS idx_adv_act_entity_id ON adv_act(entity_id);
CREATE INDEX IF NOT EXISTS idx_adv_act_adventure_id ON adv_act(adventure_id);
CREATE INDEX IF NOT EXISTS idx_adv_act_number ON adv_act(act_number);
CREATE INDEX IF NOT EXISTS idx_adv_act_status ON adv_act(status);
CREATE INDEX IF NOT EXISTS idx_adv_act_adventure_number ON adv_act(adventure_id, act_number);

-- Scene indexes
CREATE INDEX IF NOT EXISTS idx_adv_scene_entity_id ON adv_scene(entity_id);
CREATE INDEX IF NOT EXISTS idx_adv_scene_act_id ON adv_scene(act_id);
CREATE INDEX IF NOT EXISTS idx_adv_scene_number ON adv_scene(scene_number);
CREATE INDEX IF NOT EXISTS idx_adv_scene_type ON adv_scene(scene_type);
CREATE INDEX IF NOT EXISTS idx_adv_scene_status ON adv_scene(status);
CREATE INDEX IF NOT EXISTS idx_adv_scene_session ON adv_scene(session_played);
CREATE INDEX IF NOT EXISTS idx_adv_scene_act_number ON adv_scene(act_id, scene_number);

-- JSONB indexes for efficient JSON queries
CREATE INDEX IF NOT EXISTS idx_adv_adventure_adventure_settings_gin ON adv_adventure USING GIN(adventure_settings);
CREATE INDEX IF NOT EXISTS idx_adv_adventure_world_building_gin ON adv_adventure USING GIN(world_building);
CREATE INDEX IF NOT EXISTS idx_adv_adventure_session_notes_gin ON adv_adventure USING GIN(session_notes);
CREATE INDEX IF NOT EXISTS idx_adv_adventure_character_sheets_gin ON adv_adventure USING GIN(character_sheets);

CREATE INDEX IF NOT EXISTS idx_adv_act_objectives_gin ON adv_act USING GIN(objectives);
CREATE INDEX IF NOT EXISTS idx_adv_act_key_events_gin ON adv_act USING GIN(key_events);

CREATE INDEX IF NOT EXISTS idx_adv_scene_objectives_gin ON adv_scene USING GIN(objectives);
CREATE INDEX IF NOT EXISTS idx_adv_scene_npcs_involved_gin ON adv_scene USING GIN(npcs_involved);
CREATE INDEX IF NOT EXISTS idx_adv_scene_items_rewards_gin ON adv_scene USING GIN(items_rewards);
CREATE INDEX IF NOT EXISTS idx_adv_scene_key_moments_gin ON adv_scene USING GIN(key_moments);
CREATE INDEX IF NOT EXISTS idx_adv_scene_player_choices_gin ON adv_scene USING GIN(player_choices);

-- ==================================================
-- 6. TRIGGER SYSTEM
-- ==================================================

-- Main Trigger Table
CREATE TABLE IF NOT EXISTS adv_trigger (
    id BIGSERIAL PRIMARY KEY,
    entity_id VARCHAR(20) UNIQUE NOT NULL,
    adventure_id BIGINT NOT NULL REFERENCES adv_adventure(id) ON DELETE CASCADE,
    
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    
    -- Trigger Properties
    trigger_type VARCHAR(50) DEFAULT 'general' CHECK (
        trigger_type IN ('clue', 'event', 'encounter', 'discovery', 'choice', 
                        'condition', 'mystery', 'revelation', 'general')
    ),
    
    -- Status
    is_resolved BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    can_be_moved BOOLEAN DEFAULT TRUE, -- can DM move this trigger
    
    -- Trigger Mechanics
    auto_resolve BOOLEAN DEFAULT FALSE, -- resolves automatically when triggered
    resolution_condition TEXT, -- what needs to happen to resolve
    
    -- Content
    trigger_content JSONB DEFAULT '{}', -- flexible content (clues, rewards, etc.)
    dm_notes TEXT,
    player_notes TEXT, -- notes visible to players when triggered
    
    -- Priority and Difficulty
    priority INTEGER CHECK (priority BETWEEN 1 AND 10) DEFAULT 5,
    difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 10) DEFAULT 5,
    
    -- Session Tracking
    session_created INTEGER,
    session_triggered INTEGER NULL,
    session_resolved INTEGER NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    triggered_at TIMESTAMP WITH TIME ZONE NULL,
    resolved_at TIMESTAMP WITH TIME ZONE NULL
);

-- Trigger Attachment Table (where triggers can be found/activated)
CREATE TABLE IF NOT EXISTS adv_trigger_attachment (
    id BIGSERIAL PRIMARY KEY,
    trigger_id BIGINT NOT NULL REFERENCES adv_trigger(id) ON DELETE CASCADE,
    
    -- Attachment Target (one of these must be set)
    world_id BIGINT REFERENCES wld_world_entity(id) ON DELETE CASCADE,
    region_id BIGINT REFERENCES wld_region_entity(id) ON DELETE CASCADE,
    location_id BIGINT REFERENCES wld_location_entity(id) ON DELETE CASCADE,
    npc_id BIGINT REFERENCES wld_npc_entity(id) ON DELETE CASCADE,
    event_id BIGINT REFERENCES wld_event_entity(id) ON DELETE CASCADE,
    
    -- Scene/Act specific attachments (optional)
    act_id BIGINT REFERENCES adv_act(id) ON DELETE CASCADE,
    scene_id BIGINT REFERENCES adv_scene(id) ON DELETE CASCADE,
    
    -- Attachment Properties
    attachment_type VARCHAR(50) DEFAULT 'location' CHECK (
        attachment_type IN ('location', 'interaction', 'discovery', 'automatic', 
                          'conditional', 'time_based', 'story_based')
    ),
    
    -- Activation Conditions
    activation_condition TEXT, -- what needs to happen to trigger
    requires_investigation BOOLEAN DEFAULT FALSE,
    skill_check_required VARCHAR(100), -- e.g., "Perception DC 15"
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    times_triggered INTEGER DEFAULT 0,
    max_triggers INTEGER DEFAULT 1, -- how many times can this be triggered
    
    -- Metadata
    attachment_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure at least one attachment target is set
    CHECK (
        (world_id IS NOT NULL)::int + 
        (region_id IS NOT NULL)::int + 
        (location_id IS NOT NULL)::int + 
        (npc_id IS NOT NULL)::int + 
        (event_id IS NOT NULL)::int + 
        (act_id IS NOT NULL)::int + 
        (scene_id IS NOT NULL)::int >= 1
    )
);

-- Trigger Dependencies (triggers that depend on other triggers)
CREATE TABLE IF NOT EXISTS adv_trigger_dependencies (
    id BIGSERIAL PRIMARY KEY,
    trigger_id BIGINT NOT NULL REFERENCES adv_trigger(id) ON DELETE CASCADE,
    depends_on_trigger_id BIGINT NOT NULL REFERENCES adv_trigger(id) ON DELETE CASCADE,
    
    -- Dependency Type
    dependency_type VARCHAR(50) DEFAULT 'requires_resolved' CHECK (
        dependency_type IN ('requires_resolved', 'requires_triggered', 'blocks_until_resolved',
                          'activates_when_resolved', 'mutually_exclusive')
    ),
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Prevent self-reference
    CHECK (trigger_id != depends_on_trigger_id),
    
    -- Unique dependency relationships
    UNIQUE(trigger_id, depends_on_trigger_id, dependency_type)
);

-- ==================================================
-- TRIGGER SYSTEM CONSTRAINTS
-- ==================================================

-- Trigger constraints
ALTER TABLE adv_trigger ADD CONSTRAINT chk_trigger_entity_id_format 
    CHECK (entity_id ~ '^TRG-[0-9]{12}

-- ==================================================
-- COMMENTS FOR DOCUMENTATION
-- ==================================================

-- Adventure table comments
COMMENT ON TABLE adv_adventure IS 'Adventures and campaigns managed by dungeon masters';
COMMENT ON COLUMN adv_adventure.entity_id IS 'Unique entity identifier with format: ADV-{12_digit_id}';
COMMENT ON COLUMN adv_adventure.dungeon_master_id IS 'Reference to dungeon master who owns this adventure';
COMMENT ON COLUMN adv_adventure.world_id IS 'Reference to the world where this adventure takes place';
COMMENT ON COLUMN adv_adventure.name IS 'Name of the adventure/campaign';
COMMENT ON COLUMN adv_adventure.description IS 'Detailed description of the adventure';
COMMENT ON COLUMN adv_adventure.adventure_settings IS 'JSON configuration for adventure-specific settings';
COMMENT ON COLUMN adv_adventure.world_building IS 'JSON data for world building elements specific to this adventure';
COMMENT ON COLUMN adv_adventure.session_notes IS 'Array of session notes and summaries';
COMMENT ON COLUMN adv_adventure.character_sheets IS 'Array of player character information';
COMMENT ON COLUMN adv_adventure.status IS 'Current status: planning, active, paused, completed, archived';
COMMENT ON COLUMN adv_adventure.is_public IS 'Whether this adventure is publicly visible';

-- Act table comments
COMMENT ON TABLE adv_act IS 'Acts within adventures - major story divisions';
COMMENT ON COLUMN adv_act.entity_id IS 'Unique entity identifier with format: ACT-{12_digit_id}';
COMMENT ON COLUMN adv_act.adventure_id IS 'Reference to the parent adventure';
COMMENT ON COLUMN adv_act.act_number IS 'Sequential number of this act within the adventure (1, 2, 3...)';
COMMENT ON COLUMN adv_act.objectives IS 'JSON array of objectives for this act';
COMMENT ON COLUMN adv_act.key_events IS 'JSON array of important events in this act';

-- Scene table comments
COMMENT ON TABLE adv_scene IS 'Scenes within acts - individual gameplay segments';
COMMENT ON COLUMN adv_scene.entity_id IS 'Unique entity identifier with format: SCN-{12_digit_id}';
COMMENT ON COLUMN adv_scene.act_id IS 'Reference to the parent act';
COMMENT ON COLUMN adv_scene.scene_number IS 'Sequential number of this scene within the act (1, 2, 3...)';
COMMENT ON COLUMN adv_scene.scene_type IS 'Type of scene: exploration, combat, social, puzzle, etc.';
COMMENT ON COLUMN adv_scene.npcs_involved IS 'JSON array of NPCs that appear in this scene';
COMMENT ON COLUMN adv_scene.items_rewards IS 'JSON array of items, treasures, or rewards in this scene';
COMMENT ON COLUMN adv_scene.estimated_duration IS 'Estimated duration in minutes';
COMMENT ON COLUMN adv_scene.session_played IS 'Which session number this scene was actually played in';

-- Trigger system comments
COMMENT ON TABLE adv_trigger IS 'Simplified narrative trigger system for AI-driven adventure management';
COMMENT ON COLUMN adv_trigger.entity_id IS 'Unique entity identifier with format: TRG-{12_digit_id}';
COMMENT ON COLUMN adv_trigger.adventure_id IS 'Reference to the parent adventure';
COMMENT ON COLUMN adv_trigger.description IS 'Detailed description for AI to determine when trigger should activate';
COMMENT ON COLUMN adv_trigger.trigger_type IS 'Type of trigger: clue, event, encounter, discovery, etc.';
COMMENT ON COLUMN adv_trigger.is_triggered IS 'Whether this trigger has been activated';
COMMENT ON COLUMN adv_trigger.deadline_scene_id IS 'Optional deadline - trigger must be activated by this scene';
COMMENT ON COLUMN adv_trigger.missed_consequence IS 'What happens if trigger is not activated by deadline';

COMMENT ON TABLE adv_trigger_attachment IS 'Defines where triggers can be found or activated';
COMMENT ON COLUMN adv_trigger_attachment.context_notes IS 'Additional context to help AI determine trigger activation';);

-- ==================================================
-- TRIGGER SYSTEM INDEXES
-- ==================================================

-- Trigger indexes
CREATE INDEX IF NOT EXISTS idx_adv_trigger_entity_id ON adv_trigger(entity_id);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_adventure_id ON adv_trigger(adventure_id);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_type ON adv_trigger(trigger_type);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_resolved ON adv_trigger(is_resolved);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_active ON adv_trigger(is_active);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_priority ON adv_trigger(priority);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_session_created ON adv_trigger(session_created);

-- Trigger attachment indexes
CREATE INDEX IF NOT EXISTS idx_adv_trigger_attachment_trigger_id ON adv_trigger_attachment(trigger_id);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_attachment_world_id ON adv_trigger_attachment(world_id);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_attachment_region_id ON adv_trigger_attachment(region_id);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_attachment_location_id ON adv_trigger_attachment(location_id);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_attachment_npc_id ON adv_trigger_attachment(npc_id);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_attachment_event_id ON adv_trigger_attachment(event_id);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_attachment_act_id ON adv_trigger_attachment(act_id);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_attachment_scene_id ON adv_trigger_attachment(scene_id);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_attachment_type ON adv_trigger_attachment(attachment_type);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_attachment_active ON adv_trigger_attachment(is_active);

-- Trigger dependency indexes
CREATE INDEX IF NOT EXISTS idx_adv_trigger_dependencies_trigger_id ON adv_trigger_dependencies(trigger_id);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_dependencies_depends_on ON adv_trigger_dependencies(depends_on_trigger_id);
CREATE INDEX IF NOT EXISTS idx_adv_trigger_dependencies_type ON adv_trigger_dependencies(dependency_type);

-- JSONB indexes for trigger content
CREATE INDEX IF NOT EXISTS idx_adv_trigger_content_gin ON adv_trigger USING GIN(trigger_content);

-- ==================================================
-- COMMENTS FOR DOCUMENTATION
-- ==================================================

-- Adventure table comments
COMMENT ON TABLE adv_adventure IS 'Adventures and campaigns managed by dungeon masters';
COMMENT ON COLUMN adv_adventure.entity_id IS 'Unique entity identifier with format: ADV-{12_digit_id}';
COMMENT ON COLUMN adv_adventure.dungeon_master_id IS 'Reference to dungeon master who owns this adventure';
COMMENT ON COLUMN adv_adventure.world_id IS 'Reference to the world where this adventure takes place';
COMMENT ON COLUMN adv_adventure.name IS 'Name of the adventure/campaign';
COMMENT ON COLUMN adv_adventure.description IS 'Detailed description of the adventure';
COMMENT ON COLUMN adv_adventure.adventure_settings IS 'JSON configuration for adventure-specific settings';
COMMENT ON COLUMN adv_adventure.world_building IS 'JSON data for world building elements specific to this adventure';
COMMENT ON COLUMN adv_adventure.session_notes IS 'Array of session notes and summaries';
COMMENT ON COLUMN adv_adventure.character_sheets IS 'Array of player character information';
COMMENT ON COLUMN adv_adventure.status IS 'Current status: planning, active, paused, completed, archived';
COMMENT ON COLUMN adv_adventure.is_public IS 'Whether this adventure is publicly visible';

-- Act table comments
COMMENT ON TABLE adv_act IS 'Acts within adventures - major story divisions';
COMMENT ON COLUMN adv_act.entity_id IS 'Unique entity identifier with format: ACT-{12_digit_id}';
COMMENT ON COLUMN adv_act.adventure_id IS 'Reference to the parent adventure';
COMMENT ON COLUMN adv_act.act_number IS 'Sequential number of this act within the adventure (1, 2, 3...)';
COMMENT ON COLUMN adv_act.objectives IS 'JSON array of objectives for this act';
COMMENT ON COLUMN adv_act.key_events IS 'JSON array of important events in this act';

-- Scene table comments
COMMENT ON TABLE adv_scene IS 'Scenes within acts - individual gameplay segments';
COMMENT ON COLUMN adv_scene.entity_id IS 'Unique entity identifier with format: SCN-{12_digit_id}';
COMMENT ON COLUMN adv_scene.act_id IS 'Reference to the parent act';
COMMENT ON COLUMN adv_scene.scene_number IS 'Sequential number of this scene within the act (1, 2, 3...)';
COMMENT ON COLUMN adv_scene.scene_type IS 'Type of scene: exploration, combat, social, puzzle, etc.';
COMMENT ON COLUMN adv_scene.npcs_involved IS 'JSON array of NPCs that appear in this scene';
COMMENT ON COLUMN adv_scene.items_rewards IS 'JSON array of items, treasures, or rewards in this scene';
COMMENT ON COLUMN adv_scene.estimated_duration IS 'Estimated duration in minutes';
COMMENT ON COLUMN adv_scene.session_played IS 'Which session number this scene was actually played in';