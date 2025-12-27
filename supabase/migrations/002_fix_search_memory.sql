-- ============================================
-- Fix search_memory RPC function
-- Run this in Supabase SQL Editor to enable semantic search
-- ============================================
-- Drop and recreate the function with correct parameter order
DROP FUNCTION IF EXISTS search_memory(vector(1536), float, int, text);
DROP FUNCTION IF EXISTS search_memory;
-- Create the search_memory function
CREATE OR REPLACE FUNCTION search_memory(
        query_embedding vector(1536),
        match_threshold float DEFAULT 0.7,
        match_count int DEFAULT 10,
        filter_type text DEFAULT NULL
    ) RETURNS TABLE (
        id uuid,
        content text,
        memory_type text,
        similarity float,
        metadata jsonb,
        created_at timestamptz
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
-- Grant execute permission
GRANT EXECUTE ON FUNCTION search_memory(vector(1536), float, int, text) TO anon,
    authenticated,
    service_role;
-- Test the function (optional)
-- SELECT * FROM search_memory('[0.1, 0.2, ...]'::vector(1536), 0.5, 10, NULL);