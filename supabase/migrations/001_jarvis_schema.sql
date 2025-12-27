-- ============================================
-- JARVIS Database Schema
-- Version: 1.0.0
-- Created: 2025-12-25
-- ============================================
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
-- ============================================
-- AGENTS TABLE
-- Core agent registry for JARVIS and specialists
-- ============================================
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('master', 'specialist', 'subordinate')),
    status TEXT NOT NULL DEFAULT 'active' CHECK (
        status IN ('active', 'inactive', 'paused', 'error')
    ),
    parent_id UUID REFERENCES agents(id) ON DELETE
    SET NULL,
        system_prompt TEXT,
        config JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for agents
CREATE INDEX idx_agents_type ON agents(type);
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_parent ON agents(parent_id);
-- ============================================
-- TASKS TABLE
-- Task management and hierarchy
-- ============================================
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    parent_task_id UUID REFERENCES tasks(id) ON DELETE
    SET NULL,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL DEFAULT 'pending' CHECK (
            status IN (
                'pending',
                'running',
                'completed',
                'failed',
                'cancelled'
            )
        ),
        priority INT DEFAULT 5 CHECK (
            priority >= 1
            AND priority <= 10
        ),
        result JSONB,
        related_entities UUID [] DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        started_at TIMESTAMPTZ,
        completed_at TIMESTAMPTZ
);
-- Indexes for tasks
CREATE INDEX idx_tasks_agent ON tasks(agent_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX idx_tasks_priority ON tasks(priority DESC);
CREATE INDEX idx_tasks_created ON tasks(created_at DESC);
CREATE INDEX idx_tasks_related_entities ON tasks USING GIN (related_entities);
-- ============================================
-- CONVERSATIONS TABLE
-- Chat history and context
-- ============================================
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    title TEXT,
    summary TEXT,
    summary_embedding VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for conversations
CREATE INDEX idx_conversations_agent ON conversations(agent_id);
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);
CREATE INDEX idx_conversations_embedding ON conversations USING ivfflat (summary_embedding vector_cosine_ops) WITH (lists = 100);
-- ============================================
-- MESSAGES TABLE
-- Individual messages within conversations
-- ============================================
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for messages
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_created ON messages(created_at);
-- ============================================
-- SHARED MEMORY TABLE
-- Long-term memory accessible across agents
-- ============================================
CREATE TABLE shared_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    memory_type TEXT NOT NULL CHECK (
        memory_type IN (
            'fact',
            'procedure',
            'preference',
            'context',
            'solution'
        )
    ),
    source_agent_id UUID REFERENCES agents(id) ON DELETE
    SET NULL,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for shared_memory
CREATE INDEX idx_memory_type ON shared_memory(memory_type);
CREATE INDEX idx_memory_source ON shared_memory(source_agent_id);
CREATE INDEX idx_memory_created ON shared_memory(created_at DESC);
CREATE INDEX idx_memory_embedding ON shared_memory USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- ============================================
-- ENTITIES TABLE
-- Knowledge graph nodes
-- ============================================
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for entities
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_entities_name ON entities(name);
CREATE INDEX idx_entities_properties ON entities USING GIN (properties);
CREATE UNIQUE INDEX idx_entities_type_name ON entities(type, name);
-- ============================================
-- ENTITY RELATIONSHIPS TABLE
-- Knowledge graph edges
-- ============================================
CREATE TABLE entity_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_entity UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    to_entity UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    relationship TEXT NOT NULL,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for entity_relationships
CREATE INDEX idx_relationships_from ON entity_relationships(from_entity);
CREATE INDEX idx_relationships_to ON entity_relationships(to_entity);
CREATE INDEX idx_relationships_type ON entity_relationships(relationship);
CREATE UNIQUE INDEX idx_relationships_unique ON entity_relationships(from_entity, to_entity, relationship);
-- ============================================
-- AGENT COSTS TABLE
-- Usage tracking and cost monitoring
-- ============================================
CREATE TABLE agent_costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    tokens_in INT DEFAULT 0,
    tokens_out INT DEFAULT 0,
    api_cost DECIMAL(10, 4) DEFAULT 0,
    tasks_completed INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for agent_costs
CREATE INDEX idx_costs_agent ON agent_costs(agent_id);
CREATE INDEX idx_costs_date ON agent_costs(date DESC);
CREATE UNIQUE INDEX idx_costs_agent_date ON agent_costs(agent_id, date);
-- ============================================
-- FILES TABLE
-- File storage metadata
-- ============================================
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE
    SET NULL,
        filename TEXT NOT NULL,
        path TEXT NOT NULL,
        mime_type TEXT,
        size_bytes BIGINT,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for files
