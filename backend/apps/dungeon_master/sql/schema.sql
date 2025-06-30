-- ==================================================
-- Dungeon Master System - Complete Database Schema
-- ==================================================

-- ==================================================
-- 1. CORE DUNGEON MASTER TABLE
-- ==================================================
CREATE TABLE dm_user_dungeonmaster (
    id BIGSERIAL PRIMARY KEY,
    entity_id VARCHAR(20) UNIQUE NOT NULL CHECK (entity_id ~ '^DM-[0-9]{12}$'),
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    -- Core DM Profile Information
    display_name VARCHAR(200),
    bio TEXT CHECK (char_length(bio) <= 2000),
    experience_level VARCHAR(20) DEFAULT 'beginner' CHECK (
        experience_level IN ('beginner', 'intermediate', 'advanced', 'expert', 'master')
    ),
        
    -- Game Mastering Style & Preferences
    strictness_level INTEGER CHECK (strictness_level BETWEEN 1 AND 10) DEFAULT 5,
    green_flags JSONB DEFAULT '[]', -- Array of positive preferences/styles
    red_flags JSONB DEFAULT '[]',  -- Array of things to avoid/dislikes  
    
    -- Content Preferences
    content_rating VARCHAR(10) DEFAULT 'teen' CHECK (
        content_rating IN ('family', 'teen', 'mature', 'adult')
    ),
    themes_preferences JSONB DEFAULT '[]', -- preferred themes and genres
    
    -- Status and Metadata
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT FALSE, -- whether profile is publicly visible
    last_active TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================================================
-- 2. USER SETTINGS TABLE (UI/UX & AI)
-- ==================================================
CREATE TABLE dm_user_settings (
    id BIGSERIAL PRIMARY KEY,
    dungeonmaster_id BIGINT NOT NULL REFERENCES dm_user_dungeonmaster(id) ON DELETE CASCADE,
    
    -- UI/UX Settings
    ui_settings JSONB DEFAULT '{
        "theme": "dark",
        "language": "de",
        "timezone": "UTC",
        "date_format": "YYYY-MM-DD",
        "time_format": "24h",
        "compact_mode": false,
        "show_tooltips": true,
        "auto_save_interval": 300,
        "notification_preferences": {
            "email": true,
            "browser": true,
            "sound": false
        },
        "dashboard_layout": {
            "widget_order": [],
            "collapsed_sections": []
        },
        "accessibility": {
            "high_contrast": false,
            "large_text": false,
            "screen_reader_support": false
        }
    }',
    
    -- AI Assistant Settings
    ai_settings JSONB DEFAULT '{
        "language": "de",
        "memory_retention": true,
        "specialized_features": {
            "world_building_assistant": true,
            "npc_generator": true,
            "plot_suggestions": true,
            "rule_clarifications": true,
            "session_summaries": true
        }
    }',
    
    -- Feature Flags & Experimental Features
    feature_flags JSONB DEFAULT '{
        "beta_features": false
    }',
    
    -- Privacy & Security Preferences
    privacy_settings JSONB DEFAULT '{
        "profile_visibility": "private"
    }',
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure one settings record per DM
    UNIQUE(dungeonmaster_id)
);

-- ==================================================
-- 3. API KEYS TABLE (Encrypted Storage)
-- ==================================================
CREATE TABLE dm_user_keys (
    id BIGSERIAL PRIMARY KEY,
    dungeonmaster_id BIGINT NOT NULL REFERENCES dm_user_dungeonmaster(id) ON DELETE CASCADE,
    
    -- Encrypted API Keys (using pgcrypto extension)
    openai_key_encrypted BYTEA NULL,
    anthropic_key_encrypted BYTEA NULL,
    google_key_encrypted BYTEA NULL,
    deepseek_key_encrypted BYTEA NULL,
    
    -- Key Status and Metadata
    openai_status VARCHAR(20) DEFAULT 'not_configured' CHECK (
        openai_status IN ('not_configured', 'configured', 'invalid', 'expired', 'suspended')
    ),
    anthropic_status VARCHAR(20) DEFAULT 'not_configured' CHECK (
        anthropic_status IN ('not_configured', 'configured', 'invalid', 'expired', 'suspended')
    ),
    google_status VARCHAR(20) DEFAULT 'not_configured' CHECK (
        google_status IN ('not_configured', 'configured', 'invalid', 'expired', 'suspended')
    ),
    deepseek_status VARCHAR(20) DEFAULT 'not_configured' CHECK (
        deepseek_status IN ('not_configured', 'configured', 'invalid', 'expired', 'suspended')
    ),
    
    -- Last Validation Timestamps
    openai_last_validated TIMESTAMPTZ NULL,
    anthropic_last_validated TIMESTAMPTZ NULL,
    google_last_validated TIMESTAMPTZ NULL,
    deepseek_last_validated TIMESTAMPTZ NULL,
    
    -- Usage Tracking (for rate limiting and monitoring)
    usage_statistics JSONB DEFAULT '{
        "openai": {"requests_today": 0, "last_request": null},
        "anthropic": {"requests_today": 0, "last_request": null},
        "google": {"requests_today": 0, "last_request": null},
        "deepseek": {"requests_today": 0, "last_request": null}
    }',
    
    -- Security Metadata
    encryption_version INTEGER DEFAULT 1, -- for key rotation
    last_key_update TIMESTAMPTZ DEFAULT NOW(),
    security_notes TEXT, -- for admin notes about key issues
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure one keys record per DM
    UNIQUE(dungeonmaster_id)
);

-- ==================================================
-- INDEXES FOR PERFORMANCE
-- ==================================================

-- Primary entity indexes
CREATE INDEX idx_dm_user_dungeonmaster_entity_id ON dm_user_dungeonmaster(entity_id);
CREATE INDEX idx_dm_user_dungeonmaster_user_id ON dm_user_dungeonmaster(user_id);
CREATE INDEX idx_dm_user_dungeonmaster_is_active ON dm_user_dungeonmaster(is_active);
CREATE INDEX idx_dm_user_dungeonmaster_experience ON dm_user_dungeonmaster(experience_level);
CREATE INDEX idx_dm_user_dungeonmaster_public ON dm_user_dungeonmaster(is_public);
CREATE INDEX idx_dm_user_dungeonmaster_last_active ON dm_user_dungeonmaster(last_active);

-- Foreign key indexes for settings and keys
CREATE INDEX idx_dm_user_settings_dungeonmaster_id ON dm_user_settings(dungeonmaster_id);
CREATE INDEX idx_dm_user_keys_dungeonmaster_id ON dm_user_keys(dungeonmaster_id);

-- JSONB indexes for efficient JSON queries
CREATE INDEX idx_dm_user_dungeonmaster_preferred_systems_gin ON dm_user_dungeonmaster USING GIN(preferred_systems);
CREATE INDEX idx_dm_user_dungeonmaster_green_flags_gin ON dm_user_dungeonmaster USING GIN(green_flags);
CREATE INDEX idx_dm_user_dungeonmaster_red_flags_gin ON dm_user_dungeonmaster USING GIN(red_flags);
CREATE INDEX idx_dm_user_settings_ui_settings_gin ON dm_user_settings USING GIN(ui_settings);
CREATE INDEX idx_dm_user_settings_ai_settings_gin ON dm_user_settings USING GIN(ai_settings);
CREATE INDEX idx_dm_user_settings_feature_flags_gin ON dm_user_settings USING GIN(feature_flags);