-- Wiki pages migration
-- Run in Supabase SQL Editor

-- ─────────────────────────────────────────
-- 1. wiki_pages: slug をキーとするマスターテーブル
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wiki_pages (
  id          BIGSERIAL PRIMARY KEY,
  slug        TEXT NOT NULL UNIQUE,   -- e.g. "armbar", "triangle-choke"
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS wiki_pages_slug_idx ON wiki_pages (slug);

-- ─────────────────────────────────────────
-- 2. wiki_translations: 言語ごとのコンテンツ
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wiki_translations (
  id            BIGSERIAL PRIMARY KEY,
  page_id       BIGINT NOT NULL REFERENCES wiki_pages(id) ON DELETE CASCADE,
  language_code TEXT NOT NULL,          -- "en" | "ja" | "pt"
  title         TEXT NOT NULL,
  description   TEXT,
  content_html  TEXT,
  content_type  TEXT,                   -- 将来 Enum に移行予定 (e.g. "technique", "guide", "concept")
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE (page_id, language_code)
);

CREATE INDEX IF NOT EXISTS wiki_translations_page_lang_idx
  ON wiki_translations (page_id, language_code);

-- ─────────────────────────────────────────
-- 3. RLS: 全ユーザーが読み取り可能（認証不要）
-- ─────────────────────────────────────────
ALTER TABLE wiki_pages        ENABLE ROW LEVEL SECURITY;
ALTER TABLE wiki_translations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "wiki_pages_public_read"
  ON wiki_pages FOR SELECT USING (true);

CREATE POLICY "wiki_translations_public_read"
  ON wiki_translations FOR SELECT USING (true);

-- 書き込みはサービスロールのみ（migrate スクリプトが使用）
CREATE POLICY "wiki_pages_service_insert"
  ON wiki_pages FOR INSERT
  WITH CHECK (true);  -- service_role は RLS をバイパスするため実質この行は不要だが明示的に残す

CREATE POLICY "wiki_translations_service_insert"
  ON wiki_translations FOR INSERT
  WITH CHECK (true);

CREATE POLICY "wiki_pages_service_update"
  ON wiki_pages FOR UPDATE USING (true);

CREATE POLICY "wiki_translations_service_update"
  ON wiki_translations FOR UPDATE USING (true);
