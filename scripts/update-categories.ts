/**
 * scripts/update-categories.ts
 *
 * wiki_translations の content_type を slug のキーワードで自動分類して一括UPDATE。
 *
 * 使い方:
 *   npm run update-categories
 *   # または
 *   npx tsx scripts/update-categories.ts
 *
 * 分類ロジック（優先度順）:
 *   1. 'athlete'                                            -> Athlete_Bio
 *   2. rule / scoring / stalling / points / penalty / advantage  -> Rule
 *   3. best- / gear / gi- / bag / pad / mouthguard / rash-guard  -> Equipment_Gear
 *   4. diet / nutrition / strength / conditioning / cardio /
 *      recovery / health / sleep / protein / supplement /
 *      injury / athletic                                    -> Conditioning_Nutrition
 *   5. mindset / strategy / concept / -vs- / game-plan /
 *      philosophy / iq / etiquette / culture / history      -> Concept_Strategy
 *   6. drill / warm-up / routine / shark-tank / flow-rolling -> Drill
 *   7. (その他)                                              -> Technique
 */

import * as dotenv from "dotenv";
import { createClient } from "@supabase/supabase-js";
import { join } from "path";

dotenv.config({ path: join(__dirname, "../.env") });

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
// 分類ロジック
// ─────────────────────────────────────────

type ContentType =
  | "Athlete_Bio"
  | "Rule"
  | "Equipment_Gear"
  | "Conditioning_Nutrition"
  | "Concept_Strategy"
  | "Drill"
  | "Technique";

function classify(slug: string): ContentType {
  const s = slug.toLowerCase();

  if (s.includes("athlete")) return "Athlete_Bio";

  if (
    ["rule", "scoring", "stalling", "points", "penalty", "advantage"].some(
      (k) => s.includes(k)
    )
  )
    return "Rule";

  if (
    ["best-", "gear", "gi-", "bag", "pad", "mouthguard", "rash-guard"].some(
      (k) => s.includes(k)
    )
  )
    return "Equipment_Gear";

  if (
    [
      "diet",
      "nutrition",
      "strength",
      "conditioning",
      "cardio",
      "recovery",
      "health",
      "sleep",
      "protein",
      "supplement",
      "injury",
      "athletic",
    ].some((k) => s.includes(k))
  )
    return "Conditioning_Nutrition";

  if (
    [
      "mindset",
      "strategy",
      "concept",
      "-vs-",
      "game-plan",
      "philosophy",
      "iq",
      "etiquette",
      "culture",
      "history",
    ].some((k) => s.includes(k))
  )
    return "Concept_Strategy";

  if (
    ["drill", "warm-up", "routine", "shark-tank", "flow-rolling"].some((k) =>
      s.includes(k)
    )
  )
    return "Drill";

  return "Technique";
}

// ─────────────────────────────────────────
// ユーティリティ
// ─────────────────────────────────────────

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function chunk<T>(arr: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}

// ─────────────────────────────────────────
// メイン処理
// ─────────────────────────────────────────

async function main() {
  console.log("📥 wiki_pages + wiki_translations を全件取得中...\n");

  // 全ての wiki_translations を page_id と一緒に取得（ページネーションを使う）
  let allRows: Array<{ id: bigint | number; page_id: bigint | number; language_code: string; content_type: string | null; slug: string }> = [];
  let from = 0;
  const PAGE_SIZE = 1000;

  while (true) {
    const { data, error } = await supabase
      .from("wiki_translations")
      .select("id, page_id, language_code, content_type, wiki_pages!inner(slug)")
      .range(from, from + PAGE_SIZE - 1);

    if (error) {
      console.error("❌ 取得エラー:", error.message);
      process.exit(1);
    }

    if (!data || data.length === 0) break;

    for (const row of data) {
      const slugObj = (row as any).wiki_pages;
      const slug: string =
        typeof slugObj === "object" && slugObj !== null
          ? slugObj.slug
          : String(slugObj);
      allRows.push({ ...row, slug });
    }

    if (data.length < PAGE_SIZE) break;
    from += PAGE_SIZE;
  }

  console.log(`✅ 取得完了: ${allRows.length} 件\n`);

  // 分類ごとの集計
  const counts: Record<string, number> = {};
  const updates: Array<{ id: number | bigint; content_type: ContentType; slug: string }> = [];

  for (const row of allRows) {
    const ct = classify(row.slug);
    updates.push({ id: row.id, content_type: ct, slug: row.slug });
    counts[ct] = (counts[ct] ?? 0) + 1;
  }

  console.log("📊 分類結果プレビュー:");
  for (const [ct, count] of Object.entries(counts).sort((a, b) => b[1] - a[1])) {
    console.log(`  ${ct.padEnd(26)} : ${count} 件`);
  }
  console.log();

  // 50件ずつバッチUPDATE
  const batches = chunk(updates, 50);
  console.log(`⬆️  ${batches.length} バッチ × 最大50件 でUPDATE開始...\n`);

  let successCount = 0;
  let errorCount = 0;

  for (let i = 0; i < batches.length; i++) {
    const batch = batches[i];

    // Promise.all で並列更新（同一バッチ内）
    const results = await Promise.all(
      batch.map((row) =>
        supabase
          .from("wiki_translations")
          .update({ content_type: row.content_type })
          .eq("id", row.id)
      )
    );

    for (const { error } of results) {
      if (error) {
        console.error(`  ❌ UPDATE エラー: ${error.message}`);
        errorCount++;
      } else {
        successCount++;
      }
    }

    if ((i + 1) % 5 === 0 || i === batches.length - 1) {
      console.log(`  ... ${Math.min((i + 1) * 50, allRows.length)} / ${allRows.length} 完了`);
    }

    if (i < batches.length - 1) {
      await sleep(1000); // 502対策: バッチ間に1秒スリープ
    }
  }

  console.log("\n✅ UPDATE 完了");
  console.log(`  成功: ${successCount} 件`);
  console.log(`  エラー: ${errorCount} 件`);
}

main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
