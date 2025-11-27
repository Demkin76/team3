CREATE TABLE IF NOT EXISTS requests (
  id TEXT PRIMARY KEY,
  input_type TEXT NOT NULL,
  input_value TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'received',
  stage TEXT NOT NULL DEFAULT 'received',
  progress DOUBLE PRECISION NOT NULL DEFAULT 0,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS request_parsed (
  request_id TEXT PRIMARY KEY REFERENCES requests(id) ON DELETE CASCADE,
  json_prompt JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS results (
  request_id TEXT PRIMARY KEY REFERENCES requests(id) ON DELETE CASCADE,
  analogs JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS sites_cache (
  site_id TEXT PRIMARY KEY,
  normalized_json_prompt JSONB NOT NULL,
  embedding JSONB,
  analogs JSONB NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now()
);
