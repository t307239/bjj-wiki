/**
 * scripts/migrate-local.ts
 *
 * ローカルのHTMLディレクトリを走査し、wiki_pages / wiki_translations に upsert する。
 * バルク upsert 方式: API コール数を ~7800 → ~55 に削減 (40min → 1min)
 *
 * 使い方:
 *   npx tsx scripts/migrate-local.ts
 *   # または
 *   npm run migrate
 *
 * 必要な環境変数 (.env ファイルまたはシェル):
 *   SUPABASE_URL=https://xxxx.supabase.co
 *   SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
 */

import * as dotenv from "dotenv";
import { createClient } from "@supabase/supabase-js";
import { load, type CheerioAPI } from "cheerio";
import { readdirSync, readFileSync, existsSync } from "fs";
import { join, basename } from "path";

dotenv.config();

// ─────────────────────────────────────────
// 設定
// ─────────────────────────────────────────

const LANGUAGES = ["en", "ja", "pt"] as const;
type Language = (typeof LANGUAGES)[number];

/** bjj-wiki リポジトリのルートディレクトリ（このスクリプトの親の親） */
const WIKI_ROOT = join(__dirname, "..");

const SUPABASE_URL = process.env.SUPABASE_URL ?? "";
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error("❌ SUPABASE_URL と SUPABASE_SERVICE_ROLE_KEY を設定してください");
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { persistSession: false },
});

/** バルク upsert のバッチサイズ（translations は大きいので小さめに） */
const TRANSLATION_BATCH_SIZE = 80;
const PAGES_BATCH_SIZE = 500;

// ─────────────────────────────────────────
// ユーティリティ
// ─────────────────────────────────────────

function chunkArray<T>(arr: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}

// ─────────────────────────────────────────
// HTMLパース ヘルパー
// ─────────────────────────────────────────

function isRedirectFile($: CheerioAPI): boolean {
  return $('meta[http-equiv="refresh"]').length > 0;
}

function extractTitle($: CheerioAPI): string {
  const raw = $("title").text().trim();
  return raw
    .replace(/\s*[\|｜\-–—]\s*BJJ Wiki.*$/i, "")
    .replace(/\s*[\|｜\-–—]\s*BJJウィキ.*$/i, "")
    .trim();
}

function extractDescription($: CheerioAPI): string {
  return $('meta[name="description"]').attr("content")?.trim() ?? "";
}

function extractContentHtml($: CheerioAPI): string {
  const container = $(".container");
  const root = container.length ? container : $("body");

  const removeSelectors = [
    "header", "footer", "nav", "script", "style", "noscript",
    ".progress-bar", ".back-to-top", "#back-to-top",
    ".float-cta", ".contact-section", ".beehiiv-wrap", ".share-bar",
  ];

  const cloned = root.clone();
  removeSelectors.forEach((sel) => cloned.find(sel).remove());
  return cloned.html()?.trim() ?? "";
}

// ─────────────────────────────────────────
// メイン処理
// ─────────────────────────────────────────

