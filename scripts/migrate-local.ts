/**
 * scripts/migrate-local.ts
 *
 * ローカルのHTMLディレクトリを走査し、wiki_pages / wiki_translations に upsert する。
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

// ─────────────────────────────────────────
// HTMLパース ヘルパー
// ─────────────────────────────────────────

/** <meta http-equiv="refresh"> があればリダイレクトファイルと判定 */
function isRedirectFile($: CheerioAPI): boolean {
  return $('meta[http-equiv="refresh"]').length > 0;
}

/**
 * <title> から "| BJJ Wiki" などの不要なサフィックスを除去してタイトルを抽出。
 * 空の場合は空文字を返す。
 */
function extractTitle($: CheerioAPI): string {
  const raw = $("title").text().trim();
  // "Some Title | BJJ Wiki" → "Some Title"
  // "Some Title - BJJ Wiki" → "Some Title"
  return raw
    .replace(/\s*[\|｜\-–—]\s*BJJ Wiki.*$/i, "")
    .replace(/\s*[\|｜\-–—]\s*BJJウィキ.*$/i, "")
    .trim();
}

/** <meta name="description"> を取得 */
function extractDescription($: CheerioAPI): string {
  return $('meta[name="description"]').attr("content")?.trim() ?? "";
}

/**
 * メインコンテンツの HTML を抽出。
 * .container が存在すればその innerHTML を使う。なければ <body> をフォールバック。
 * ヘッダー・フッター・ナビ・スクリプト・スタイルは除去する。
 */
function extractContentHtml($: CheerioAPI): string {
  const container = $(".container");
  const root = container.length ? container : $("body");

  // 除去対象のセレクター
  const removeSelectors = [
    "header",
    "footer",
    "nav",
    "script",
    "style",
    "noscript",
    ".progress-bar",
    ".back-to-top",
    "#back-to-top",
    ".float-cta",
    ".contact-section",
    ".beehiiv-wrap",
    ".share-bar",
  ];

  // クローンして不要要素を削除
  const cloned = root.clone();
  removeSelectors.forEach((sel) => cloned.find(sel).remove());

  return cloned.html()?.trim() ?? "";
}

// ─────────────────────────────────────────
// メイン処理
// ─────────────────────────────────────────

async function main() {
  console.log("🚀 Wiki migration 開始\n");

  // slug ごとに { lang → parsed data } を収集
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
      const slug = basename(file, ".html"); // "armbar.html" → "armbar"
      const filePath = join(langDir, file);
      const html = readFileSync(filePath, "utf-8");
      const $ = load(html);

      // リダイレクトファイルはスキップ
      if (isRedirectFile($)) {
        skipped++;
        continue;
      }

      const title = extractTitle($);
      const description = extractDescription($);
      const contentHtml = extractContentHtml($);

      if (!title) {
        // タイトルが空のファイルもスキップ
        skipped++;
        continue;
      }

      if (!slugMap.has(slug)) {
        slugMap.set(slug, new Map());
      }
      slugMap.get(slug)!.set(lang, { title, description, contentHtml });
      parsed++;
    }

    console.log(`   ✅ ${parsed} ページ解析 / ⏭  ${skipped} スキップ`);
  }

  console.log(`\n📊 合計 slug 数: ${slugMap.size}`);
  console.log("⬆️  Supabase に upsert 中...\n");

  let successCount = 0;
  let errorCount = 0;

  for (const [slug, langMap] of slugMap) {
    // 1. wiki_pages upsert (slug で衝突時は updated_at を更新しない — created_at を保持)
    const { data: pageData, error: pageError } = await supabase
      .from("wiki_pages")
      .upsert({ slug }, { onConflict: "slug", ignoreDuplicates: true })
      .select("id")
      .single();

    if (pageError) {
      // ignoreDuplicates=true の場合、既存行は null を返すので SELECT で取得
      const { data: existing, error: fetchError } = await supabase
        .from("wiki_pages")
        .select("id")
        .eq("slug", slug)
        .single();

      if (fetchError || !existing) {
        console.error(`❌ wiki_pages upsert 失敗 [${slug}]:`, pageError.message);
        errorCount++;
        continue;
      }

      // 2. 各言語の wiki_translations upsert
      for (const [lang, data] of langMap) {
        const { error: transError } = await supabase
          .from("wiki_translations")
          .upsert(
            {
              page_id: existing.id,
              language_code: lang,
              title: data.title,
              description: data.description,
              content_html: data.contentHtml,
              content_type: null, // AI分類は後フェーズで実施
              updated_at: new Date().toISOString(),
            },
            { onConflict: "page_id,language_code" }
          );

        if (transError) {
          console.error(`❌ wiki_translations upsert 失敗 [${slug}/${lang}]:`, transError.message);
          errorCount++;
        }
      }
    } else {
      // 新規挿入成功
      const pageId = pageData?.id;

      for (const [lang, data] of langMap) {
        const { error: transError } = await supabase
          .from("wiki_translations")
          .upsert(
            {
              page_id: pageId,
              language_code: lang,
              title: data.title,
              description: data.description,
              content_html: data.contentHtml,
              content_type: null,
              updated_at: new Date().toISOString(),
            },
            { onConflict: "page_id,language_code" }
          );

        if (transError) {
          console.error(`❌ wiki_translations upsert 失敗 [${slug}/${lang}]:`, transError.message);
          errorCount++;
        }
      }
    }

    successCount++;

    // 100件ごとに進捗表示
    if (successCount % 100 === 0) {
      console.log(`   ... ${successCount} / ${slugMap.size} 完了`);
    }
  }

  console.log("\n✅ migration 完了");
  console.log(`   成功: ${successCount} slugs`);
  console.log(`   エラー: ${errorCount}`);
}

main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