CREATE INDEX idx_files_agent ON files(agent_id);
CREATE INDEX idx_files_type ON files(mime_type);
CREATE INDEX idx_files_path ON files(path);
-- ============================================
-- RPC FUNCTIONS
-- ============================================
-- Semantic search on shared memory
CREATE OR REPLACE FUNCTION search_memory(
        query_embedding VECTOR(1536),
        match_threshold FLOAT DEFAULT 0.7,
        match_count INT DEFAULT 10,
        filter_type TEXT DEFAULT NULL
    ) RETURNS TABLE (
        id UUID,
        content TEXT,
        memory_type TEXT,
        similarity FLOAT,
        metadata JSONB,
        created_at TIMESTAMPTZ
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT sm.id,
    sm.content,
    sm.memory_type,
    1 - (sm.embedding <=> query_embedding) AS similarity,
    sm.metadata,
    sm.created_at
FROM shared_memory sm
WHERE (
        filter_type IS NULL
        OR sm.memory_type = filter_type
    )
    AND 1 - (sm.embedding <=> query_embedding) > match_threshold
ORDER BY sm.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Search conversations by summary similarity
CREATE OR REPLACE FUNCTION search_conversations(
        query_embedding VECTOR(1536),
        match_threshold FLOAT DEFAULT 0.7,
        match_count INT DEFAULT 5,
        agent_filter UUID DEFAULT NULL
    ) RETURNS TABLE (
        id UUID,
        title TEXT,
        summary TEXT,
        similarity FLOAT,
        agent_id UUID,
        created_at TIMESTAMPTZ
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT c.id,
    c.title,
    c.summary,
    1 - (c.summary_embedding <=> query_embedding) AS similarity,
    c.agent_id,
    c.created_at
FROM conversations c
WHERE c.summary_embedding IS NOT NULL
    AND (
        agent_filter IS NULL
        OR c.agent_id = agent_filter
    )
    AND 1 - (c.summary_embedding <=> query_embedding) > match_threshold
ORDER BY c.summary_embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Get agent with task stats
CREATE OR REPLACE FUNCTION get_agent_stats(target_agent_id UUID) RETURNS TABLE (
        agent_name TEXT,
        total_tasks BIGINT,
        completed_tasks BIGINT,
        failed_tasks BIGINT,
        avg_task_duration INTERVAL,
        total_conversations BIGINT,
        total_memories BIGINT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT a.name AS agent_name,
    COUNT(DISTINCT t.id) AS total_tasks,
    COUNT(DISTINCT t.id) FILTER (
        WHERE t.status = 'completed'
    ) AS completed_tasks,
    COUNT(DISTINCT t.id) FILTER (
        WHERE t.status = 'failed'
    ) AS failed_tasks,
    AVG(t.completed_at - t.started_at) FILTER (
        WHERE t.completed_at IS NOT NULL
    ) AS avg_task_duration,
    COUNT(DISTINCT c.id) AS total_conversations,
    COUNT(DISTINCT sm.id) AS total_memories
FROM agents a
    LEFT JOIN tasks t ON t.agent_id = a.id
    LEFT JOIN conversations c ON c.agent_id = a.id
    LEFT JOIN shared_memory sm ON sm.source_agent_id = a.id
WHERE a.id = target_agent_id
GROUP BY a.id,
    a.name;
END;
$$;
-- ============================================
-- TRIGGERS
-- ============================================
-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trigger_agents_updated_at BEFORE
UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trigger_conversations_updated_at BEFORE
UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trigger_entities_updated_at BEFORE
UPDATE ON entities FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trigger_files_updated_at BEFORE
UPDATE ON files FOR EACH ROW EXECUTE FUNCTION update_updated_at();
-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- Enable for production use
-- ============================================
-- Enable RLS on all tables (policies to be added based on auth requirements)
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE shared_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE entity_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_costs ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
-- Default policy: Allow all for authenticated users (customize for production)
CREATE POLICY "Allow all for authenticated" ON agents FOR ALL USING (true);
CREATE POLICY "Allow all for authenticated" ON tasks FOR ALL USING (true);
CREATE POLICY "Allow all for authenticated" ON conversations FOR ALL USING (true);
CREATE POLICY "Allow all for authenticated" ON messages FOR ALL USING (true);
CREATE POLICY "Allow all for authenticated" ON shared_memory FOR ALL USING (true);
CREATE POLICY "Allow all for authenticated" ON entities FOR ALL USING (true);
CREATE POLICY "Allow all for authenticated" ON entity_relationships FOR ALL USING (true);
CREATE POLICY "Allow all for authenticated" ON agent_costs FOR ALL USING (true);
CREATE POLICY "Allow all for authenticated" ON files FOR ALL USING (true);
-- ============================================
-- COMMENTS
-- ============================================
COMMENT ON TABLE agents IS 'Registry of all AI agents in the JARVIS system';
COMMENT ON TABLE tasks IS 'Task queue and execution history';
COMMENT ON TABLE conversations IS 'Chat sessions with summary embeddings for semantic search';
COMMENT ON TABLE messages IS 'Individual messages within conversations';
COMMENT ON TABLE shared_memory IS 'Long-term semantic memory shared across agents';
COMMENT ON TABLE entities IS 'Knowledge graph nodes for structured data';
COMMENT ON TABLE entity_relationships IS 'Knowledge graph edges connecting entities';
COMMENT ON TABLE agent_costs IS 'Daily cost and usage tracking per agent';
COMMENT ON TABLE files IS 'Metadata for files stored in Supabase Storage';