#!/usr/bin/env python3
"""
BJJ Wiki - 検索強化（Fuse.js）+ Beehiiv メールリスト埋め込み
Usage: python3 patch_search_beehiiv.py --beehiiv-id YOUR_EMBED_ID
Run from ~/Claude/bjj-wiki/

Beehiiv embed IDの取得方法:
  Beehiivダッシュボード → Grow → Subscribe Forms → Embed → コード内のpublication_idをコピー
"""
import os, re, argparse, glob

BASE = os.path.expanduser("~/Claude/bjj-wiki")

# ===== Fuse.js 強化検索スクリプト =====
FUSE_SCRIPT = """
<!-- Fuse.js fuzzy search -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/fuse.js/7.0.0/fuse.min.js"></script>
<script>
(function(){
  const searchInput = document.getElementById('tech-search');
  const catSections = document.querySelectorAll('.cat-section');
  const pills = document.querySelectorAll('.filter-pill');
  let activeFilter = 'all';

  // 全カードのデータを収集
  const allCards = [];
  catSections.forEach(sec => {
    const cat = sec.dataset.cat || 'all';
    sec.querySelectorAll('.tech-card').forEach(card => {
      const nameEl = card.querySelector('.tech-name');
      if (nameEl) allCards.push({ name: nameEl.textContent, cat, el: card, sec });
    });
  });

  // Fuse.jsインスタンス（ファジー検索）
  const fuse = new Fuse(allCards, {
    keys: ['name'],
    threshold: 0.4,  // 0=完全一致, 1=なんでもマッチ
    minMatchCharLength: 2,
  });

  function applyFilter() {
    const q = searchInput ? searchInput.value.trim() : '';
    let matched = new Set();

    if (q.length >= 2) {
      const results = fuse.search(q);
      results.forEach(r => matched.add(r.item.el));
    }

    let anyVisible = false;
    catSections.forEach(sec => {
      const cat = sec.dataset.cat || 'all';
      const cards = sec.querySelectorAll('.tech-card');
      let secVisible = false;
      cards.forEach(card => {
        const nameEl = card.querySelector('.tech-name');
        const name = nameEl ? nameEl.textContent.toLowerCase() : '';
        const filterOk = activeFilter === 'all' || cat === activeFilter;
        const searchOk = q.length < 2
          ? true
          : (matched.has(card) || name.includes(q.toLowerCase()));
        const show = filterOk && searchOk;
        card.style.display = show ? '' : 'none';
        if (show) secVisible = true;
      });
      sec.style.display = secVisible ? '' : 'none';
      if (secVisible) anyVisible = true;
    });

    let nr = document.querySelector('.no-results');
    if (!nr) {
      nr = document.createElement('p');
      nr.className = 'no-results';
      nr.textContent = 'No techniques found.';
      document.querySelector('.container').appendChild(nr);
    }
    nr.style.display = anyVisible ? 'none' : '';
  }

  pills.forEach(p => {
    p.addEventListener('click', () => {
      pills.forEach(x => x.classList.remove('active'));
      p.classList.add('active');
      activeFilter = p.dataset.filter;
      applyFilter();
    });
  });

  if (searchInput) searchInput.addEventListener('input', applyFilter);
  applyFilter();
})();
</script>
"""

# ===== Beehiiv メール登録セクション =====
def make_beehiiv_html(pub_id, lang="en"):
    labels = {
        "en": ("Get Weekly BJJ Tips", "Join the BJJ Wiki newsletter. Technique breakdowns, training tips, and exclusive content — free.", "Subscribe Free →"),
        "ja": ("週次BJJヒントを受け取る", "BJJ Wikiニュースレターに参加。技の解説、トレーニングTips、限定コンテンツ — 無料。", "無料で登録 →"),
        "pt": ("Receba Dicas Semanais de BJJ", "Junte-se ao newsletter do BJJ Wiki. Análises de técnicas, dicas de treino e conteúdo exclusivo — grátis.", "Assinar Grátis →"),
    }
    title, desc, btn = labels.get(lang, labels["en"])

    if pub_id == "PLACEHOLDER":
        # Beehiiv未設定の場合はシンプルなフォームのみ
        return f"""
  <div class="beehiiv-wrap">
    <div class="beehiiv-inner">
      <h3 class="beehiiv-title">🐝 {title}</h3>
      <p class="beehiiv-desc">{desc}</p>
      <p style="color:var(--muted);font-size:0.8rem;margin-top:8px">Coming soon — check back shortly!</p>
    </div>
  </div>"""

    return f"""
  <div class="beehiiv-wrap">
    <div class="beehiiv-inner">
      <h3 class="beehiiv-title">🐝 {title}</h3>
      <p class="beehiiv-desc">{desc}</p>
      <iframe src="https://embeds.beehiiv.com/embed/{pub_id}"
        data-test-id="beehiiv-embed"
        width="100%" height="52"
        frameborder="0" scrolling="no"
        style="border-radius:8px;margin-top:14px;border:0;background:transparent">
      </iframe>
    </div>
  </div>"""

