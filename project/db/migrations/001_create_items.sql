-- Supabase SQL 에디터에서 실행하세요.
-- Dashboard → SQL Editor → New Query → 아래 SQL 붙여넣기 → Run

CREATE TABLE IF NOT EXISTS items (
    id           BIGSERIAL PRIMARY KEY,
    type         TEXT NOT NULL CHECK (type IN ('news', 'market')),
    title        TEXT,
    url          TEXT UNIQUE,
    source       TEXT,
    published_at TEXT,
    summary      TEXT,
    symbol       TEXT,
    name         TEXT,
    price        REAL,
    change_pct   REAL,
    volume       REAL,
    fetched_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_items_type_fetched
    ON items(type, fetched_at DESC);

CREATE INDEX IF NOT EXISTS idx_items_market_sym
    ON items(symbol, fetched_at DESC) WHERE type = 'market';

-- 서버 사이드 앱이므로 RLS 비활성화 (publishable key로 모든 CRUD 허용)
ALTER TABLE items DISABLE ROW LEVEL SECURITY;
