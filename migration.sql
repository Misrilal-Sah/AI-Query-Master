
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS query_history (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  db_type TEXT NOT NULL DEFAULT 'mysql',
  feature TEXT NOT NULL DEFAULT 'query_review',
  input_text TEXT NOT NULL,
  result JSONB NOT NULL DEFAULT '{}',
  scores JSONB,
  confidence FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_query_history_created_at ON query_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_query_history_feature ON query_history(feature);
CREATE INDEX IF NOT EXISTS idx_query_history_db_type ON query_history(db_type);
CREATE INDEX IF NOT EXISTS idx_query_history_user_id ON query_history(user_id);

ALTER TABLE query_history ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own history" ON query_history;
DROP POLICY IF EXISTS "Users can insert own history" ON query_history;
DROP POLICY IF EXISTS "Users can delete own history" ON query_history;
DROP POLICY IF EXISTS "Service role full access" ON query_history;

CREATE POLICY "Users can view own history"
  ON query_history FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own history"
  ON query_history FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own history"
  ON query_history FOR DELETE
  USING (auth.uid() = user_id);

CREATE POLICY "Service role full access"
  ON query_history FOR ALL
  USING (true)
  WITH CHECK (true);

-- ============================================================
-- Supabase pgvector-backed RAG storage
-- ============================================================
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS rag_chunks (
  id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  source TEXT NOT NULL,
  category TEXT NOT NULL DEFAULT 'general',
  chunk_index INT NOT NULL DEFAULT 0,
  embedding VECTOR(384) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rag_chunks_category ON rag_chunks(category);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_source ON rag_chunks(source);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding
  ON rag_chunks USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE OR REPLACE FUNCTION public.match_rag_chunks(
  query_embedding VECTOR(384),
  match_count INT DEFAULT 15,
  categories TEXT[] DEFAULT NULL
)
RETURNS TABLE (
  id TEXT,
  content TEXT,
  source TEXT,
  category TEXT,
  chunk_index INT,
  similarity FLOAT
)
LANGUAGE SQL
STABLE
AS $$
  SELECT
    rc.id,
    rc.content,
    rc.source,
    rc.category,
    rc.chunk_index,
    1 - (rc.embedding <=> query_embedding) AS similarity
  FROM rag_chunks rc
  WHERE categories IS NULL OR rc.category = ANY(categories)
  ORDER BY rc.embedding <=> query_embedding
  LIMIT GREATEST(match_count, 1);
$$;