BEEHIIV_CSS = """
  /* Beehiiv newsletter */
  .beehiiv-wrap{background:linear-gradient(135deg,#0d1225,#1a1040);
    border:1px solid #2d2060;border-radius:14px;padding:28px;
    margin:32px 0 8px;text-align:center}
  .beehiiv-title{font-size:1.05rem;font-weight:800;margin-bottom:10px}
  .beehiiv-desc{color:var(--muted);font-size:0.88rem;line-height:1.6}"""

def patch_index(path, pub_id, lang):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    changed = False

    # 1. Fuse.js: 既存の素朴な検索スクリプトを置換
    old_script_pattern = re.compile(
        r'<script>\s*const pills[\s\S]*?applyFilter\(\);\s*</script>', re.MULTILINE
    )
    if old_script_pattern.search(html) and "fuse.min.js" not in html:
        html = old_script_pattern.sub(FUSE_SCRIPT, html)
        changed = True

    # 2. Beehiiv: footerの直前に挿入
    if "beehiiv-wrap" not in html:
        if BEEHIIV_CSS.strip() not in html:
            html = html.replace("</style>", BEEHIIV_CSS + "\n</style>", 1)
        beehiiv_html = make_beehiiv_html(pub_id, lang)
        html = html.replace("<footer>", beehiiv_html + "\n<footer>", 1)
        changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
    return changed

def patch_article(path, pub_id, lang):
    """記事ページのaff-boxの後にBeehiivを追加"""
    with open(path, encoding="utf-8") as f:
        html = f.read()

    if "beehiiv-wrap" in html:
        return False

    if BEEHIIV_CSS.strip() not in html:
        html = html.replace("</style>", BEEHIIV_CSS + "\n</style>", 1)

    beehiiv_html = make_beehiiv_html(pub_id, lang)
    # aff-boxの後 or footerの前
    if '</div>\n  </div>\n</body>' in html:
        html = html.replace('</div>\n  </div>\n</body>',
                            beehiiv_html + '\n</div>\n  </div>\n</body>', 1)
    else:
        html = html.replace("<footer>", beehiiv_html + "\n<footer>", 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--beehiiv-id", default="PLACEHOLDER",
                        help="Beehiiv embed ID (publication_idの値)")
    parser.add_argument("--index-only", action="store_true",
                        help="インデックスページのみ処理")
    args = parser.parse_args()

    pub_id = args.beehiiv_id
    langs  = ["en", "ja", "pt"]
    idx_count = art_count = 0

    for lang in langs:
        # インデックスページ
        idx = os.path.join(BASE, lang, "index.html")
        if os.path.exists(idx) and patch_index(idx, pub_id, lang):
            print(f"[OK] {lang}/index.html (Fuse.js + Beehiiv)")
            idx_count += 1

        if args.index_only:
            continue

        # 記事ページ
        for path in sorted(glob.glob(os.path.join(BASE, lang, "*.html"))):
            if path.endswith("index.html"):
                continue
            slug = os.path.basename(path).replace(".html", "")
            if patch_article(path, pub_id, lang):
                print(f"[OK] {lang}/{slug}.html (Beehiiv)")
                art_count += 1

    total = idx_count + art_count
    print(f"\n[完了] {total}件を更新（インデックス {idx_count}件 + 記事 {art_count}件）")
    if pub_id == "PLACEHOLDER":
        print("⚠️  Beehiiv IDが未設定です。取得後に:")
        print("   python3 scripts/patch_search_beehiiv.py --beehiiv-id YOUR_ID")
        print("   を再実行してください（既存のPLACEHOLDERは自動置換されます）")

if __name__ == "__main__":
    main()