async function main() {
  console.log("🚀 Wiki migration 開始 (バルクモード)\n");
  const startTime = Date.now();

  // ─── Phase 1: HTML ファイルを全言語分パース ───
  const slugMap = new Map<string, Map<Language, {
    title: string;
    description: string;
    contentHtml: string;
  }>>();

  for (const lang of LANGUAGES) {
    const langDir = join(WIKI_ROOT, lang);
    if (!existsSync(langDir)) {
      console.warn(`⚠️  ディレクトリが存在しません: ${langDir}`);
      continue;
    }

    const files = readdirSync(langDir).filter((f) => f.endsWith(".html"));
    console.log(`📂 ${lang}/ — ${files.length} ファイル検出`);

    let skipped = 0;
    let parsed = 0;

    for (const file of files) {
      const slug = basename(file, ".html");
      const filePath = join(langDir, file);
      const html = readFileSync(filePath, "utf-8");
      const $ = load(html);

      if (isRedirectFile($)) { skipped++; continue; }

      const title = extractTitle($);
      const description = extractDescription($);
      const contentHtml = extractContentHtml($);

      if (!title) { skipped++; continue; }

      if (!slugMap.has(slug)) slugMap.set(slug, new Map());
      slugMap.get(slug)!.set(lang, { title, description, contentHtml });
      parsed++;
    }

    console.log(`   ✅ ${parsed} ページ解析 / ⏭  ${skipped} スキップ`);
  }

  const allSlugs = [...slugMap.keys()];
  console.log(`\n📊 合計 slug 数: ${allSlugs.length}`);

  // ─── Phase 2: wiki_pages を一括 upsert ───
  console.log("\n⬆️  wiki_pages バルク upsert...");
  const pageRows = allSlugs.map((slug) => ({ slug }));
  const pageChunks = chunkArray(pageRows, PAGES_BATCH_SIZE);

  for (const [i, chunk] of pageChunks.entries()) {
    const { error } = await supabase
      .from("wiki_pages")
      .upsert(chunk, { onConflict: "slug", ignoreDuplicates: true });
    if (error) console.error(`  ⚠️  wiki_pages batch ${i + 1} error:`, error.message);
    else console.log(`  ✅ wiki_pages batch ${i + 1}/${pageChunks.length} (${chunk.length}件)`);
  }

  // ─── Phase 3: slug → id マップを取得 ───
  console.log("\n🔍 wiki_pages ID マップ取得...");
  const pageIdMap = new Map<string, string>();
  const slugChunks = chunkArray(allSlugs, 500);

  for (const chunk of slugChunks) {
    const { data, error } = await supabase
      .from("wiki_pages")
      .select("id, slug")
      .in("slug", chunk);
    if (error) { console.error("  ❌ ID 取得失敗:", error.message); continue; }
    data?.forEach((p) => pageIdMap.set(p.slug, p.id));
  }
  console.log(`  ✅ ${pageIdMap.size}件の ID を取得`);

  // ─── Phase 4: wiki_translations をバルク upsert ───
  console.log("\n⬆️  wiki_translations バルク upsert...");
  const now = new Date().toISOString();

  const allTranslations: object[] = [];
  for (const [slug, langMap] of slugMap) {
    const pageId = pageIdMap.get(slug);
    if (!pageId) { console.warn(`  ⚠️  page_id not found for slug: ${slug}`); continue; }

    for (const [lang, data] of langMap) {
      allTranslations.push({
        page_id: pageId,
        language_code: lang,
        title: data.title,
        description: data.description,
        content_html: data.contentHtml,
        content_type: null,
        updated_at: now,
      });
    }
  }

  console.log(`  📦 合計 ${allTranslations.length} 件の translations を ${TRANSLATION_BATCH_SIZE} 件ずつ処理`);
  const transChunks = chunkArray(allTranslations, TRANSLATION_BATCH_SIZE);
  let transSuccess = 0;
  let transError = 0;

  for (const [i, chunk] of transChunks.entries()) {
    const { error } = await supabase
      .from("wiki_translations")
      .upsert(chunk, { onConflict: "page_id,language_code" });

    if (error) {
      console.error(`  ❌ translations batch ${i + 1} error:`, error.message);
      transError += chunk.length;
    } else {
      transSuccess += chunk.length;
    }

    // 10バッチごとに進捗表示
    if ((i + 1) % 10 === 0) {
      console.log(`  ... ${i + 1}/${transChunks.length} バッチ完了 (${transSuccess} 件成功)`);
    }
  }

  const elapsed = Math.round((Date.now() - startTime) / 1000);
  console.log("\n✅ migration 完了");
  console.log(`   translations 成功: ${transSuccess} 件`);
  console.log(`   translations エラー: ${transError} 件`);
  console.log(`   所要時間: ${elapsed}秒`);
}

main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
