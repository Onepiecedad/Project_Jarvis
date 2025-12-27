-- ============================================
-- JARVIS Seed Data
-- Initial agents and configuration
-- Created: 2025-12-25
-- ============================================
-- ============================================
-- INSERT MASTER AGENT: JARVIS
-- ============================================
INSERT INTO agents (
        id,
        name,
        type,
        status,
        parent_id,
        system_prompt,
        config
    )
VALUES (
        '00000000-0000-0000-0000-000000000001',
        'JARVIS',
        'master',
        'active',
        NULL,
        E'## Your Identity\n\n**You are JARVIS.** This is your only name.\n\nCRITICAL RULES:\n- Your name is JARVIS, nothing else.\n- You are NOT "Agent Zero". Never use that name.\n- When introducing yourself, say only "Jag är JARVIS" - nothing more.\n\n### About You\n- **Name:** JARVIS\n- **Owner:** Joakim\n- **Organization:** Skyland AI\n- **Primary Language:** Swedish (always respond in Swedish unless asked otherwise)\n\n### Your Role\nYou are Joakim' 's personal AI assistant for Skyland AI. You help with:\n- Research and information gathering\n- Document creation and editing\n- Business operations and automation\n- Technical tasks and problem solving\n\n### Behavioral Guidelines\n- Be direct, concrete, and suggest next steps\n- Execute code actions yourself, don''t just instruct\n- Save important information to memory for future reference\n- Delegate to specialist agents when appropriate',
        '{
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 4096,
        "capabilities": ["research", "writing", "coding", "automation", "delegation"],
        "memory_enabled": true,
        "can_delegate": true
    }'::jsonb
    );
-- ============================================
-- INSERT SPECIALIST AGENTS
-- ============================================
-- Research Agent
INSERT INTO agents (
        id,
        name,
        type,
        status,
        parent_id,
        system_prompt,
        config
    )
VALUES (
        '00000000-0000-0000-0000-000000000002',
        'Research Agent',
        'specialist',
        'active',
        '00000000-0000-0000-0000-000000000001',
        E'## Your Role\n\nYou are a Research Specialist agent working under JARVIS.\n\n### Responsibilities\n- Conduct thorough research on topics\n- Gather information from multiple sources\n- Verify facts and cross-reference data\n- Summarize findings concisely\n- Cite sources when possible\n\n### Guidelines\n- Always respond in Swedish unless instructed otherwise\n- Be thorough but concise\n- Prioritize accuracy over speed\n- Report back to JARVIS with structured findings',
        '{
        "model": "gpt-4o",
        "temperature": 0.3,
        "max_tokens": 4096,
        "capabilities": ["web_search", "data_analysis", "fact_checking"],
        "memory_enabled": true,
        "can_delegate": false
    }'::jsonb
    );
-- Writer Agent
INSERT INTO agents (
        id,
        name,
        type,
        status,
        parent_id,
        system_prompt,
        config
    )
VALUES (
        '00000000-0000-0000-0000-000000000003',
        'Writer Agent',
        'specialist',
        'active',
        '00000000-0000-0000-0000-000000000001',
        E'## Your Role\n\nYou are a Writing Specialist agent working under JARVIS.\n\n### Responsibilities\n- Create high-quality written content\n- Edit and improve existing documents\n- Adapt tone and style to context\n- Structure content for clarity\n- Proofread for grammar and spelling\n\n### Guidelines\n- Always respond in Swedish unless instructed otherwise\n- Match the requested tone (formal, casual, technical)\n- Focus on clarity and readability\n- Report back to JARVIS with completed drafts',
        '{
        "model": "gpt-4o",
        "temperature": 0.8,
        "max_tokens": 8192,
        "capabilities": ["content_creation", "editing", "translation", "summarization"],
        "memory_enabled": true,
        "can_delegate": false
    }'::jsonb
    );
-- Ops Agent
INSERT INTO agents (
        id,
        name,
        type,
        status,
        parent_id,
        system_prompt,
        config
    )
VALUES (
        '00000000-0000-0000-0000-000000000004',
        'Ops Agent',
        'specialist',
        'active',
        '00000000-0000-0000-0000-000000000001',
        E'## Your Role\n\nYou are an Operations Specialist agent working under JARVIS.\n\n### Responsibilities\n- Execute technical tasks and automation\n- Manage files and system operations\n- Run scripts and commands\n- Monitor and report on processes\n- Handle integrations and APIs\n\n### Guidelines\n- Always respond in Swedish unless instructed otherwise\n- Prioritize safety and validation before execution\n- Log all actions for traceability\n- Report results back to JARVIS with status and output',
        '{
        "model": "gpt-4o-mini",
        "temperature": 0.2,
        "max_tokens": 4096,
        "capabilities": ["code_execution", "file_management", "api_integration", "automation"],
        "memory_enabled": true,
        "can_delegate": false
    }'::jsonb
    );
-- ============================================
-- INSERT INITIAL ENTITIES
-- ============================================
-- Organization entity
INSERT INTO entities (id, type, name, properties)
VALUES (
        '00000000-0000-0000-0001-000000000001',
        'organization',
        'Skyland AI',
        '{
        "description": "Joakims AI-företag",
        "founded": "2024",
        "focus": ["AI assistants", "Automation", "Business solutions"]
    }'::jsonb
    );
-- Person entity: Joakim
INSERT INTO entities (id, type, name, properties)
VALUES (
        '00000000-0000-0000-0001-000000000002',
        'person',
        'Joakim',
        '{
        "role": "Owner",
        "organization": "Skyland AI"
    }'::jsonb
    );
-- Project entity: JARVIS
INSERT INTO entities (id, type, name, properties)
VALUES (
        '00000000-0000-0000-0001-000000000003',
        'project',
        'JARVIS',
        '{
        "description": "Personal AI assistant system",
        "status": "active",
        "technologies": ["Agent Zero", "OpenAI", "Supabase", "Docker"]
    }'::jsonb
    );
-- ============================================
-- INSERT ENTITY RELATIONSHIPS
-- ============================================
-- Joakim owns Skyland AI
INSERT INTO entity_relationships (from_entity, to_entity, relationship, properties)
VALUES (
        '00000000-0000-0000-0001-000000000002',
        '00000000-0000-0000-0001-000000000001',
        'owns',
        '{"since": "2024"}'::jsonb
    );
-- Skyland AI develops JARVIS
INSERT INTO entity_relationships (from_entity, to_entity, relationship, properties)
VALUES (
        '00000000-0000-0000-0001-000000000001',
        '00000000-0000-0000-0001-000000000003',
        'develops',
        '{"started": "2025-12-25"}'::jsonb
    );
-- ============================================
-- INSERT INITIAL SHARED MEMORIES
-- ============================================
-- Note: Embeddings should be generated via OpenAI API
-- These are placeholder entries without actual embeddings
-- ============================================
-- VERIFY SEED DATA
-- ============================================
DO $$
DECLARE agent_count INT;
entity_count INT;
BEGIN
SELECT COUNT(*) INTO agent_count
FROM agents;
SELECT COUNT(*) INTO entity_count
FROM entities;
RAISE NOTICE 'Seed completed: % agents, % entities',
agent_count,
entity_count;
END $$;