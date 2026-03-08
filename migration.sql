
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
