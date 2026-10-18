CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS filings (
  accession_no  TEXT PRIMARY KEY,
  ticker        TEXT NOT NULL,
  form_type     TEXT NOT NULL,
  fiscal_year   INT,
  filed_at      DATE,
  url           TEXT
);

CREATE TABLE IF NOT EXISTS chunks (
  id            BIGSERIAL PRIMARY KEY,
  accession_no  TEXT REFERENCES filings(accession_no) ON DELETE CASCADE,
  section       TEXT,
  chunk_index   INT,
  text          TEXT NOT NULL,
  embedding     vector(384),
  tsv           tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED
);
CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON chunks USING GIN (tsv);
CREATE INDEX IF NOT EXISTS chunks_emb_idx ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS financial_facts (
  id            BIGSERIAL PRIMARY KEY,
  ticker        TEXT NOT NULL,
  fiscal_year   INT NOT NULL,
  metric        TEXT NOT NULL,
  value         NUMERIC,
  unit          TEXT,
  accession_no  TEXT REFERENCES filings(accession_no) ON DELETE CASCADE,
  UNIQUE (ticker, fiscal_year, metric)
);

CREATE TABLE IF NOT EXISTS filing_diffs (
  id            BIGSERIAL PRIMARY KEY,
  ticker        TEXT NOT NULL,
  section       TEXT NOT NULL,
  from_year     INT NOT NULL,
  to_year       INT NOT NULL,
  change_type   TEXT,
  summary       TEXT
);
