#!/usr/bin/env python3
"""
BJJ Wiki - Formspree お問い合わせフォーム埋め込み
Usage: python3 patch_formspree.py --form-id YOUR_FORM_ID
Run from ~/Claude/bjj-wiki/

フォームIDの取得方法:
  1. https://formspree.io/register でアカウント作成
  2. Dashboard → + New Form → 名前入力（例: BJJ Wiki Contact）
  3. 表示されたID（例: xeqbplgn）をコピー
  4. python3 scripts/patch_formspree.py --form-id xeqbplgn
"""
import os, re, argparse, glob

BASE = os.path.expanduser("~/Claude/bjj-wiki")

FORM_BLOCK = """
<!-- Formspree Contact Form -->
<section class="contact-section" style="max-width:680px;margin:48px auto 0;padding:32px 24px;background:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;">
  <h3 style="margin:0 0 8px;font-size:1.1rem;color:#1e293b;">📬 お問い合わせ / Contact</h3>
  <p style="margin:0 0 20px;font-size:0.85rem;color:#64748b;">記事の誤り・追加情報・コラボ提案など、お気軽にどうぞ。</p>
  <form action="https://formspree.io/f/{FORM_ID}" method="POST" style="display:flex;flex-direction:column;gap:12px;">
    <input type="text" name="name" placeholder="お名前 / Name" required
      style="padding:10px 14px;border:1px solid #cbd5e1;border-radius:8px;font-size:0.9rem;outline:none;">
    <input type="email" name="email" placeholder="メールアドレス / Email" required
      style="padding:10px 14px;border:1px solid #cbd5e1;border-radius:8px;font-size:0.9rem;outline:none;">
    <textarea name="message" rows="4" placeholder="メッセージ / Message" required
      style="padding:10px 14px;border:1px solid #cbd5e1;border-radius:8px;font-size:0.9rem;resize:vertical;outline:none;"></textarea>
    <button type="submit"
      style="padding:10px 24px;background:#1e293b;color:#fff;border:none;border-radius:8px;font-size:0.9rem;cursor:pointer;align-self:flex-start;transition:background 0.2s;"
      onmouseover="this.style.background='#334155'" onmouseout="this.style.background='#1e293b'">
      送信 / Send
    </button>
  </form>
</section>
<!-- /Formspree -->
"""

ALREADY_MARKER = "formspree.io/f/"

def patch_file(path, form_id):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    if ALREADY_MARKER in html:
        return "skip"

    block = FORM_BLOCK.replace("{FORM_ID}", form_id)

    # </body>の直前に挿入
    if "</body>" in html:
        html = html.replace("</body>", block + "\n</body>", 1)
    else:
        html += block

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return "ok"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--form-id", required=True, help="FormspreeのフォームID（例: xeqbplgn）")
    parser.add_argument("--index-only", action="store_true", help="インデックスのみ処理")
    args = parser.parse_args()

    ok = skip = 0
    patterns = []

    if args.index_only:
        patterns = [
            os.path.join(BASE, "en", "index.html"),
            os.path.join(BASE, "ja", "index.html"),
            os.path.join(BASE, "pt", "index.html"),
        ]
    else:
        for lang in ["en", "ja", "pt"]:
            patterns += glob.glob(os.path.join(BASE, lang, "*.html"))

    for path in sorted(patterns):
        rel = os.path.relpath(path, BASE)
        result = patch_file(path, args.form_id)
        if result == "ok":
            print(f"[OK] {rel}")
            ok += 1
        else:
            skip += 1

    print(f"\n[完了] {ok}件を更新（スキップ {skip}件）")

if __name__ == "__main__":
    main()
